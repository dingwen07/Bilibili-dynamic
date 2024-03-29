import json
import os


class DynamicParser:
    @staticmethod
    def plaintext_parser(dynamic) -> str:
        processed_dynamic = DynamicParser.dictionary_parser(dynamic)
        if processed_dynamic['code'] != 0:
            return processed_dynamic['msg']
        else:
            processed_dynamic = processed_dynamic['data']
            output = '动态地址:\n\thttps://t.bilibili.com/{}\n'.format(processed_dynamic['dynamic_id'])
            output += 'UP主名称: {}\t'.format(processed_dynamic['dynamic_uploader_name'])
            output += 'UID: {}\n'.format(processed_dynamic['dynamic_uploader_uid'])
            output += '动态内容: \n\t{}\n'.format(processed_dynamic['content'])
            if processed_dynamic['type_contains_title']:
                output += '稿件标题: \n\t{}'.format(processed_dynamic['title'])
            return output

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
            output = '<strong>动态地址: </strong>\n'
            link = 'https://t.bilibili.com/{}\n'.format(processed_dynamic['dynamic_id'])
            output += '<a href=\"{}\">{}</a>'.format(link, link)
            output += '<strong>UP主名称: </strong><code>{}</code>\n'.format(processed_dynamic['dynamic_uploader_name'])
            output += '<strong>UID: </strong><code>{}</code>\n'.format(processed_dynamic['dynamic_uploader_uid'])
            output += '<strong>动态内容: </strong>\n'
            output += '{}\n'.format(processed_dynamic['content'])
            if processed_dynamic['type_contains_title']:
                output += '<strong>稿件标题: </strong>\n'
                output += '<pre>{}</pre>\n'.format(processed_dynamic['title'])
            return output

    @staticmethod
    def dictionary_parser(dynamic, legacy_mode=True) -> dict:
        filename = 'dynamic_types.json'
        if not os.path.exists(filename):
            filename = 'Bilibili-dynamic/dynamic_types.json'
        with open(filename, 'r') as load_file:
            dynamic_types = json.load(load_file)

        try:
            with open('diagnosis.json', 'r') as load_file:
                diagnosis = json.load(load_file)
        except Exception:
            diagnosis = {'diagnosis': []}
            with open('diagnosis.json', 'w') as dump_file:
                json.dump(diagnosis, dump_file)
        if legacy_mode:
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
                return {
                    'dynamic_id': dynamic_id,
                    'type_name': type_name,
                    'uploader_uid': dynamic_uploader_uid,
                    'uploader_name': dynamic_uploader_name,
                    'content': content,
                    'type_contains_title': type_contains_title,
                    'title': title
                }
            else:
                diagnosis['diagnosis'].append(dynamic)
                with open('diagnosis.json', 'w') as dump_file:
                    json.dump(diagnosis, dump_file)
                return {'msg': '发现不能被识别的动态类型，请联系开发者'}
        else:
            dynamic_card_item = dynamic['dynamic_card_item']
            dynamic_id = int(dynamic_card_item['id_str'])
            dynamic_type = str(dynamic_card_item['type'])
            dynamic_uploader_uid = dynamic_card_item['modules']['module_author']['mid']
            dynamic_uploader_name = dynamic_card_item['modules']['module_author']['name']
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
                return {
                    'dynamic_id': dynamic_id,
                    'type_name': type_name,
                    'uploader_uid': dynamic_uploader_uid,
                    'uploader_name': dynamic_uploader_name,
                    'content': content,
                    'type_contains_title': type_contains_title,
                    'title': title
                }
            else:
                return {'msg': '发现不能被识别的动态类型，请联系开发者'}

