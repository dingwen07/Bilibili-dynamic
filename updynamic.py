import json
import sqlite3
import time
import os
import re
import requests

from urllib.parse import urlparse

try:
    from .constants import URL_REGEX
    from .constants import RESOURCE_TYPES
except ImportError:
    from constants import URL_REGEX
    from constants import RESOURCE_TYPES


class UploaderDynamic(object):
    def __init__(self, uploader_uid, cache_resource=True, fetch=True, database_file='dynamic_data.db',
                 resource_base_path='./resource_cache'):
        super().__init__()
        self.uploader_uid = uploader_uid
        self.cache_resource = cache_resource
        self.resource_path = resource_base_path + '/' + str(self.uploader_uid)
        self.dynamic_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}' \
                           '&offset_dynamic_id={}&need_top=1'.format(str(self.uploader_uid), '{}')
        self.session = requests.Session()
        if not os.path.exists(database_file):
            UploaderDynamic.init_db(database_file)
        self.db = sqlite3.connect(database_file)
        self.db_cursor = self.db.cursor()
        uploader_data = self.db_cursor.execute(
            '''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
        if len(uploader_data) == 0:
            url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(str(self.uploader_uid))
            uploader_info_response = self.session.get(url)
            uploader_info = json.loads(uploader_info_response.content.decode())
            if uploader_info['code'] != 0:
                if uploader_info['code'] == -404:
                    raise ValueError
                elif uploader_info['code'] == -400:
                    raise ValueError
                else:
                    raise ValueError
            uploader_name = uploader_info['data']['name']
            self.db_cursor.execute('''INSERT INTO "main"."uploader_info" ("uid", "name", "data") VALUES (?, ?, ?);''',
                                   (uploader_uid, uploader_name, json.dumps(uploader_info['data'])))
            self._save_data()
            if fetch:
                self.fetch()
        uploader_data = self.db_cursor.execute(
            '''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
        self.uploader_name = uploader_data[0][1]

    def fetch(self):
        counter = 0
        dynamic_offset = 0
        while True:
            url = self.dynamic_url.format(str(dynamic_offset))
            # noinspection PyBroadException
            try:
                dynamic_response = self.session.get(url)
            except Exception:
                time.sleep(1)
                continue
            dynamic_history = json.loads(dynamic_response.content.decode())
            if dynamic_history['code'] != 0:
                time.sleep(1)
                continue
            dynamic_offset = dynamic_history['data']['next_offset']
            if counter == 0:
                if 'cards' not in dynamic_history['data']:
                    self._save_data()
                    return 0
            if 'cards' in dynamic_history['data']:
                for dynamic in dynamic_history['data']['cards']:
                    dynamic_id = dynamic['desc']['dynamic_id']
                    select = self.db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''',
                                                    (dynamic_id,)).fetchall()
                    if len(select) == 0:
                        dynamic['card'] = json.loads(dynamic['card'])
                        dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                        self.db_cursor.execute(
                            '''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''',
                            (dynamic_id, self.uploader_uid, 0, json.dumps(dynamic)))
                        if self.cache_resource:
                            self.download_resources(dynamic, self.resource_path)
                    counter = counter + 1
            self._save_data()
            if dynamic_offset == 0:
                return counter

    def get_update(self):
        dynamic_offset = 0
        url = self.dynamic_url.format(str(dynamic_offset))
        dynamic_response = self.session.get(url)
        dynamic_history = json.loads(dynamic_response.content.decode())
        new_dynamics = []
        for dynamic in dynamic_history['data']['cards']:
            dynamic_id = dynamic['desc']['dynamic_id']
            select = self.db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''',
                                            (dynamic_id,)).fetchall()
            if len(select) == 0:
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                self.db_cursor.execute(
                    '''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''',
                    (dynamic_id, self.uploader_uid, 0, json.dumps(dynamic)))
                if self.cache_resource:
                    self.download_resources(dynamic, self.resource_path)
                new_dynamics.append(dynamic.copy())
        if len(new_dynamics) > 0:
            self._save_data()
        return new_dynamics

    def get_all_dynamics(self):
        dynamic_dict = {}
        dynamic_offset = 0
        while True:
            url = self.dynamic_url.format(str(dynamic_offset))
            # noinspection PyBroadException
            try:
                dynamic_response = self.session.get(url)
            except Exception:
                continue
            dynamic_history = json.loads(dynamic_response.content.decode())
            if dynamic_history['code'] != 0:
                time.sleep(1)
                continue
            dynamic_offset = dynamic_history['data']['next_offset']
            if 'cards' in dynamic_history['data']:
                for dynamic in dynamic_history['data']['cards']:
                    dynamic_id = dynamic['desc']['dynamic_id']
                    dynamic['card'] = json.loads(dynamic['card'])
                    dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                    dynamic_dict[str(dynamic_id)] = dynamic
            if dynamic_history['data']['next_offset'] == 0:
                return dynamic_dict

    def refresh_dynamic_status(self):
        current_dynamics = self.get_all_dynamics()
        counter = 0
        select = self.db_cursor.execute('''SELECT "id", "status" FROM "main"."dynamics" WHERE "uid" = ?;''',
                                        (self.uploader_uid,)).fetchall()
        for dynamic_record in select:
            if (not str(dynamic_record[0]) in current_dynamics) and dynamic_record[1] == 0:
                self.db_cursor.execute('''UPDATE "main"."dynamics" SET "status"=? WHERE "_rowid_"=?;''',
                                       (1, dynamic_record[0]))
                counter = counter + 1
        self._save_data()
        return counter

    def refresh_info(self):
        url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(str(self.uploader_uid))
        uploader_info_response = self.session.get(url)
        uploader_info = json.loads(uploader_info_response.content.decode())
        if uploader_info['code'] != 0:
            if uploader_info['code'] == -404:
                raise ValueError
            elif uploader_info['code'] == -400:
                raise ValueError
            else:
                raise ValueError
        uploader_name = uploader_info['data']['name']
        self.uploader_name = uploader_name
        self.db_cursor.execute('''UPDATE "main"."uploader_info" SET "name"=?, "data"=? WHERE "uid"=?;''',
                               (uploader_name, json.dumps(uploader_info['data']), self.uploader_uid))
        self._save_data()

    def close(self):
        self.db.close()

    def _save_data(self):
        self.db.commit()

    @staticmethod
    def download_resources(dynamic: dict, resource_path: str = './resource_cache'):
        def get_dict_values(data: list, target: dict):
            for key, value in target.items():
                if isinstance(value, dict):
                    get_dict_values(data, value)
                else:
                    data.append(str(value))

        dict_values = []
        get_dict_values(dict_values, dynamic)
        dict_values_str = ' '.join(dict_values)
        urls = re.findall(URL_REGEX, dict_values_str)
        downloaded_files = []
        for url in urls:
            if url[-3:] in RESOURCE_TYPES or url[-4:] in RESOURCE_TYPES or url[-5:] in RESOURCE_TYPES:
                o = urlparse(url)
                netloc = o.netloc.replace(':', '_')
                down_path = resource_path + '/' + netloc + '/' + o.path
                downloaded_files.append(os.path.abspath(down_path))
                if not os.path.exists(down_path):
                    response = requests.get(url)
                    if response.status_code == 200:
                        # noinspection PyBroadException
                        try:
                            os.makedirs(os.path.dirname(down_path))
                        except Exception:
                            pass
                        with open(down_path, 'wb') as f:
                            f.write(response.content)
                    else:
                        print('[WARN] Download of {} failed with code {}'.format(url, str(response.status_code)))
                        downloaded_files.pop()

        return downloaded_files

    @staticmethod
    def init_db(database_file='dynamic_data.db'):
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        db_cursor.execute('''CREATE TABLE "uploader_info" (
                                "uid"	INTEGER NOT NULL UNIQUE,
                                "name"	TEXT,
                                "data"	TEXT,
                                PRIMARY KEY("uid")
                                );''')
        db_cursor.execute('''CREATE TABLE "dynamics" (
                                "id"	INTEGER NOT NULL,
                                "uid"	INTEGER NOT NULL,
                                "status"	INTEGER NOT NULL,
                                "data"	TEXT,
                                PRIMARY KEY("id"),
                                FOREIGN KEY("uid") REFERENCES "uploader_info"("uid")
                                );''')
        db.commit()
        db.close()

    @staticmethod
    def get_dynamic(dynamic_id, database_file='dynamic_data.db'):
        """
        docstring
        """
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        select = \
            db_cursor.execute('''SELECT "id", "status" FROM "main"."dynamics" WHERE "id" = ?;''',
                              (dynamic_id,)).fetchall()[
                0]
        db.close()
        return select

    @staticmethod
    def migrate(uploader_uid, database_file='dynamic_data.db'):
        uploader_data_file = 'uploader_data/{}.json'.format(uploader_uid)
        with open(uploader_data_file, 'r') as load_file:
            migrate_data = json.load(load_file)
        session = requests.Session()
        db = sqlite3.connect(database_file)
        db_cursor = db.cursor()
        url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(str(uploader_uid))
        uploader_data = db_cursor.execute(
            '''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
        if len(uploader_data) == 0:
            uploader_info_response = session.get(url)
            uploader_info = json.loads(uploader_info_response.content.decode())
            if uploader_info['code'] != 0:
                if uploader_info['code'] == -404:
                    raise ValueError
                elif uploader_info['code'] == -400:
                    raise ValueError
                else:
                    raise ValueError
            uploader_name = uploader_info['data']['name']
            db_cursor.execute('''INSERT INTO "main"."uploader_info" ("uid", "name", "data") VALUES (?, ?, ?);''',
                              (uploader_uid, uploader_name, json.dumps(uploader_info['data'])))
        for dynamic_id, dynamic in migrate_data['dynamics'].items():
            select = db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''',
                                       (dynamic_id,)).fetchall()
            if len(select) == 0:
                db_cursor.execute(
                    '''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''',
                    (dynamic_id, uploader_uid, 0, json.dumps(dynamic)))
        db.commit()
        db.close()
