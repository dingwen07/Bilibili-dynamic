import json
import time
import updynamic
from dynamic_parser import DynamicParser
from notifier import Notifier

uid = int(input('UP主UID: '))
upwh = updynamic.UploaderDynamic(uid)
uploader_name = upwh.uploader_name

notify_methods = ['stdout']

available_notify_methods_d = Notifier.get_available_notify_methods_d()
user_selection_notify_methods_d = {}
print('选择你需要的通知方式:')
i = 0
for key, value in available_notify_methods_d.items():
    if key == 'stdout':
        continue
    user_selection_notify_methods_d[str(i)] = key
    print('\t{}: {}'.format(i, value))
    i += 1
user_selection_input = input('请输入你的选择 (多个选择用空格隔开): ')
for item in user_selection_input.split(' '):
    if item in user_selection_notify_methods_d:
        notify_methods.append(user_selection_notify_methods_d[item])

notifier = Notifier(notify_methods)

notifier.notify(
    {
        'type': 0,
        'start': True,
        'monitor': None,
        'uploader_name': uploader_name
    }
)

while True:
    try:
        new_dynamics = upwh.get_update()
        if len(new_dynamics) > 0:
            for dynamic in new_dynamics:
                dynamic_dict = DynamicParser.dictionary_parser(dynamic, legacy_mode=True)
                dynamic_dict['type'] = 0
                notifier.notify(dynamic_dict)              
    except Exception as e:
        print(e)
    finally:
        time.sleep(30)
