
!pip install gradio pandas matplotlib twilio scikit-learn

import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from twilio.rest import Client
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("🔐 Enter Twilio Details")
TWILIO_SID = input("SID: ").strip()
TWILIO_TOKEN = input("TOKEN: ").strip()
TWILIO_NUMBER = input("PHONE (+1...): ").strip()
client = Client(TWILIO_SID, TWILIO_TOKEN)


df = pd.read_csv("/content/drive/MyDrive/major/postpartum_900_balanced.csv")

le_mood = LabelEncoder()
le_bleeding = LabelEncoder()
le_ppd = LabelEncoder()
le_result = LabelEncoder()

df['Mood'] = le_mood.fit_transform(df['Mood'])
df['Bleeding'] = le_bleeding.fit_transform(df['Bleeding'])
df['PPD_Symptom'] = le_ppd.fit_transform(df['PPD_Symptom'])
df['Result'] = le_result.fit_transform(df['Result'])

X = df[['Age','Blood_Pressure','Temperature','Mood','Bleeding','Pain_Level','PPD_Symptom']]
y = df['Result']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=500, max_depth=10, random_state=42)
model.fit(X_train, y_train)

print("✅ Accuracy:", accuracy_score(y_test, model.predict(X_test)))

conn = sqlite3.connect("patients.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Age INTEGER,
    Blood_Pressure REAL,
    Temperature REAL,
    Mood TEXT,
    Bleeding TEXT,
    Pain_Level INTEGER,
    PPD_Symptom TEXT,
    Husband TEXT,
    Mother TEXT,
    Result TEXT,
    SMS_Status TEXT,
    Call_Status TEXT
)
""")
conn.commit()

def format_number(num):
    num = str(num).strip()
    if not num.startswith("+"):
        num = "+91" + num
    return num

def send_sms(alert, h, m):
    status = ""
    try:
        client.messages.create(body=alert, from_=TWILIO_NUMBER, to=h)
        status += "SMS Husband ✅ "
    except:
        status += "SMS Husband ❌ "

    try:
        client.messages.create(body=alert, from_=TWILIO_NUMBER, to=m)
        status += "SMS Mother ✅ "
    except:
        status += "SMS Mother ❌ "
    return status

def make_call(alert, h, m):
    status = ""
    twiml = f"<Response><Say>{alert}</Say></Response>"
    try:
        client.calls.create(twiml=twiml, to=h, from_=TWILIO_NUMBER)
        status += "Call Husband ✅ "
    except:
        status += "Call Husband ❌ "

    try:
        client.calls.create(twiml=twiml, to=m, from_=TWILIO_NUMBER)
        status += "Call Mother ✅ "
    except:
        status += "Call Mother ❌ "
    return status

def df_to_html(df):
    html = "<table border=1 style='width:100%;border-collapse:collapse;'>"
    html += "<tr>" + "".join([f"<th>{c}</th>" for c in df.columns]) + "</tr>"
    for _, row in df.iterrows():
        color = "#ffcccc" if "RISK" in row["Result"] else "#ccffcc"
        html += "<tr>" + "".join([f"<td style='background:{color}'>{i}</td>" for i in row]) + "</tr>"
    html += "</table>"
    return html


def find_nearby_hospital():
    return "https://www.google.com/maps/search/hospitals+near+me"

def check_health(name, age, bp, temp, mood, bleeding, pain, ppd, husband, mother):

    mood_e = le_mood.transform([mood])[0]
    bleed_e = le_bleeding.transform([bleeding])[0]
    ppd_e = le_ppd.transform([ppd])[0]

    pred = model.predict([[age, bp, temp, mood_e, bleed_e, pain, ppd_e]])
    label = le_result.inverse_transform(pred)[0]

    husband = format_number(husband)
    mother = format_number(mother)

    # Decision Logic
    if label == "RISK":
        result = f"🚨 {name} is at RISK (ML)"
        alert = f"ALERT: {name} is at RISK. Immediate attention needed."

    elif bp > 150 or temp > 39 or pain > 8:
        result = f"🚨 {name} is at CRITICAL RISK (Rule Override)"
        alert = f"CRITICAL ALERT: {name} needs urgent care!"

    else:
        result = f"✅ {name} is SAFE"
        alert = None

   
    if alert:
        sms = send_sms(alert, husband, mother)
        call = make_call(alert, husband, mother)
    else:
        sms = "No SMS"
        call = "No Call"

    hospital_link = ""
    if "RISK" in result:
        hospital_link = f"[🚑 Find Nearby Hospitals]({find_nearby_hospital()})"

    cursor.execute("""
    INSERT INTO patients (Name, Age, Blood_Pressure, Temperature, Mood, Bleeding, Pain_Level, PPD_Symptom, Husband, Mother, Result, SMS_Status, Call_Status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, bp, temp, mood, bleeding, pain, ppd, husband, mother, result, sms, call))
    conn.commit()

    df_recent = pd.read_sql_query("SELECT * FROM patients ORDER BY id DESC LIMIT 10", conn)
    df_all = pd.read_sql_query("SELECT * FROM patients", conn)

    csv_path = "patients_report.csv"
    df_all.to_csv(csv_path, index=False)

    safe = df_all['Result'].str.contains("SAFE").sum()
    risk = df_all['Result'].str.contains("RISK").sum()

    chart = "chart.png"
    plt.bar(["SAFE","RISK"], [safe, risk])
    plt.title("Health Status")
    plt.savefig(chart)
    plt.close()

    return result, df_to_html(df_recent), chart, csv_path, hospital_link


app = gr.Interface(
    fn=check_health,
    inputs=[
        gr.Textbox(label="Name"),
        gr.Number(label="Age"),
        gr.Number(label="Blood Pressure"),
        gr.Number(label="Temperature"),
        gr.Dropdown(["Happy","Sad","Angry","Tired","Depressed","Irritable"]),
        gr.Dropdown(["None","Mild","Moderate","Heavy"]),
        gr.Slider(0,10),
        gr.Dropdown(["Mild","Moderate","Severe"]),
        gr.Textbox(label="Husband Number"),
        gr.Textbox(label="Mother Number")
    ],
    outputs=[
        gr.Textbox(label="Result"),
        gr.HTML(label="Recent Records"),
        gr.Image(label="Chart"),
        gr.File(label="Download CSV"),
        gr.Markdown(label="🏥 Emergency Help")
    ],
    title="Postpartum Health Monitoring System (ML + Alerts + Hospital Finder)"
)

app.launch(share=True)
