import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import time
from datetime import datetime


def retry(retry_time):
    def wrapper_1(func):

        def wrapper_2(*args, **kwargs):
            retry = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except:
                    if retry < retry_time:
                        time.sleep(3)
                        retry += 1
                        continue
                    log("重试失败", *args, func.__name__)
                    break
        return wrapper_2
    return wrapper_1

def log(*args):
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    print(now_str, *args)

@retry(3)
def send_mail(content, to_addr):

    from_addr = "591210216@qq.com"
    password = "daokuynnvgzabbjf"
    smtp_server = "smtp.qq.com"

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = "李先生"
    msg['To'] = to_addr
    msg['Subject'] = "疫情更新"

    server = smtplib.SMTP(smtp_server, 25)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

@retry(9999999)
def get_statistics():
    res = requests.get("https://ncov.dxy.cn/ncovh5/view/pneumonia")
    res.encoding = "utf-8"

    statistics = json.loads(re.findall("getStatisticsService = (.+?)}catch", res.text)[0])
    stat_str = "\n".join(["确诊人数：%s" % statistics["confirmedCount"], 
        "疑似人数：%s" % statistics["suspectedCount"],
        "死亡人数：%s" % statistics["deadCount"], 
        "治愈人数：%s" % statistics["curedCount"]])
    statistics["stat_str"] = stat_str

    return statistics

if __name__ == "__main__":

    first_check = True
    seen = {
        "confirmedCount": 0,
        "suspectedCount": 0,
        "deadCount": 0,
        "curedCount": 0,
    }

    while True:
        log("Checking...")
        stat = get_statistics()

        changed = (stat["confirmedCount"] != seen["confirmedCount"]) or (stat["deadCount"] != seen["deadCount"]) or (stat["curedCount"] != seen["curedCount"])
        if changed:
            log(stat["stat_str"])
        seen.update(stat)
        time.sleep(10)
