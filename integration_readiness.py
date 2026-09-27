"""Server configuration inventory; never exposes secret values to the UI."""
from urllib.parse import urlparse


def brevo_readiness(settings):
    """Supabase owns Auth email; local secrets alone cannot prove delivery."""
    sender = str(settings.get('BREVO_SENDER_EMAIL', '')).strip()
    checks = {
        'sending_domain': bool(sender and '@' in sender and '.' in sender.rsplit('@', 1)[-1]),
        'supabase_custom_smtp_confirmed': str(settings.get('BREVO_SUPABASE_SMTP_CONFIRMED', '')).lower() == 'true',
        'test_confirmation_delivered': str(settings.get('BREVO_TEST_CONFIRMATION_DELIVERED', '')).lower() == 'true',
    }
    return checks


def paypal_readiness(settings):
    """Fail closed until an independent webhook ledger has been verified."""
    callback = urlparse(str(settings.get('PAYPAL_WEBHOOK_URL', '')))
    checks = {
        'client_credentials': bool(settings.get('PAYPAL_CLIENT_ID') and settings.get('PAYPAL_CLIENT_SECRET')),
        'webhook_identity': bool(settings.get('PAYPAL_WEBHOOK_ID') and callback.scheme == 'https' and callback.hostname),
        'plan': str(settings.get('PAYPAL_PLAN_ID', '')).startswith('P-'),
        'verified_ledger': str(settings.get('PAYPAL_LEDGER_VERIFIED', '')).lower() == 'true',
        'sandbox_scenarios': str(settings.get('PAYPAL_SANDBOX_SCENARIOS_PASSED', '')).lower() == 'true',
    }
    return checks


def checkout_enabled(settings):
    # Configuration claims cannot by themselves prove a deployed receiver;
    # this function is an audit signal, never a purchase or entitlement gate.
    return False
