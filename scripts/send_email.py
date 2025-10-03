import os
import base64
import requests
from datetime import datetime

# Vérifie si aujourd'hui est le premier mercredi du mois
today = datetime.today()
first_wednesday = min(
    day for day in range(1, 8)
    if datetime(today.year, today.month, day).weekday() == 2
)

if today.day != first_wednesday:
    print("⏭️ Ce n'est pas le premier mercredi du mois. Aucun email ne sera envoyé.")
    exit(0)

# Lecture de la clé API depuis la variable d'environnement
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not SENDGRID_API_KEY:
    raise EnvironmentError("La variable d'environnement SENDGRID_API_KEY n'est pas définie.")

# Chargement du fichier PDF
pdf_filename = "press_review.pdf"
with open(pdf_filename, "rb") as f:
    pdf_data = f.read()

# Encodage en base64
encoded_pdf = base64.b64encode(pdf_data).decode()

# Corps de l'email
email_data = {
    "personalizations": [
        {
            "to": [
                {"email": "natanael.farret@hertz.com"}
            ],
            "subject": "Business Monthly Press Review"
        }
    ],
    "from": {"email": "natanael.farret@hotmail.com"},
    "content": [
        {
            "type": "text/plain",
            "value": "Hi,\n\nPlease find attached your monthly business press review.\n\nBest regards,\nGitHub Actions"
        }
    ],
    "attachments": [
        {
            "content": encoded_pdf,
            "type": "application/pdf",
            "filename": pdf_filename,
            "disposition": "attachment"
        }
    ]
}

# Envoi via l'API SendGrid
response = requests.post(
    "https://api.sendgrid.com/v3/mail/send",
    headers={
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    },
    json=email_data
)

if response.status_code == 202:
    print("✅ Email sent successfully.")
else:
    print(f"❌ Failed to send email. Status code: {response.status_code}")
    print(response.text)
