from __future__ import annotations

import logging

import resend

from app.config import settings

logger = logging.getLogger(__name__)


def build_password_reset_link(reset_token: str) -> str:
    return "{0}?token={1}".format(settings.password_reset_url, reset_token)


def send_password_reset_email(*, to_email: str, reset_token: str) -> None:
    reset_link = build_password_reset_link(reset_token)

    if not settings.resend_configured:
        logger.warning(
            "Resend not configured — password reset link for %s: %s",
            to_email,
            reset_link,
        )
        return

    resend.api_key = settings.resend_api_key
    resend.Emails.send(
        {
            "from": "HERITIA <{0}>".format(settings.resend_from_email),
            "to": [to_email],
            "subject": "Réinitialisation de votre mot de passe HERITIA",
            "html": (
                "<p>Bonjour,</p>"
                "<p>Vous avez demandé la réinitialisation de votre mot de passe HERITIA.</p>"
                '<p><a href="{0}">Cliquez ici pour choisir un nouveau mot de passe</a>.</p>'
                "<p>Ce lien expire dans 1 heure. Si vous n'êtes pas à l'origine de cette demande, "
                "ignorez cet email.</p>"
                "<p>— L'équipe HERITIA</p>"
            ).format(reset_link),
            "text": (
                "Réinitialisez votre mot de passe HERITIA : {0}\n"
                "Ce lien expire dans 1 heure."
            ).format(reset_link),
        }
    )
