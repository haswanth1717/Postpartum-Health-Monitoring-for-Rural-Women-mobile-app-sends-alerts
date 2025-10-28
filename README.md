This project aims to develop a mobile-based postpartum health monitoring system designed specifically for rural women. The system helps in tracking the physical and emotional health of new mothers after childbirth and automatically sends alerts to healthcare workers, family members, or ASHA workers when abnormal conditions are detected.

The solution combines wearable health sensors and a mobile application to collect vital health data such as:

Blood pressure

Heart rate

Body temperature

Mood/emotional status

Sleep patterns

Postpartum depression indicators

The data collected from the wearable or manual input through the app is analyzed using AI-based health rules to determine if the woman is in a safe, moderate, or risk health condition.

In case of any abnormalities — such as high blood pressure, signs of postpartum depression, excessive bleeding, or fever — the system automatically:

Sends an SMS and call alert via Twilio API to the ASHA worker or family members.

Displays an emergency alert message on the app dashboard.

Stores the health record securely in a local database (SQLite) for tracking progress over time.

This system helps in early detection of postpartum complications, enabling timely medical intervention and reducing maternal mortality, especially in rural and remote areas with limited healthcare access.

Key Features:

📱 User-friendly mobile interface (Gradio/Android)

❤️ Real-time health monitoring (manual or wearable data)

📊 Data storage using SQLite database

🔔 Automated SMS/Call alerts using Twilio API

🌐 Works in internet is available
