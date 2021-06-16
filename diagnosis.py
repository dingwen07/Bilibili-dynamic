import json

try:
    with open('diagnosis.json', 'r') as load_file:
        diagnosis = json.load(load_file)
        dynamic_list = diagnosis['diagnosis']
except Exception as e:
    print(e)
    diagnosis = {'diagnosis': []}
    with open('diagnosis.json', 'w') as dump_file:
        json.dump(diagnosis, dump_file)
    dynamic_list = diagnosis['diagnosis']

input('共 {} 条动态'.format(str(len(dynamic_list))))

while len(diagnosis['diagnosis']) > 0:
    dynamic = dynamic_list.pop(0)
    uploader_info = 'Uploader: [UID: {uid}] {uname}'
    dynamic_id = 'Dynamic ID: {dynamic_id}'
    dynamic_type = 'Dynamic Type: {type}'
    # noinspection PyBroadException
    try:
        uploader_info = uploader_info.format(uid=str(dynamic['desc']['uid']), uname='{uname}')
    except Exception as e:
        # noinspection PyBroadException
        try:
            uploader_info = uploader_info.format(uid=str(dynamic['desc']['user_profile']['info']['uid']),
                                                 uname='{uname}')
        except Exception as e:
            uploader_info = uploader_info.format(uid='<Unknown>', uname='{uname}')

    # noinspection PyBroadException
    try:
        uploader_info = uploader_info.format(uname=dynamic['desc']['user_profile']['info']['uname'])
    except Exception as e:
        uploader_info = uploader_info.format(uname='<Unknown>')

    # noinspection PyBroadException
    try:
        dynamic_id = dynamic_id.format(dynamic_id=str(dynamic['desc']['dynamic_id']))
    except Exception as e:
        dynamic_id = dynamic_id.format(dynamic_id='<Unknown>')

    # noinspection PyBroadException
    try:
        dynamic_type = dynamic_type.format(type=str(dynamic['desc']['type']))
    except Exception as e:
        dynamic_type = dynamic_type.format(type='<Unknown>')

    print(dynamic_id)
    print(dynamic_type)
    print(uploader_info)
    print('Dynamic Data: ' + json.dumps(dynamic))
    print()
    input('剩余 {} 条动态...'.format(str(len(dynamic_list))))
