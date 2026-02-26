from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

from .config import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_USE_TLS

def send_otp_email(background_tasks: BackgroundTasks, to_email: str, otp_code: str):
    """Додава задача за испраќање е-пошта во позадина."""
    background_tasks.add_task(_send_email_sync, to_email, otp_code)

def _send_email_sync(to_email: str, otp_code: str):
    """Синхрона функција која навистина го испраќа мејлот."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Вашиот код за двојна автентикација"

        body = f"""
        <html>
        <body>
            <h2>Код за верификација</h2>
            <p>Вашиот код за пристап е: <strong>{otp_code}</strong></p>
            <p>Кодот важи 5 минути.</p>
            <p>Доколку не сте го побарале овој код, игнорирајте ја пораката.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        if EMAIL_USERNAME and EMAIL_PASSWORD:
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        server.send_message(msg)
        server.quit()
        print(f"Email успешно испратен до {to_email}")  # за дебагирање
    except Exception as e:
        print(f"Грешка при испраќање е-пошта: {e}")

def generate_otp(length=6) -> str:
    return ''.join(random.choices(string.digits, k=length))