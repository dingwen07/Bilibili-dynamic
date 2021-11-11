from pync import Notifier


def send_notification(title, msg, action_link):
    Notifier.notify(
        message=msg,
        title=title,
        open=action_link
    )
