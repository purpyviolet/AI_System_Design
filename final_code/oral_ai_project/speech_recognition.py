import sys
import json
import base64
import time
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode

class SpeechRecognition:
    def __init__(self):
        self.API_KEY = 'ZiyCG2S8pZ8g8Kq1vDzIncts'
        self.SECRET_KEY = 'xQ2DsAqAvHWuwt3qVqbre49ntzfMYSza'
        self.TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
        self.ASR_URL = 'http://vop.baidu.com/server_api'
        self.DEV_PID = 1537  # 普通话识别
        self.RATE = 16000
        self.CUID = 'python_demo'
        self.token = None
        self.token_expire_time = 0

    def fetch_token(self):
        """获取百度API的token"""
        if self.token and time.time() < self.token_expire_time:
            return self.token

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.API_KEY,
            'client_secret': self.SECRET_KEY
        }
        post_data = urlencode(params).encode('utf-8')
        req = Request(self.TOKEN_URL, post_data)
        
        try:
            f = urlopen(req)
            result_str = f.read().decode()
            result = json.loads(result_str)
            
            if 'access_token' in result:
                self.token = result['access_token']
                self.token_expire_time = time.time() + result['expires_in'] - 60  # 提前60秒过期
                return self.token
            else:
                raise Exception('获取token失败')
        except Exception as e:
            print(f'获取token出错: {str(e)}')
            return None

    def recognize_audio(self, audio_file_path):
        """识别音频文件内容"""
        try:
            # 读取音频文件
            with open(audio_file_path, 'rb') as speech_file:
                speech_data = speech_file.read()

            if len(speech_data) == 0:
                raise Exception('音频文件为空')

            # 获取token
            token = self.fetch_token()
            if not token:
                raise Exception('获取token失败')

            # 准备请求数据
            speech = base64.b64encode(speech_data).decode('utf-8')
            params = {
                'dev_pid': self.DEV_PID,
                'format': audio_file_path[-3:],  # 获取文件格式
                'rate': self.RATE,
                'token': token,
                'cuid': self.CUID,
                'channel': 1,
                'speech': speech,
                'len': len(speech_data)
            }

            # 发送请求
            post_data = json.dumps(params).encode('utf-8')
            req = Request(self.ASR_URL, post_data)
            req.add_header('Content-Type', 'application/json')

            response = urlopen(req)
            result_str = response.read().decode('utf-8')
            result = json.loads(result_str)

            if 'result' in result:
                return result['result'][0]  # 返回识别结果
            else:
                raise Exception('识别失败')

        except Exception as e:
            print(f'语音识别出错: {str(e)}')
            return None 