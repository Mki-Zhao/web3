import base64
import hashlib
import json
import random
import string
import time
from time import sleep
from loguru import logger
import requests
from DrissionPage import ChromiumPage
from concurrent.futures import ThreadPoolExecutor, as_completed
from MoreLoginVerify import MoreloginVerify


class Xos:
    def __init__(self,APPID, SECRETKEY, BASEURL):
        self.APPID = APPID
        self.SECRETKEY = SECRETKEY
        self.BASEURL = BASEURL
        self.moreloginverify = MoreloginVerify(APPID, SECRETKEY, BASEURL)   #在其他函数内实例化，即可直接调用

    # 关闭浏览器
    def close_environment(self,env_id, env_name):
        close_env_url = f"{self.BASEURL}/api/env/close"
        close_env_data = {"envId": env_id}
        try:
            response = requests.post(close_env_url, headers=self.moreloginverify.requestHeader(), json=close_env_data)
            response.raise_for_status()
            logger.info(f"环境【 {env_name}】 已关闭。")
        except Exception as e:
            logger.info(f"关闭环境 【{env_name}】 失败: {e}")

    # 对浏览器进行操作
    def single_env_test(self,env):
        env_id = env["id"]
        env_name = env["envName"]
        print(f"【{env_name}】开始执行")
        start_env_url = f"{self.BASEURL}/api/env/start"
        # 注意这里如果接口参数固定为某个值，可以根据需要调整
        start_env_data = {"envId": env_id}
        try:
            response = requests.post(start_env_url, headers=moreloginverify.requestHeader(), json=start_env_data)
            response.raise_for_status()
            response_data = response.json()
        except Exception as e:
            logger.info(f"【{env_name}】启动环境请求错误: {e}")
            return

        debug_port = response_data.get("data", {}).get("debugPort")
        if not debug_port:
            logger.info(f"【{env_name}】没有获取到调试端口，无法继续操作。")
            return

        driver = ChromiumPage(f"127.0.0.1:{debug_port}")
        time.sleep(2)
        x = driver.new_tab("https://x.ink/airdrop")

        # 调整窗口大小
        # teafi.set.window.size(1200,900)
        try:
            x.ele("xpath://a[normalize-space(text())='Check-In Now']").click()
            time.sleep(3)
            logger.info(f"【{env_name}】\033[32m签到完成！\033[0m")
            self.close_environment(env_id, env_name)
        except Exception:
            logger.info(f"【{env_name}】\033[31m签到已完成，无需操作。\033[0m")

            # 错误环境保存至文件中
            with open("teafi_error_env.log", "a") as f:
                f.write(env_name + "\n")
                logger.info(f"【{env_name}】执行完毕，关闭窗口,环境保存至error_env.log文件中")
                self.close_environment(env_id, env_name)


if __name__ == "__main__":
    #调用验证morelogin函数
    APPID = '1617723807467469'
    SECRETKEY = 'c8dde24bddf9492db49edc3ea13528f3'
    BASEURL = 'http://127.0.0.1:40000'

    moreloginverify = MoreloginVerify(APPID, SECRETKEY, BASEURL)    #实例化MoreloginVerify类

    #实例化类
    newton = Xos(APPID, SECRETKEY, BASEURL)
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(newton.single_env_test, env) for env in moreloginverify.all_envid()]     #通过前面的实例化moreloginverify，直接调用all_envid函数，并返回一个数组
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("任务异常：", e)
    print("所有任务已完成。")
