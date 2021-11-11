import json
import random
import time
from dynamic_parser import DynamicParser
from topic_dynamic import TopicDynamic
from notifier import Notifier
import platform

with open('dynamic_types.json', 'r') as load_file:
    dynamic_types = json.load(load_file)
# noinspection PyBroadException
try:
    with open('diagnosis.json', 'r') as load_file:
        diagnosis = json.load(load_file)
except Exception:
    diagnosis = {'diagnosis': []}
    with open('diagnosis.json', 'w') as dump_file:
        json.dump(diagnosis, dump_file)

topicwh_list = []
topic_list = []

while True:
    topic_name = input('话题名称: ')
    while True:
        new_mode = input('是否为活动话题(y/n): ')
        if new_mode.upper() == 'Y' or new_mode.upper() == 'YES':
            legacy_mode = False
            break
        elif new_mode.upper() == 'N' or new_mode.upper() == 'NO':
            legacy_mode = True
            break
        else:
            print('输入错误，请重新输入')

    if legacy_mode:
        topicwh_list.append(TopicDynamic(topic_name=topic_name, legacy_mode=legacy_mode))
        topic_list.append(topic_name)
    else:
        result = TopicDynamic.get_topic_id_list(topic_name)
        counter = 0
        if len(result) == 0:
            print('没有找到符合条件的话题，请重新输入!')
            selection = '-1'
        else:
            print('根据你提供的关键词，找到以下话题: ')
            for item in result:
                print('{}:'.format(counter))
                print('话题名称: {}'.format(item['name']))
                print('话题id: {}'.format(item['id']))
                if 'description' in item:
                    print('话题描述: {}'.format(item['description']))
                print()
                counter += 1

            while True:
                selection = input('请选择你需要监视的话题(0~{}, -1为重新输入): '.format(len(result) - 1))
                if selection.isdigit() and int(selection) in range(len(result)):
                    print('你选择了\'{}\''.format(result[int(selection)]['name']))
                    print('对应的话题ID是: {}'.format(result[int(selection)]['id']))
                    break
                elif selection == '-1':
                    break
                else:
                    print('输入有误，请重新输入!')

        if selection == '-1':
            continue

        topic_name = result[int(selection)]['name']
        topic_list.append(topic_name)
        topic_id = result[int(selection)]['id']
        topicwh_list.append(TopicDynamic(topic_id=topic_id, topic_name=topic_name, legacy_mode=legacy_mode))

    print('当前你已经添加的话题: \n{}'.format(topic_list))

    while True:
        add_another = input('是否继续添加话题?(y/n): ')
        if add_another == 'y' or \
                add_another == 'Y' or \
                add_another == 'yes' or \
                add_another == 'Yes' or \
                add_another == 'YES':
            print('-------------------------------------------')
            break
        elif add_another == 'n' or \
                add_another == 'N' or \
                add_another == 'no' or \
                add_another == 'No' or \
                add_another == 'NO':
            break
        else:
            print('输入有误，请重新输入!')

    if add_another == 'n' or \
            add_another == 'N' or \
            add_another == 'no' or \
            add_another == 'No' or \
            add_another == 'NO':
        break

notification_method = ['stdout']

if platform.system() == 'Windows' or platform.system() == 'Darwin':
    while True:
        toast_mode = input('是否启用toast提醒(y/n): ')
        if toast_mode.upper() == 'Y' or toast_mode.upper() == 'YES':
            notification_method.append('toast')
            break
        elif toast_mode.upper() == 'N' or toast_mode.upper() == 'NO':
            break
        else:
            print('输入错误，请重新输入！')

    if platform.system() == 'Darwin':
        while True:
            tts_mode = input('是否开启语音提醒功能？(y/n)')
            if tts_mode.upper() == 'Y' or tts_mode.upper() == 'YES':
                notification_method.append('tts_macOS')
                break
            elif tts_mode.upper() == 'N' or tts_mode.upper() == 'NO':
                break
            else:
                print('输入错误，请重新输入！')
notification = Notifier(notification_method)

print()

notification.notify(
    {
        'start': True,
        'type': 1,
        'no_toast': True
    }
)

for item in topicwh_list:
    notification.notify(
        {
            'monitor': True,
            'topic_id': item.topic_id,
            'topic_name': item.topic,
            'type': 1,
            'legacy_mode': item.legacy_mode
        }
    )
print()

while True:
    for topicwh in topicwh_list:
        try:
            new_dynamics = topicwh.get_update()
            if len(new_dynamics) > 0:
                for dynamic in new_dynamics:
                    dynamic_dict = DynamicParser.dictionary_parser(dynamic, legacy_mode=topicwh.legacy_mode)
                    dynamic_dict['topic_name'] = topicwh.topic
                    dynamic_dict['topic_id'] = topicwh.topic_id
                    dynamic_dict['type'] = 1
                    notification.notify(dynamic_dict)
        except Exception as e:
            print(e)
        finally:
            time.sleep(10)

    time.sleep(random.randint(1, 10))
