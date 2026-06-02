import json

from django.conf import settings


def send_web_push(subscription, payload):
    """Send a Web Push message to a single PushSubscription.

    Args:
        subscription (PushSubscription): The target subscription.
        payload (dict): JSON-serializable notification payload
            (e.g. {"title": ..., "body": ..., "url": ...}).

    Returns:
        bool: True if the push was accepted, False otherwise. If the push
        service reports the subscription is gone (404/410), it is deleted.
    """
    if not settings.VAPID_PRIVATE_KEY:
        return False

    from pywebpush import webpush, WebPushException

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT},
        )
        return True
    except WebPushException as exc:
        status = getattr(exc.response, "status_code", None)
        if status in (404, 410):
            subscription.delete()
        return False
