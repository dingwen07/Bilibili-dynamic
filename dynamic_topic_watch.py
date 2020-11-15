import json
import time
import topic_dynamic_json

topic = input('话题名称: ')

topicwh = topic_dynamic_json.TopicDynamic(topic)

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
print('开始监视话题<{}>的更新...'.format(topic_name))
print()

while True:
    try:
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
                print('您关注的话题<{}>有新的{}'.format(topic_name, type_name))
                print('动态链接: \n\thttps://t.bilibili.com/{}'.format(dynamic_id))
                print('动态内容: \n\t{}'.format(content))
                if type_contains_title:
                    print('稿件标题: {}'.format(title))
                print()
    except Exception as e:
        print(e)
    finally:
        time.sleep(30)

