import platform

from constants import APP_ID, BILIBILI_ICON_URL


class Notifier(object):

    def __init__(self, notify_types=['stdout']):
        self.notify_types = notify_types

    def notify(self, data={'type': 0}):
        for n in self.notify_types:
            if n == 'stdout':
                self.notify_stdout(data)
            elif n == 'toast':
                self.notify_toast(data)

    @staticmethod
    def notify_stdout(data={'type': 0}):
        update_type = data['type']
        if update_type == 0:
            if 'uploader_name' in data:
                print('您关注的UP主<{}>'.format(data['uploader_name']), end='')
            if 'type_name' in data:
                print('发布了新的{}'.format(data['type_name']))
            else:
                print()
            if 'dynamic_id' in data:
                print('动态ID: {}'.format(data['dynamic_id']))
                print('动态链接: \n\thttps://t.bilibili.com/{}'.format(str(data['dynamic_id'])))
            if 'content' in data:
                print('动态内容: {}'.format(data['content']))
        elif update_type == 1:
            # TODO: topic dynamic notify for stdout
            pass
        else:
            raise ValueError('Unknown update type')

    @staticmethod
    def notify_toast(data={'type': 0}):
        system_type = platform.system()
        update_type = data['type']
        if update_type == 0:
            if 'start' in data:
                title = 'Bilibili UP主更新提醒'
                message = '开始监视UP主<{}>的更新...'
                if 'uploader_name' in data:
                    message = message.format(data['uploader_name'])
            else:
                title = '您关注的UP主<{}>发布了新的{}'
                message = 'Null'
                if 'uploader_name' in data:
                    title = title.format(data['uploader_name'])
                if 'type_name' in data:
                    title = title.format(data['type_name'])
                if 'content' in data:
                    message = data['content']
                if 'title' in data:
                    message = data['title']
        elif update_type == 1:
            # TODO: topic dynamic notify for toast notification
            pass
        else:
            raise ValueError('Unknown update type')

        if system_type == 'Windows':
            from toast_win import send_notification
            if 'dynamic_id' in data:
                dynamic_id = data['dynamic_id']
            else:
                dynamic_id = ''
            send_notification(app_id=APP_ID, title=title,
                              msg=message,
                              icon=BILIBILI_ICON_URL,
                              action_label='View',
                              action_link='https://t.bilibili.com/{}'.format(str(dynamic_id)))
        elif system_type == 'Darwin':
            # TODO: macOS toast notification
            pass
        else:
            print('OS {} is not currently supported for toast notification'.format(system_type))
