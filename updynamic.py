import requests
import json
import urllib


class UploaderDynamic(object):
    def __init__(self, uploader_uid):
        super().__init__()
        self.uploader_uid = uploader_uid
        self.session = requests.Session()
        self.uploader_data_file = 'uploader_data/{}.json'.format(self.uploader_uid)
        try:
            with open(self.uploader_data_file, 'r') as load_file:
                self.uploader_data = json.load(load_file)
                self.get_update()
        except:
            url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(str(self.uploader_uid))
            uploader_info_response = self.session.get(url)
            uploader_info = json.loads(uploader_info_response.content.decode())
            self.uploader_data = {
                'info': uploader_info['data'],
                'dynamics': {}
            }
            self.fetch()
        self.uploader_name = self.uploader_data['info']['name']

    def fetch(self, dynamic_offset = 0, counter = 0):
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&offset_dynamic_id={}&need_top=1'.format(str(self.uploader_uid), str(dynamic_offset))
        dynamic_response = self.session.get(url)
        dynamic_history = json.loads(dynamic_response.content.decode())
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

    def get_update(self):
        dynamic_offset = 0
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&offset_dynamic_id={}&need_top=1'.format(str(self.uploader_uid), str(dynamic_offset))
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

    def _save_data(self):
        with open(self.uploader_data_file, 'w') as dump_file:
            json.dump(self.uploader_data, dump_file)
