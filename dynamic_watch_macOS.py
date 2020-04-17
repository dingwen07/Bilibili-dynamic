import json
import time
import updynamic
import os

uid = int(input('UP主UID: '))

upwh = updynamic.UploaderDynamic(uid)

with open('dynamic_types.json', 'r') as load_file:
    dynamic_types = json.load(load_file)
try:
    with open('diagnosis.json', 'r') as load_file:
        diagnosis = json.load(load_file)
except:
    diagnosis = {'diagnosis': []}
    with open('diagnosis.json', 'w') as dump_file:
        json.dump(diagnosis, dump_file)

uploader_name = upwh.uploader_name
print('开始监视UP主<{}>的更新...'.format(uploader_name))
print()
os.system('osascript -e \'display notification \"开始监视UP主<{}>的更新...\" with title \"Bilibili UP主更新提醒\"\''.format(uploader_name))

while True:
    new_dynamics = upwh.get_update()
    if len(new_dynamics) > 0:
        for dynamic in new_dynamics:
            dynamic_id = dynamic['desc']['dynamic_id']
            dynamic_type = str(dynamic['desc']['type'])
            if dynamic_type in dynamic_types['types']:
                type_data = dynamic_types['types'][dynamic_type]
                type_name = type_data['name']
                type_contains_title = type_data['contains_title']
                type_content_path = type_data['path']
                content = dynamic.copy()
                for k in type_content_path:
                    content = content[k]
                if type_contains_title:
                    type_title_path = type_data['title_path']
                    title = dynamic.copy()
                    for k in type_title_path:
                        title = title[k]

            else:
                type_name = '[未知类型动态]'
                diagnosis['diagnosis'].append(dynamic)
                with open('diagnosis.json', 'w') as dump_file:
                    json.dump(diagnosis, dump_file)
                    print('发现不能被识别的动态类型，请将"diagnosis.json"提交给开发者')
            title = '您关注的UP主<{}>发布了新的{}'.format(uploader_name, type_name)
            print(title)
            if type_contains_title:
                print('稿件标题：{}'.format(title))
            os.system('osascript -e \'display notification "{}" with title "{}"\''.format(content, title))
            print('动态内容: {}'.format(content))
    time.sleep(60)
