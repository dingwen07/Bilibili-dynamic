import json
import sqlite3
import time
import os

import requests


class UploaderDynamic(object):
    def __init__(self, uploader_uid, database_file='dynamic_data.db'):
        super().__init__()
        self.uploader_uid = uploader_uid
        self.dynamic_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&offset_dynamic_id={}&need_top=1'.format(str(self.uploader_uid), '{}')
        self.session = requests.Session()
        if not os.path.exists(database_file):
            UploaderDynamic.init_db(database_file)
        self.db = sqlite3.connect(database_file)
        self.db_cursor = self.db.cursor()
        uploader_data = self.db_cursor.execute('''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
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
            self.db_cursor.execute('''INSERT INTO "main"."uploader_info" ("uid", "name", "data") VALUES (?, ?, ?);''', (uploader_uid, uploader_name, json.dumps(uploader_info['data'])))
            self._save_data()
            self.fetch()
        uploader_data = self.db_cursor.execute('''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
        self.uploader_name = uploader_data[0][1]

    def fetch(self):
        counter = 0
        dynamic_offset = 0
        while True:
            url = self.dynamic_url.format(str(dynamic_offset))
            try:
                dynamic_response = self.session.get(url)
            except:
                time.sleep(1)
                continue
            dynamic_history = json.loads(dynamic_response.content.decode())
            if dynamic_history['code'] != 0:
                time.sleep(1)
                continue
            dynamic_offset = dynamic_history['data']['next_offset']
            if counter == 0:
                if not 'cards' in dynamic_history['data']:
                    self._save_data()
                    return 0
            if 'cards' in dynamic_history['data']:
                for dynamic in dynamic_history['data']['cards']:
                    dynamic_id = dynamic['desc']['dynamic_id']
                    select = self.db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''', (dynamic_id,)).fetchall()
                    if len(select) == 0:
                        dynamic['card'] = json.loads(dynamic['card'])
                        dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                        self.db_cursor.execute('''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''', (dynamic_id, self.uploader_uid, 0, json.dumps(dynamic)))
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
            select = self.db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''', (dynamic_id,)).fetchall()
            if len(select) == 0:
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                self.db_cursor.execute('''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''', (dynamic_id, self.uploader_uid, 0, json.dumps(dynamic)))
                new_dynamics.append(dynamic.copy())
        if len(new_dynamics) > 0:
            self._save_data()
        return new_dynamics

    def get_all_dynamics(self):
        dynamic_dict = {}
        dynamic_offset = 0
        while True:
            url = self.dynamic_url.format(str(dynamic_offset))
            try:
                dynamic_response = self.session.get(url)
            except:
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
        select = self.db_cursor.execute('''SELECT "id", "status" FROM "main"."dynamics" WHERE "uid" = ?;''', (self.uploader_uid,)).fetchall()
        for dynamic_record in select:
            if (not str(dynamic_record[0]) in current_dynamics) and dynamic_record[1] == 0:
                self.db_cursor.execute('''UPDATE "main"."dynamics" SET "status"=? WHERE "_rowid_"=?;''', (1, dynamic_record[0]))
                counter = counter + 1
        self._save_data()
        return counter

    def close(self):
        self.db.close()

    def _save_data(self):
        self.db.commit()

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
        select = db_cursor.execute('''SELECT "id", "status" FROM "main"."dynamics" WHERE "id" = ?;''', (dynamic_id,)).fetchall()[0]
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
        uploader_data = db_cursor.execute('''SELECT "uid", "name", "data" FROM "main"."uploader_info" WHERE "uid" = ?;''', (uploader_uid,)).fetchall()
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
            db_cursor.execute('''INSERT INTO "main"."uploader_info" ("uid", "name", "data") VALUES (?, ?, ?);''', (uploader_uid, uploader_name, json.dumps(uploader_info['data'])))
        for dynamic_id, dynamic in migrate_data['dynamics'].items():
            select = db_cursor.execute('''SELECT "id" FROM "main"."dynamics" WHERE "id" = ?;''', (dynamic_id,)).fetchall()
            if len(select) == 0:
                db_cursor.execute('''INSERT INTO "main"."dynamics" ("id", "uid", "status", "data") VALUES (?, ?, ?, ?);''', (dynamic_id, uploader_uid, 0, json.dumps(dynamic)))
        db.commit()
        db.close()
