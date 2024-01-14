import requests
import time
from datetime import datetime, timedelta
import json


last_max_ctime = 0  # 全局变量，用于存储上次检查时的最大ctime
last_max_top_ctime = 0 # 全局变量，用于存储当前置顶消息的ctime
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh-HK;q=0.8,zh;q=0.7,en;q=0.6,en-GB;q=0.5,en-US;q=0.4',
    'Cookie': "LIVE_BUVID=AUTO2615961160026458; PVID=1; CURRENT_FNVAL=4048; bsource=search_bing; innersign=0; theme_style=light; FEED_LIVE_VERSION=V8; buvid_fp=09ac033591caf0d68c899edf8e7c0e8d; home_feed_column=5; nostalgia_conf=-1; buvid4=F6D1C3B4-23F1-2D43-4A0A-C0559E00500986132-022030423-RWL9F7QZC6vJpL%2FhqFVmXg%3D%3D; browser_resolution=1632-914; buvid3=B6B51FCE-A534-E596-CDD1-FFFBA7B5DE0103408infoc; b_nut=1705242503; i-wanna-go-back=-1; b_ut=7; b_lsid=826CC25B_18D085FA557; _uuid=593D7422-873E-7684-28C2-546CC4D9924102501infoc; enable_web_push=DISABLE; header_theme_version=undefined; SESSDATA=456ddbdf%2C1720794544%2C565b4%2A12CjAeKMFdyjYiOTLVy-wzJXr7SjzrSZ9mYXiBtD5OoofyirXQP2ea_hNAuIRV3p7AfNESVjc3dEM2RkNvY05HN1lDTDNicTlHcjNRM3ByOVlRVXV1NWpLb2djU01vSEhRZXpPZ2FxUXg4bUkwUERSanNxOWJ4Ym52U21GZjVBODM2Wk9YY2wxS2lRIIEC; bili_jct=b90126bc2c5b916f071f55f295d0d35d; DedeUserID=1732692; DedeUserID__ckMd5=b5f4f7f3645cf428; sid=pyos3gd2; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU1MDE3NjAsImlhdCI6MTcwNTI0MjUwMCwicGx0IjotMX0.9Ytx19AxymXdSjTL3Wif6IFQzgKwIqRy8rY-I1z0pnU; bili_ticket_expires=1705501700",
    'Dnt': '1',
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/opus/883788966862520403?spm_id_from=333.999.0.0',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': 'macOS',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50'
}

def filter_new_replies(data, last_max_ctime, is_top_reply=False):

    replies_key = 'replies' if not is_top_reply else 'top_replies'
    replies = [reply for reply in data.get('data', {}).get(replies_key, []) ]
    if is_top_reply != True:
        replies = [reply for reply in replies if reply.get('mid') == 212153] #如果是非置顶 需要筛选出一哥的回复
    new_replies = [reply for reply in replies if reply.get('ctime') > last_max_ctime] #筛选出新的回复
    if new_replies:
        last_max_ctime = max(reply.get('ctime') for reply in new_replies) #存在新的回复，更新最大的ctime
    return new_replies, last_max_ctime

def print_new_replies(replies, message_type,conf):
    for reply in sorted(replies, key=lambda x: x.get('ctime')):
        datetime_object = datetime.fromtimestamp(reply.get('ctime'))
        formatted_time = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
        message = reply.get('content', {}).get('message')
        print(formatted_time, f"{message_type}:", message)
        msg_str = f"{formatted_time} {message_type}: {message}"
        if message_type == "消息内容":  #保存到配置文件中
            conf["zga"]["message"].extend([msg_str])
        else:
            conf["zga"]["top_message"] = [msg_str]

def fetch_and_parse_json(url):
    global last_max_ctime
    global last_max_top_ctime
    global headers
    file_path ="config.json"
    with open(file_path) as file:
        conf = json.load(file)

    #获取当前时间
    current_date = datetime.now()
    previous_day = current_date - timedelta(days=1)
    previous_day_timestamp = previous_day.timestamp()
    last_max_ctime = max(conf["zga"]["last_time"], previous_day_timestamp)
    last_max_top_ctime = max(conf["zga"]["last_top_time"], previous_day_timestamp)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 确保请求成功
        data = response.json()
        new_replies, new_ctime = filter_new_replies(data, last_max_ctime)
        if new_ctime > last_max_ctime:
            last_max_ctime = new_ctime
            message = print_new_replies(new_replies, "消息内容",conf)
        new_top_replies, new_top_ctime = filter_new_replies(data, last_max_top_ctime, is_top_reply=True)
        if new_top_ctime > last_max_top_ctime:
            last_max_top_ctime = new_top_ctime
            top_message = print_new_replies(new_top_replies, "置顶消息内容",conf)
    except requests.RequestException as e:
        print(f"请求出错: {e}")
    conf["zga"]["last_time"] = last_max_ctime
    conf["zga"]["last_top_time"] = last_max_top_ctime
    with open(file_path, 'w') as file:
            json.dump(conf, file, indent=4)

def main():
    url = "https://api.bilibili.com/x/v2/reply/wbi/main?oid=886478243451895861&type=17&mode=3&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=0&web_location=1315875&w_rid=c1854f7dfad46fab9b00d4126a9346d4&wts=1705242847"
    while True:
        fetch_and_parse_json(url)
        time.sleep(300)  # 休眠300秒，即5分钟

if __name__ == "__main__":
    main()

