import json
import time
import topic_dynamic_json
import os

topic = input('话题名称：')

try:
    topicwh = topic_dynamic_json.TopicDynamic(topic)
except ValueError:
    print('该话题不存在，请检查后再试！')
    exit(1)


while True:
    tts_mode = input('是否开启语音提醒功能？(Y/N)')
    if tts_mode.upper() == 'Y' or tts_mode.upper() == 'YES':
        use_tts = True
        break
    elif tts_mode.upper() == 'N' or tts_mode.upper() == 'NO':
        use_tts = False
        break
    else:
        print('输入错误，请重新输入！')

with open('dynamic_types.json', 'r') as load_file:
    dynamic_types = json.load(load_file)
try:
    with open('diagnosis.json', 'r') as load_file:
        diagnosis = json.load(load_file)
except:
    diagnosis = {'diagnosis': []}
    with open('diagnosis.json', 'w') as dump_file:
        json.dump(diagnosis, dump_file)

topic_name = topicwh.topic
if use_tts:
    os.system('osascript -e \'display notification \"开始监视话题<{}>的更新...\" with title \"Bilibili 话题更新提醒\"\''.format(
        topic_name))
    os.system('osascript -e \'say "Bilibili 话题更新提醒"\'')
    os.system('osascript -e \'say "开始监视话题{}的更新"\''.format(topic_name))
else:
    os.system('osascript -e \'display notification \"开始监视话题<{}>的更新...\" with title \"Bilibili 话题更新提醒\" sound name \"Purr\"\''.format(
        topic_name))
print('开始监视话题<{}>的更新...'.format(topic_name))
print()

while True:
    new_dynamics = topicwh.get_update()
    if len(new_dynamics) > 0:
        for dynamic in new_dynamics:
            dynamic_id = dynamic['desc']['dynamic_id']
            dynamic_type = str(dynamic['desc']['type'])
            content = "未解析"
            type_contains_title = False
            title = ""
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
            title = '您关注的话题<{}>有新的{}'.format(topic_name, type_name)
            print(title)
            print('动态链接: \n\thttps://t.bilibili.com/{}'.format(dynamic_id))
            print('动态内容: \n\t{}'.format(content))
            if type_contains_title:
                print('稿件标题：\n\t{}'.format(title))
            print()
            if use_tts:
                os.system('osascript -e \'display notification "{}" with title "{}"\''.format(content, title))
                os.system('osascript -e \'say "您关注的话题有新的{}"\''.format(type_name))
                os.system('osascript -e \'say "动态内容：{}"\''.format(content))
            else:
                os.system('osascript -e \'display notification "{}" with title "{}"\' sound name \"Purr\"'.format(content, title))

    time.sleep(30)
