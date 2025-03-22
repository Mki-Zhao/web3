import requests
import random
import string
import json
import hashlib
import time

class MoreloginVerify:
    def __init__(self,APPID,SECRETKEY,BASEURL):
        self.APPID = APPID
        self.SECRETKEY = SECRETKEY
        self.BASEURL = BASEURL

    def generateRandom(self,length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


    def generateNonceId(self):
        return str(int(time.time() * 1000)) + self.generateRandom()


    def md5Encode(self,nonceId):
        md5 = hashlib.md5()
        md5.update((self.APPID + nonceId + self.SECRETKEY).encode('utf-8'))
        return md5.hexdigest()


    def requestHeader(self):
        nonceId = self.generateNonceId()
        md5Str = self.md5Encode(nonceId)
        return {
            'X-Api-Id': self.APPID,
            'Authorization': md5Str,
            'X-Nonce-Id': nonceId
        }

    def all_envid(self):
        '''
        获取所有环境ID
        '''
        env_list_url = f"{self.BASEURL}/api/env/page"
        env_list_data = {
            "pageNo": 1,
            "pageSize": 100
        }
        try:
            response = requests.post(env_list_url, headers=self.requestHeader(), json=env_list_data)
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取环境列表请求错误: {e}")
            exit()
        except json.JSONDecodeError:
            print("错误：环境列表接口返回的不是 JSON 格式")
            exit()

        # 反转列表并构造环境列表
        data_list = response_data["data"]["dataList"][::-1]
        envs = []
        for item in data_list:
            envs.append({
                "id": item["id"],
                "envName": item["envName"]
            })

        if not envs:
            print("没有获取到任何环境信息")
            exit()
        print("总共获取到的环境数量：", len(envs))
        random.shuffle(envs)
        return envs  # 返回打乱后的环境列表
