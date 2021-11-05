import json
import random
import time
from topic_dynamic import TopicDynamic

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
        if new_mode == 'y' or new_mode == 'Y' or new_mode == 'yes' or new_mode == 'Yes' or new_mode == 'YES':
            legacy_mode = False
            break
        elif new_mode == 'n' or new_mode == 'N' or new_mode == 'no' or new_mode == 'No' or new_mode == 'NO':
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
            selection = input('请选择你需要监视的话题(0~{}): '.format(len(result) - 1))
            if selection.isdigit() and int(selection) in range(len(result)):
                print('你选择了\'{}\''.format(result[int(selection)]['name']))
                print('对应的话题ID是: {}'.format(result[int(selection)]['id']))
                break
            else:
                print('输入有误，请重新输入!')

        topic_name = result[int(selection)]['name']
        topic_list.append(topic_name)
        topic_id = result[int(selection)]['id']
        topicwh_list.append(TopicDynamic(topic_id=topic_id, topic_name=topic_name, legacy_mode=legacy_mode))

    print('当前你已经添加的话题: \n{}'.format(topic_list))

    while True:
        add_another = input('是否继续添加话题?(y/n): ')
        if add_another == 'y' or\
                add_another == 'Y' or\
                add_another == 'yes' or\
                add_another == 'Yes' or\
                add_another == 'YES':
            print('-------------------------------------------')
            break
        elif add_another == 'n' or\
                add_another == 'N' or\
                add_another == 'no' or\
                add_another == 'No' or\
                add_another == 'NO':
            break
        else:
            print('输入有误，请重新输入!')

    if add_another == 'n' or\
            add_another == 'N' or\
            add_another == 'no' or\
            add_another == 'No' or\
            add_another == 'NO':
        break

print()
for item in topicwh_list:
    print('开始监视话题<{}>的更新...'.format(item.topic))
print()

while True:
    for topicwh in topicwh_list:
        try:
            new_dynamics = topicwh.get_update()
            if len(new_dynamics) > 0:
                if topicwh.legacy_mode:
                    for dynamic in new_dynamics:
                        dynamic_id = dynamic['desc']['dynamic_id']
                        dynamic_type = str(dynamic['desc']['type'])
                        dynamic_uploader_uid = str(dynamic['desc']['user_profile']['info']['uid'])
                        dynamic_uploader_name = str(dynamic['desc']['user_profile']['info']['uname'])
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
                        print('您关注的话题<{}>有新的{}'.format(topicwh.topic, type_name))
                        print('动态链接: \n\thttps://t.bilibili.com/{}'.format(dynamic_id))
                        print('发布人: {}\tUID:{}'.format(dynamic_uploader_name, dynamic_uploader_uid))
                        print('动态内容: \n\t{}'.format(content))
                        if type_contains_title:
                            print('稿件标题: {}'.format(title))
                        print()
                else:
                    for dynamic in new_dynamics:
                        dynamic_card_item = dynamic['dynamic_card_item']
                        dynamic_id = int(dynamic_card_item['id_str'])
                        dynamic_type = str(dynamic_card_item['type'])
                        dynamic_uploader_uid = dynamic_card_item['modules']['module_author']['mid']
                        dynamic_uploader_name = dynamic_card_item['modules']['module_author']['name']
                        content = "未解析"
                        type_contains_title = False
                        title = ""
                        if dynamic_type in dynamic_types['types']:
                            type_data = dynamic_types['types'][dynamic_type]
                            type_name = type_data['name']
                            type_contains_title = type_data['contains_title']
                            type_content_path = type_data['path']
                            content = dynamic_card_item.copy()
                            for k in type_content_path:
                                content = content[k]
                            if type_contains_title:
                                type_title_path = type_data['title_path']
                                title = dynamic_card_item.copy()
                                for k in type_title_path:
                                    title = title[k]

                        else:
                            type_name = '[未知类型动态]'
                            diagnosis['diagnosis'].append(dynamic)
                            with open('diagnosis.json', 'w') as dump_file:
                                json.dump(diagnosis, dump_file)
                            print('发现不能被识别的动态类型，请将"diagnosis.json"提交给开发者')
                        print('您关注的话题<{}>有新的{}'.format(topicwh.topic, type_name))
                        print('动态链接: \n\thttps://t.bilibili.com/{}'.format(dynamic_id))
                        print('发布人: {}\tUID:{}'.format(dynamic_uploader_name, dynamic_uploader_uid))
                        print('动态内容: \n\t{}'.format(content))
                        if type_contains_title:
                            print('稿件标题: {}'.format(title))
                        print()
        except Exception as e:
            print(e)
        finally:
            time.sleep(30)

    time.sleep(random.randint(1, 10))

