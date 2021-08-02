import re
from winotify import Notification


from constants import URL_REGEX
from updynamic import UploaderDynamic


def send_notification(app_id, title, msg, icon, action_label, action_link):
    urls = re.findall(URL_REGEX, icon)
    if len(urls) == 1:
        icon = UploaderDynamic.download_resources({'': urls[0]}, './resource_cache/0')[0]
    toast = Notification(app_id=app_id,
                         title=title,
                         msg=msg,
                         icon=icon)
    toast.add_actions(label=action_label,
                      link=action_link)

    toast.build().show()
