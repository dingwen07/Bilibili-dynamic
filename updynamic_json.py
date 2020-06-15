import json
import os
import time

import requests


class UploaderDynamic(object):
    def __init__(self, uploader_uid):
        super().__init__()
        self.uploader_uid = uploader_uid
        self.dynamic_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&offset_dynamic_id={}&need_top=1'.format(str(self.uploader_uid), '{}')
        self.session = requests.Session()
        self.uploader_data_file = 'uploader_data/{}.json'.format(self.uploader_uid)
        if os.access(self.uploader_data_file, os.R_OK):
            with open(self.uploader_data_file, 'r') as load_file:
                self.uploader_data = json.load(load_file)
                self.get_update()
        else:
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
            self.uploader_data = {
                'info': uploader_info['data'],
                'dynamics': {}
            }
            self.fetch()
        self.uploader_name = self.uploader_data['info']['name']

    def fetch(self):
        counter = 0
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
            if counter == 0:
                if not 'cards' in dynamic_history['data']:
                    self._save_data()
                    return 0
            for dynamic in dynamic_history['data']['cards']:
                dynamic_id = dynamic['desc']['dynamic_id']
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                self.uploader_data['dynamics'][str(dynamic_id)] = dynamic
                counter = counter + 1
            if dynamic_offset == 0:
                self._save_data()
                return counter


    '''
    def fetch(self, dynamic_offset = 0, counter = 0):
        url = self.dynamic_url.format(str(dynamic_offset))
        dynamic_response = self.session.get(url)
        dynamic_history = json.loads(dynamic_response.content.decode())
        if counter == 0:
            if not 'cards' in dynamic_history['data']:
                self._save_data()
                return 0
        for dynamic in dynamic_history['data']['cards']:
            dynamic_id = dynamic['desc']['dynamic_id']
            dynamic['card'] = json.loads(dynamic['card'])
            dynamic['extend_json'] = json.loads(dynamic['extend_json'])
            self.uploader_data['dynamics'][str(dynamic_id)] = dynamic
            counter = counter + 1
        if dynamic_history['data']['next_offset'] == 0:
            self._save_data()
            return counter
        else:
            return self.fetch(dynamic_history['data']['next_offset'], counter)
    '''

    def get_update(self):
        dynamic_offset = 0
        url = self.dynamic_url.format(str(dynamic_offset))
        dynamic_response = self.session.get(url)
        dynamic_history = json.loads(dynamic_response.content.decode())
        new_dynamics = []
        for dynamic in dynamic_history['data']['cards']:
            dynamic_id = dynamic['desc']['dynamic_id']
            if not str(dynamic_id) in self.uploader_data['dynamics']:
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                self.uploader_data['dynamics'][str(dynamic_id)] = dynamic
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
            for dynamic in dynamic_history['data']['cards']:
                dynamic_id = dynamic['desc']['dynamic_id']
                dynamic['card'] = json.loads(dynamic['card'])
                dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                dynamic_dict[str(dynamic_id)] = dynamic
            if dynamic_history['data']['next_offset'] == 0:
                return dynamic_dict


    '''
    def get_all_dynamics(self, dynamic_dict = {}, dynamic_offset = 0):
        url = self.dynamic_url.format(str(dynamic_offset))
        dynamic_response = self.session.get(url)
        dynamic_history = json.loads(dynamic_response.content.decode())
        for dynamic in dynamic_history['data']['cards']:
            dynamic_id = dynamic['desc']['dynamic_id']
            dynamic['card'] = json.loads(dynamic['card'])
            dynamic['extend_json'] = json.loads(dynamic['extend_json'])
            dynamic_dict[str(dynamic_id)] = dynamic
        if dynamic_history['data']['next_offset'] == 0:
            return dynamic_dict
        else:
            return self.get_all_dynamics(dynamic_dict, dynamic_history['data']['next_offset'])
    '''

    def get_deleted_dynamics(self):
        current_dynamics = self.get_all_dynamics()
        deleted_dynamics = []
        for dynamic_id in self.uploader_data['dynamics']:
            if not dynamic_id in current_dynamics:
                deleted_dynamics.append(self.uploader_data['dynamics'][dynamic_id])
        return deleted_dynamics

    def _save_data(self):
        with open(self.uploader_data_file, 'w') as dump_file:
            json.dump(self.uploader_data, dump_file)
