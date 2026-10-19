import smtplib
from email.message import EmailMessage

from arqueo_pipeline.config import entorno


def enviar(destinatario: str, asunto: str, cuerpo: str) -> None:
	mensaje = EmailMessage()
	mensaje["From"] = entorno("SMTP_FROM")
	mensaje["To"] = destinatario
	mensaje["Subject"] = asunto
	mensaje.set_content(cuerpo)

	with smtplib.SMTP(entorno("SMTP_HOST"), int(entorno("SMTP_PORT", "587"))) as smtp:
		smtp.starttls()
		smtp.login(entorno("SMTP_USER"), entorno("SMTP_PASSWORD"))
		smtp.send_message(mensaje)
