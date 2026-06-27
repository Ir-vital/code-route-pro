"""
Service d'envoi d'emails.
Supporte SMTP générique (Gmail, Mailgun, etc.) et Resend via HTTP.
Sélection automatique selon les settings disponibles.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Interface abstraite ──────────────────────────────────────────────────────

class EmailService:
    """Service d'envoi d'emails avec templates HTML."""

    async def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """
        Envoie un email. Retourne True si succès, False sinon.
        Ne lève jamais d'exception — les erreurs email ne doivent pas bloquer le flux.
        """
        try:
            return await self._send(to, subject, html_body, text_body)
        except Exception as e:
            logger.error("Email send failed", extra={"to": to, "subject": subject, "error": str(e)})
            return False

    async def _send(self, to: str, subject: str, html_body: str, text_body: str | None) -> bool:
        raise NotImplementedError


# ─── Implémentation SMTP ──────────────────────────────────────────────────────

class SmtpEmailService(EmailService):

    async def _send(self, to: str, subject: str, html_body: str, text_body: str | None) -> bool:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_ADDRESS}>"
        msg["To"] = to

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_ADDRESS, to, msg.as_string())

        logger.info("Email sent via SMTP", extra={"to": to, "subject": subject})
        return True


# ─── Implémentation Resend (HTTP API) ─────────────────────────────────────────

class ResendEmailService(EmailService):
    """
    Utilise l'API Resend (https://resend.com) — plus fiable que SMTP direct.
    Nécessite RESEND_API_KEY dans les settings.
    """

    async def _send(self, to: str, subject: str, html_body: str, text_body: str | None) -> bool:
        import httpx

        api_key = getattr(settings, "RESEND_API_KEY", None)
        if not api_key:
            raise ValueError("RESEND_API_KEY not configured")

        payload = {
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_ADDRESS}>",
            "to": [to],
            "subject": subject,
            "html": html_body,
        }
        if text_body:
            payload["text"] = text_body

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=10,
            )
            response.raise_for_status()

        logger.info("Email sent via Resend", extra={"to": to, "subject": subject})
        return True


# ─── Implémentation No-op (développement) ────────────────────────────────────

class ConsoleEmailService(EmailService):
    """
    En développement : affiche l'email dans les logs au lieu de l'envoyer.
    Activé quand SMTP_USER est vide.
    """

    async def _send(self, to: str, subject: str, html_body: str, text_body: str | None) -> bool:
        logger.info(
            "📧 [DEV] Email non envoyé — affiché en console",
            extra={"to": to, "subject": subject},
        )
        print(f"\n{'='*60}")
        print(f"TO: {to}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{text_body or html_body}")
        print(f"{'='*60}\n")
        return True


# ─── Factory ─────────────────────────────────────────────────────────────────

def get_email_service() -> EmailService:
    """Retourne le service d'email adapté à la configuration."""
    resend_key = getattr(settings, "RESEND_API_KEY", None)
    if resend_key:
        return ResendEmailService()
    if settings.SMTP_USER:
        return SmtpEmailService()
    return ConsoleEmailService()


# ─── Templates ────────────────────────────────────────────────────────────────

def render_password_reset_email(reset_url: str, first_name: str) -> tuple[str, str]:
    """Retourne (html, text) pour l'email de réinitialisation de mot de passe."""
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Réinitialisation de mot de passe</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <h1 style="color: #3b82f6;">CodeRoute Pro</h1>
  <p>Bonjour {first_name},</p>
  <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
  <p>Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe :</p>
  <p style="text-align: center; margin: 30px 0;">
    <a href="{reset_url}"
       style="background-color: #3b82f6; color: white; padding: 12px 24px;
              text-decoration: none; border-radius: 6px; font-weight: bold;">
      Réinitialiser mon mot de passe
    </a>
  </p>
  <p style="color: #6b7280; font-size: 0.875rem;">
    Ce lien expire dans {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} heures.<br>
    Si vous n'avez pas fait cette demande, ignorez cet email.
  </p>
  <hr style="border: none; border-top: 1px solid #e5e7eb;">
  <p style="color: #9ca3af; font-size: 0.75rem;">
    CodeRoute Pro — Plateforme d'apprentissage du code de la route
  </p>
</body>
</html>
"""
    text = (
        f"Bonjour {first_name},\n\n"
        f"Réinitialisez votre mot de passe en cliquant sur ce lien :\n{reset_url}\n\n"
        f"Ce lien expire dans {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} heures.\n"
        "Si vous n'avez pas fait cette demande, ignorez cet email."
    )
    return html, text


def render_welcome_email(first_name: str) -> tuple[str, str]:
    """Retourne (html, text) pour l'email de bienvenue après inscription."""
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Bienvenue sur CodeRoute Pro</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <h1 style="color: #3b82f6;">Bienvenue sur CodeRoute Pro ! 🚦</h1>
  <p>Bonjour {first_name},</p>
  <p>Votre compte a bien été créé. Vous pouvez dès maintenant vous connecter
     et commencer à préparer votre code de la route.</p>
  <p>Bonne préparation !</p>
  <p>— L'équipe CodeRoute Pro</p>
</body>
</html>
"""
    text = (
        f"Bonjour {first_name},\n\n"
        "Bienvenue sur CodeRoute Pro ! Votre compte a été créé avec succès.\n"
        "Connectez-vous sur la plateforme pour commencer à préparer votre code de la route."
    )
    return html, text
