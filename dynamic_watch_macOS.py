import json
import time
import updynamic
import os

uid = int(input('UP主UID: '))

try:
    upwh = updynamic.UploaderDynamic(uid)
except ValueError:
    print('该UP主不存在，请检查后再试！')
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
# noinspection PyBroadException
try:
    with open('diagnosis.json', 'r') as load_file:
        diagnosis = json.load(load_file)
except Exception:
    diagnosis = {'diagnosis': []}
    with open('diagnosis.json', 'w') as dump_file:
        json.dump(diagnosis, dump_file)

uploader_name = upwh.uploader_name
if use_tts:
    os.system('osascript -e \'display notification \"开始监视UP主<{}>的更新...\" with title \"Bilibili UP主更新提醒\"\''.format(
        uploader_name))
    os.system('osascript -e \'say "Bilibili UP主更新提醒"\'')
    os.system('osascript -e \'say "开始监视UP主的更新"\'')
else:
    # TODO: fix line too long, need testing after shortening the line length, I don’t have macOS
    os.system('osascript -e \'display notification \"开始监视UP主<{}>的更新...\" with title \"Bilibili UP主更新提醒\" sound name \"Purr\"\''.format(
        uploader_name))
print('开始监视UP主<{}>的更新...'.format(uploader_name))
print()

while True:
    try:
        new_dynamics = upwh.get_update()
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
                title_announce = '您关注的UP主<{}>发布了新的{}'.format(uploader_name, type_name)
                print(title_announce)
                print('动态ID: {}'.format(dynamic_id))
                print('动态内容: {}'.format(content))
                if type_contains_title:
                    print('稿件标题：{}'.format(title))
                if use_tts:
                    os.system('osascript -e \'display notification "{}" with title "{}"\''.format(content, title_announce))
                    os.system('osascript -e \'say "您关注的UP主发布了新的{}"\''.format(type_name))
                    os.system('osascript -e \'say "动态内容：{}"\''.format(content))
                else:
                    os.system('osascript -e \'display notification "{}" with title "{}"\' sound name \"Purr\"'.format(content, title_announce))
    except Exception as e:
        print(e)
    finally:
        time.sleep(30)
