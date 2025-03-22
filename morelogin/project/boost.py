import time
from loguru import logger
import requests
from DrissionPage import ChromiumPage
from concurrent.futures import ThreadPoolExecutor, as_completed
from MoreLoginVerify import MoreloginVerify


class Boost:
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
        start_env_url = f"{BASEURL}/api/env/start"
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
        boost = driver.new_tab("https://www.alphabot.app/boost")

        boost.set.window.size(940,680)

        try:
            # boost.set.window.size(740,925)
            boost.ele(
                "tag:button@class =MuiButtonBase-root MuiIconButton-root MuiIconButton-colorSuccess MuiIconButton-sizeMedium css-q0nz0x").click()
            boost.wait.ele_displayed("tag:button@text():Spin!", timeout=30)  # 等待该元素出现后再点击,等待30秒
            boost.ele("tag:button@text():Spin!").click()
            re = boost.ele("tag:span@text():YOU WON")

            if re:
                self.close_environment(env_id, env_name)
                logger.info("签到完成，关闭窗口")

        except Exception:
            with open("boost_error_env.log", "a") as f:
                f.write(env_name + "\n")
                logger.info("执行失败，页面未加载或任务已完成，错误环境保存至boost_error_env.log文件中")
                logger.info(f"环境【{env_name}】执行完毕，关闭窗口")
                self.close_environment(env_id, env_name)


if __name__ == "__main__":
    #调用验证morelogin函数
    print("---------------------------------------")
    APPID = input("输入Morelogin APP ID： ")
    SECRETKEY = input("输入Morelogin API Key: ")
    BASEURL = 'http://127.0.0.1:40000'

    moreloginverify = MoreloginVerify(APPID, SECRETKEY, BASEURL)    #实例化MoreloginVerify类

    #实例化类
    boost = Boost(APPID, SECRETKEY, BASEURL)
    max_workers = input("输入多线程执行的数量： ")
    max_workers =int(max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(boost.single_env_test, env) for env in moreloginverify.all_envid()]     #通过前面的实例化moreloginverify，直接调用all_envid函数，并返回一个数组
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("任务异常：", e)
    print("所有任务已完成。")
