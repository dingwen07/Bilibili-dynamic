import requests
import json
from urllib import parse
import time


class TopicDynamic(object):
    def __init__(self, topic_name):
        super().__init__()
        self.topic = topic_name
        self.topic_url_parsed = parse.quote(topic_name)
        self.session = requests.Session()
        self.topic_data_file = 'topic_data/{}.json'.format(self.topic)
        try:
            with open(self.topic_data_file, 'r') as load_file:
                self.topic_data = json.load(load_file)
                self.get_update()
        except:
            url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new?topic_name={}'.format(
                str(self.topic_url_parsed))
            while True:
                try:
                    topic_info_response = self.session.get(url)
                    break
                except:
                    time.sleep(1)
            topic_info = json.loads(topic_info_response.content.decode())
            self.topic_data = {
                'topic': topic_info,
                'dynamics': {}
            }
            self.get_update(True)

    def get_update(self, is_first_fetch=False):
        dynamic_offset = 0
        url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history?topic_name={}&offset_dynamic_id={}'.format(
            str(self.topic_url_parsed), str(dynamic_offset))
        while True:
            try:
                dynamic_response = self.session.get(url)
                break
            except:
                time.sleep(1)
        dynamic_history = json.loads(dynamic_response.content.decode())
        new_dynamics = []
        if not is_first_fetch:
            for dynamic in dynamic_history['data']['cards']:
                dynamic_id = dynamic['desc']['dynamic_id']
                if not str(dynamic_id) in self.topic_data['dynamics']:
                    dynamic['card'] = json.loads(dynamic['card'])
                    dynamic['extend_json'] = json.loads(dynamic['extend_json'])
                    self.topic_data['dynamics'][str(dynamic_id)] = dynamic
                    new_dynamics.append(dynamic.copy())
            if len(new_dynamics) > 0:
                self._save_data()
        return new_dynamics

    def _save_data(self):
        with open(self.topic_data_file, 'w') as dump_file:
            json.dump(self.topic_data, dump_file)
