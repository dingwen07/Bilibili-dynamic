import os
import platform
from urllib import parse

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
            elif n == 'tts_macOS':
                self.notify_tts_macos(data)

    @staticmethod
    def notify_stdout(data={'type': 0}):
        update_type = data['type']
        if update_type == 0:
            if 'start' in data:
                title = 'Bilibili UP主更新提醒'
                print(title)
            if 'monitor' in data:
                message = '开始监视UP主<{}>的更新...'
                if 'uploader_name' in data:
                    message = message.format(data['uploader_name'])
                print(message)
            if 'uploader_name' in data:
                print('您关注的UP主<{}>'.format(data['uploader_name']), end='')
            if 'type_name' in data:
                print('发布了新的{}'.format(data['type_name']))
            else:
                print()
            if 'dynamic_id' in data:
                print('动态链接: \n\thttps://t.bilibili.com/{}'.format(str(data['dynamic_id'])))
            if 'content' in data:
                print('动态内容: \n\t{}'.format(data['content']))
            if 'title' in data:
                print('稿件标题: \n\t{}'.format(data['title']))
            print()
        elif update_type == 1:
            if 'start' in data:
                title = 'Bilibili 话题更新提醒'
                print(title)
            if 'monitor' in data:
                message = '开始监视话题<{}>的更新...'
                if 'topic_name' in data:
                    message = message.format(data['topic_name'])
                print(message)
            elif 'topic_name' in data:
                print('您关注的话题<{}>'.format(data['topic_name']), end='')
            if 'type_name' in data:
                print('发布了新的{}'.format(data['type_name']))
            if 'uploader_name' in data:
                print('发布人:{}\t'.format(data['uploader_name']), end='')
            if 'uploader_uid' in data:
                print('UID:{}'.format(data['uploader_uid']))
            if 'dynamic_id' in data:
                print('动态链接: \n\thttps://t.bilibili.com/{}'.format(str(data['dynamic_id'])))
            if 'content' in data:
                print('动态内容: \n\t{}'.format(data['content']))
            if 'type_contains_title' in data:
                if data['type_contains_title']:
                    if 'title' in data:
                        print('稿件标题: \n\t{}'.format(data['title']))
            print()
            pass
        else:
            raise ValueError('Unknown update type')

    @staticmethod
    def notify_toast(data={'type': 0}):
        system_type = platform.system()
        update_type = data['type']
        action_link = ''
        if update_type == 0:
            if 'monitor' in data:
                title = 'Bilibili UP主更新提醒'
                message = '开始监视UP主<{}>的更新...'
                if 'uploader_name' in data:
                    message = message.format(data['uploader_name'])
                    if 'uploader_uid' in data:
                        action_link = 'https://space.bilibili.com/{}'.format(str(data['uploader_uid']))
                else:
                    action_link = 'https://space.bilibili.com/'
            else:
                title = '您关注的UP主<{}>发布了新的{}'
                message = 'Null'
                if 'dynamic_id' in data:
                    dynamic_id = data['dynamic_id']
                else:
                    dynamic_id = ''
                action_link = 'https://t.bilibili.com/{}'.format(str(dynamic_id))
                if 'uploader_name' in data:
                    title = title.format(data['uploader_name'])
                if 'type_name' in data:
                    title = title.format(data['type_name'])
                if 'content' in data:
                    message = data['content']
                if 'type_contains_title' in data:
                    if data['type_contains_title']:
                        if 'title' in data:
                            message = data['title']
        elif update_type == 1:
            if 'monitor' in data:
                title = 'Bilibili 话题更新提醒'
                message = '开始监视话题<{}>的更新...'
                if 'topic_name' in data:
                    message = message.format(data['topic_name'])
                    if 'legacy_mode' in data:
                        if data['legacy_mode']:
                            action_link = 'https://t.bilibili.com/topic/name/{}/feed'.format(
                                parse.quote(data['topic_name']))
                        else:
                            action_link = 'https://www.bilibili.com/v/topic/detail?topic_id={}&topic_name={}' \
                                .format(data['topic_id'], parse.quote(data['topic_name']))
                    else:
                        action_link = 'https://t.bilibili.com/'
                else:
                    action_link = 'https://t.bilibili.com/'
            else:
                title = '您关注的话题<{}>有新的{}'
                message = 'Null'
                if 'dynamic_id' in data:
                    dynamic_id = data['dynamic_id']
                else:
                    dynamic_id = ''
                action_link = 'https://t.bilibili.com/{}'.format(str(dynamic_id))
                if 'topic_name' in data:
                    title = title.format(data['topic_name'], '{}')
                if 'type_name' in data:
                    title = title.format(data['type_name'])
                if 'content' in data:
                    message = data['content']
                if 'type_contains_title' in data:
                    if data['type_contains_title']:
                        if 'title' in data:
                            message = data['title']
            pass
        else:
            raise ValueError('Unknown update type')

        if system_type == 'Windows':
            from toast_win import send_notification
            send_notification(
                app_id=APP_ID,
                title=title,
                msg=message,
                icon=BILIBILI_ICON_URL,
                action_label='View',
                action_link=action_link
            )
        elif system_type == 'Darwin':
            from toast_macOS import send_notification
            if 'start' in data:
                send_notification(
                    title=title,
                    msg=message,
                    action_link=action_link
                )
            else:
                send_notification(
                    title=title,
                    msg=message,
                    action_link=action_link
                )
            pass
        else:
            print('OS {} is not currently supported for toast notification'.format(system_type))

    @staticmethod
    def notify_tts_macos(data={'type': 0}):
        system_type = platform.system()
        update_type = data['type']
        if system_type == 'Darwin':
            if update_type == 0:
                if 'start' in data:
                    title = 'Bilibili UP主更新提醒'
                    os.system('say {}'.format(title))
                    message = '开始监视UP主<{}>的更新...'
                    if 'uploader_name' in data:
                        message = message.format(data['uploader_name'])
                    os.system('say \'{}\''.format(message))
                else:
                    title = '您关注的UP主有新的{}'
                    message = 'Null'
                    if 'type_name' in data:
                        title = title.format(data['type_name'])
                    if 'content' in data:
                        message = data['content']
                    if 'title' in data:
                        message = data['title']
                    os.system('say \'{}\''.format(title))
                    os.system('say \'{}\''.format(message))
            elif update_type == 1:
                if 'start' in data:
                    title = 'Bilibili 话题更新提醒'
                    os.system('say \'{}\''.format(title))
                elif 'monitor' in data:
                    message = '开始监视话题<{}>的更新...'
                    if 'topic_name' in data:
                        message = message.format(data['topic_name'])
                    os.system('say \'{}\''.format(message))
                else:
                    title = '您关注的话题有新的{}'
                    message = 'Null'
                    if 'type_name' in data:
                        title = title.format(data['type_name'])
                    if 'content' in data:
                        message = '动态内容: ' + data['content']
                    if 'type_contains_title' in data:
                        if data['type_contains_title']:
                            if 'title' in data:
                                message = '稿件标题: ' + data['title']
                    os.system('say \'{}\''.format(title))
                    os.system('say \'{}\''.format(message))
            else:
                raise ValueError('Unknown update type')
        else:
            print('OS {} is not currently supported for tts notification'.format(system_type))
