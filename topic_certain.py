import json
import sqlite3
import time
import os
from urllib import parse

import requests

with open('dynamic_types.json', 'r') as load_file:
    dynamic_types = json.load(load_file)


class TopicDynamic(object):
    def __init__(self, topic_name, database_file='dynamic_topic_data.db'):
        super().__init__()
        self.topic_name = topic_name
        self.topic_url_parsed = parse.quote(topic_name)
        self.topic_dynamic_url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history?topic_name={}' \
                                 '&offset_dynamic_id={}'.format(self.topic_url_parsed, '{}')
        self.session = requests.Session()
        if not os.path.exists(database_file):
            TopicDynamic.init_db(database_file)
        self.db = sqlite3.connect(database_file)
        self.db_cursor = self.db.cursor()
        topic_data = self.db_cursor.execute(
            '''SELECT "topic_name", "data" FROM "main"."topic_info" WHERE "topic_name" = ?; ''',
            (self.topic_name,)).fetchall()
        if len(topic_data) == 0:
            url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_name={}'.format(
                self.topic_url_parsed)
            while True:
                # noinspection PyBroadException
                try:
                    topic_info_response = self.session.get(url)
                    break
                except Exception:
                    time.sleep(1)
            topic_info = json.loads(topic_info_response.content.decode())
            if topic_info['code'] != 0:
                if topic_info['code'] == -404:
                    raise ValueError
                elif topic_info['code'] == -400:
                    raise ValueError
                else:
                    raise ValueError
            self.db_cursor.execute('''INSERT INTO "main"."topic_info" ("topic_name", "data") VALUES (?, ?);''',
                                   (self.topic_name, json.dumps(topic_info['data'])))
            self._save_data()
            self.get_update()
            self.db_cursor.execute(
                '''SELECT "topic_name", "data" FROM "main"."topic_info" WHERE "topic_name" = ?; ''',
                (self.topic_name,)).fetchall()

    def get_update(self, bound=1628179200, offset=0):
        url = self.topic_dynamic_url.format(str(offset))
        while True:
            # noinspection PyBroadException
            try:
                dynamic_response = self.session.get(url)
                break
            except Exception:
                print(Exception)
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
                # TODO: Just shortened this line, need testing
                self.db_cursor.execute(
                    '''INSERT INTO 
                    "main"."dynamics" ("id", "uid", "topic_name", "time", "status", "description", "data")
                    VALUES (?, ?, ?, ?, ?, ?, ?);''',
                    (dynamic_id, dynamic_uploader_uid, self.topic_name, dynamic_post_time_formatted, 0, dynamic_description,
                     json.dumps(dynamic)))
                new_dynamics.append(dynamic.copy())
        if len(new_dynamics) > 0:
            self._save_data()
        if dynamic_history['data']['has_more'] == 1:
            error_time = 0
            while True:
                # noinspection PyBroadException
                try:
                    dynamic_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={}'
                    dynamic_url = dynamic_url.format(dynamic_history['data']['offset'])
                    dynamic_response = self.session.get(dynamic_url)
                    dynamic = json.loads(dynamic_response.content.decode())
                    if dynamic['data']['card']['desc']['timestamp'] > bound:
                        time.sleep(10)
                        new_dynamics += self.get_update(bound, offset=dynamic_history['data']['offset'])
                    break
                except Exception:
                    error_time += 1
                    if error_time > 4:
                        return new_dynamics
                    time.sleep(2)
        return new_dynamics

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
