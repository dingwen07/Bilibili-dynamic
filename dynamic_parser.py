import json


class DynamicParser:
    @staticmethod
    def plaintext_parser(dynamic) -> str:
        return str(dynamic)

    @staticmethod
    def markdown_parser(dynamic) -> str:
        return str(dynamic)

    @staticmethod
    def html_parser(dynamic) -> str:
        processed_dynamic = DynamicParser.dictionary_parser(dynamic)
        if processed_dynamic['code'] != 0:
            return '<strong>{}</strong>'.format(processed_dynamic['msg'])
        else:
            processed_dynamic = processed_dynamic['data']
            output = '<strong>UP主名称: </strong><code>{}</code>\n'.format(processed_dynamic['dynamic_uploader_name'])
            output += '<strong>UID: </strong><code>{}</code>\n'.format(processed_dynamic['dynamic_uploader_uid'])
            output += '<strong>动态内容: </strong>\n'
            output += '<pre>{}</pre>\n'.format(processed_dynamic['content'])
            if processed_dynamic['type_contains_title']:
                output += '<strong>稿件标题: </strong>\n'
                output += '<pre>{}</pre>'.format(processed_dynamic['title'])
            output = output + '<strong>动态地址: </strong>\n'
            link = 'https://t.bilibili.com/{}'.format(processed_dynamic['dynamic_id'])
            output += '<a href=\"{}\">{}</a>'.format(link, link)
            return output

    @staticmethod
    def dictionary_parser(dynamic):
        with open('dynamic_types.json', 'r') as load_file:
            dynamic_types = json.load(load_file)

        try:
            with open('diagnosis.json', 'r') as load_file:
                diagnosis = json.load(load_file)
        except Exception:
            diagnosis = {'diagnosis': []}
            with open('diagnosis.json', 'w') as dump_file:
                json.dump(diagnosis, dump_file)

        dynamic_id = dynamic['desc']['dynamic_id']
        dynamic_type = str(dynamic['desc']['type'])
        dynamic_uploader_uid = str(dynamic['desc']['user_profile']['info']['uid'])
        dynamic_uploader_name = str(dynamic['desc']['user_profile']['info']['uname'])
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
            return {'code': 0, 'msg': '', 'data': {'dynamic_id': dynamic_id, 'type_name': type_name,
                                                   'dynamic_uploader_uid': dynamic_uploader_uid,
                                                   'dynamic_uploader_name': dynamic_uploader_name,
                                                   'content': content, 'type_contains_title': type_contains_title,
                                                   'title': title}}
        else:
            diagnosis['diagnosis'].append(dynamic)
            with open('diagnosis.json', 'w') as dump_file:
                json.dump(diagnosis, dump_file)
            return {'code': -1, 'msg': '发现不能被识别的动态类型，请联系开发者', 'data': {}}
