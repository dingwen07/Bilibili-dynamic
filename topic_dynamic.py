import json
import sqlite3
import time
import os
from urllib import parse

import requests

with open('dynamic_types.json', 'r') as load_file:
    dynamic_types = json.load(load_file)


class TopicDynamic(object):
    def __init__(self, topic_name, database_file='topic_dynamic_data.db'):
        super().__init__()
        self.topic = topic_name
        self.topic_url_parsed = parse.quote(topic_name)
        self.topic_dynamic_url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history?topic_name={}&offset_dynamic_id={}'.format(self.topic_url_parsed, '{}')
        self.session = requests.Session()
        if not os.path.exists(database_file):
            TopicDynamic.init_db(database_file)
        self.db = sqlite3.connect(database_file)
        self.db_cursor = self.db.cursor()
        topic_data = self.db_cursor.execute('''SELECT "topic_name", "data" FROM "main"."topic_info" WHERE "topic_name" = ?; ''', (self.topic,)).fetchall()
        if len(topic_data) == 0:
            url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_name={}'.format(self.topic_url_parsed)
            while True:
                try:
                    topic_info_response = self.session.get(url)
                    break
                except:
                    time.sleep(1)
            topic_info = json.loads(topic_info_response.content.decode())
            if topic_info['code'] != 0:
                if topic_info['code'] == -404:
                    raise ValueError
                elif topic_info['code'] == -400:
                    raise ValueError
                else:
                    raise ValueError
            self.db_cursor.execute('''INSERT INTO "main"."topic_info" ("topic_name", "data") VALUES (?, ?);''', (self.topic, json.dumps(topic_info['data'])))
            self._save_data()
            self.get_update()
            topic_data = self.db_cursor.execute('''SELECT "topic_name", "data" FROM "main"."topic_info" WHERE "topic_name" = ?; ''', (self.topic,)).fetchall()

    def get_update(self):
        dynamic_offset = 0
        url = self.topic_dynamic_url.format(str(dynamic_offset))
        while True:
            try:
                dynamic_response = self.session.get(url)
                break
            except:
                time.sleep(1)
        dynamic_history = json.loads(dynamic_response.content.decode())
        new_dynamics = []
        for dynamic in dynamic_history['data']['cards']:
            dynamic_id = dynamic['desc']['dynamic_id']
            select = self.db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''',
                                            (dynamic_id,)).fetchall()
            if len(select) == 0:
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                dynamic_uploader_uid = dynamic['desc']['uid']
                dynamic_post_time = time.localtime(dynamic['desc']['timestamp'])
                dynamic_post_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", dynamic_post_time)
                dynamic_description = "未解析"
                dynamic_type = str(dynamic['desc']['type'])
                if dynamic_type in dynamic_types['types']:
                    type_data = dynamic_types['types'][dynamic_type]
                    type_content_path = type_data['path']
                    dynamic_description = dynamic.copy()
                    for k in type_content_path:
                        dynamic_description = dynamic_description[k]
                self.db_cursor.execute('''INSERT INTO "main"."dynamics" ("id", "uid", "topic_name", "time", "status", "description", "data") VALUES (?, ?, ?, ?, ?, ?, ?);''', (dynamic_id, dynamic_uploader_uid, self.topic, dynamic_post_time_formatted, 0, dynamic_description, json.dumps(dynamic)))
                new_dynamics.append(dynamic.copy())
        if len(new_dynamics) > 0:
            self._save_data()
        return new_dynamics

    def refresh_dynamic_status(self, topic_name='', refresh_line=100, delay=30, refresh_rate=30, offset=0):
        counter = 0
        dynamic_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={}'
        lines_later_process = 0
        if refresh_line == 0:
            refresh_line = self.db_cursor.execute('''SELECT COUNT(*) FROM "main"."dynamics" WHERE "topic_name" = ?;''', (topic_name,)).fetchall()[0][0]
        if refresh_line > refresh_rate:
            lines_later_process = refresh_line - refresh_rate
        dynamics = self.db_cursor.execute('''SELECT "id", "status" 
                                             FROM "main"."dynamics" 
                                             WHERE "topic_name" = ? 
                                             AND "status" = 0
                                             ORDER BY "id" DESC 
                                             LIMIT ? OFFSET ?;''', (topic_name, refresh_rate, offset)).fetchall()
        offset = offset + refresh_rate
        for dynamics_record in dynamics:
            if dynamics_record[1] == 0:
                while True:
                    try:
                        result = self.session.get(dynamic_url.format(dynamics_record[0]))
                        response = json.loads(result.content.decode())
                        data_response = response['data']
                        if 'card' in data_response:
                            break
                        elif result.status_code == 200:
                            self.db_cursor.execute('''UPDATE "main"."dynamics" SET "status"=? WHERE "id"=?;''',(1, str(dynamics_record[0])))
                            counter = counter + 1
                            break
                        else:
                            exit(1)
                    except:
                        try:
                            # Exception Process When User Encounter 412 Error
                            if result.status_code == 412:
                                raise ConnectionError
                        except ConnectionError:
                            raise ConnectionRefusedError
                        except Exception as e:
                            print(e)
                            continue
                        time.sleep(10)
            else:
                continue
        self._save_data()
        if lines_later_process > 0:
            time.sleep(delay)
            counter += self.refresh_dynamic_status(topic_name, lines_later_process, delay, refresh_rate, offset)
        return counter

    def close(self):
        self.db.close()

    def _save_data(self):
        self.db.commit()

    @staticmethod
    def init_db(database_file='topic_dynamic_data.db'):
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        db_cursor.execute('''CREATE TABLE "topic_info" (
                                "topic_name"    TEXT,
                                "data"          TEXT,
                                PRIMARY KEY("topic_name")
                                );''')
        db_cursor.execute('''CREATE TABLE "dynamics" (
                                "id"    INTEGER NOT NULL,
                                "uid"   INTEGER NOT NULL,
                                "topic_name" TEXT,
                                "time"  TEXT,
                                "status"    INTEGER NOT NULL,
                                "description"   TEXT,
                                "data"  TEXT,
                                PRIMARY KEY("id"),
                                FOREIGN KEY("topic_name") REFERENCES "topic_info"("topic_name")
                                );''')
        db.commit()
        db.close()

    @staticmethod
    def get_dynamic(dynamic_id, database_file='topic_dynamic_data.db'):
        """
        docstring
        """
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        select = db_cursor.execute('''SELECT "id", "status" FROM "main"."dynamics" WHERE "id" = ?;''', (dynamic_id,)).fetchall()[0]
        db.close()
        return select

    @staticmethod
    def migrate(topic_name, database_file='topic_dynamic_data.db'):
        topic_data_file = 'topic_data/{}.json'.format(topic_name)
        with open(topic_data_file, 'r') as load_file:
            migrate_data = json.load(load_file)
        session = requests.Session()
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_name={}'.format(topic_name)
        topic_data = db_cursor.execute('''SELECT "topic_name", "data" FROM "main"."topic_info" WHERE "topic_name" = ?;''', (topic_name,)).fetchall()
        if len(topic_data) == 0:
            while True:
                try:
                    topic_info_response = session.get(url)
                    break
                except:
                    time.sleep(1)
            topic_info = json.loads(topic_info_response.content.decode())
            if topic_info['code'] != 0:
                if topic_info['code'] == -404:
                    raise ValueError
                elif topic_info['code'] == -400:
                    raise ValueError
                else:
                    raise ValueError
            db_cursor.execute('''INSERT INTO "main"."topic_info" ("topic_name", "data") VALUES (?, ?);''',
                              (topic_name, json.dumps(topic_info['data'])))
        for dynamic_id, dynamic in migrate_data['dynamics'].items():
            dynamic_uploader_uid = dynamic['desc']['uid']
            dynamic_post_time = time.localtime(dynamic['desc']['timestamp'])
            dynamic_post_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", dynamic_post_time)
            if 'item' in dynamic['card']:
                if 'description' in dynamic['card']['item']:
                    dynamic_description = dynamic['card']['item']['description']
                elif 'content' in dynamic['card']['item']:
                    dynamic_description = dynamic['card']['item']['content']
                else:
                    raise KeyError
            elif 'dynamic' in dynamic['card']:
                dynamic_description = dynamic['card']['dynamic']
            else:
                raise KeyError
            select = db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''',
                                       (dynamic_id,)).fetchall()
            if len(select) == 0:
                db_cursor.execute('''INSERT INTO "main"."dynamics" ("id", "uid", "topic_name", "time", "status", "description", "data") VALUES (?, ?, ?, ?, ?, ?, ?);''', (dynamic_id, dynamic_uploader_uid, topic_name, dynamic_post_time_formatted, 0, dynamic_description, json.dumps(dynamic)))
        db.commit()
        db.close()
