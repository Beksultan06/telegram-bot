from firebase_admin import messaging
from firebase_admin.messaging import AndroidConfig, AndroidNotification, APNSConfig, APNSPayload, Aps


def send_push_notification(notification, topic=None):
    title = notification.title if notification.title else "Новое уведомление"
    body = notification.message if notification.message else "Новость"
    try:
        if topic:
            tokens = [
                token for token in
                notification.users.values_list('fcm_token', flat=True)
                if token is not None
            ]
            messaging.subscribe_to_topic(
                tokens,
                topic=topic,
            )
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                topic=topic
            )
            messaging.send(message)
            return True

        users_count = notification.users.count()
        if not users_count:
            return False
        for fcm_token in notification.users.values_list('fcm_token', flat=True):
            sound = 'default'
            android = AndroidConfig(notification=AndroidNotification(sound=sound))
            ios = APNSConfig(payload=APNSPayload(aps=Aps(sound=sound)))
            if not fcm_token:
                continue
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                # android=android,
                apns=ios,
                token=fcm_token
            )
            messaging.send(message)
        return True
    except Exception as _:
        return False


def send_message_notification(title, body, fcm_token):
    sound = 'default'
    android = AndroidConfig(notification=AndroidNotification(sound=sound))
    ios = APNSConfig(payload=APNSPayload(aps=Aps(sound=sound)))
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,

        ),
        # android=android,
        apns=ios,
        token=fcm_token,
    )
    messaging.send(message)
