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
    'Cookie': "buvid3=3447F442-65E1-1F81-19AB-8E0C9E3B0AC638027infoc; b_nut=1696753938; CURRENT_FNVAL=4048; _uuid=AAC97DF3-43610-8921-1EC6-3F57B3110EC1638791infoc; buvid4=8558B91B-8158-097B-F145-EC4EC98E5A4618272-022101010-8HAmuyV9nH8aZ8hFGlSsbA%3D%3D; header_theme_version=CLOSE; home_feed_column=5; rpdid=|(JYYkRkm)Rk0J'uYmY)JRm~k; buvid_fp_plain=undefined; enable_web_push=DISABLE; browser_resolution=1619-958; DedeUserID=1732692; DedeUserID__ckMd5=b5f4f7f3645cf428; share_source_origin=COPY; bsource=share_source_copy_link; hit-dyn-v2=1; PVID=1; fingerprint=3796a42c86b7668fcf2f16c2b59062be; innersign=0; SESSDATA=a38e17a9%2C1720234155%2Cadd0e%2A12CjDni0zHl2COYaZYmr_op-muJlvRk-FqjSly1GNyJtNHorgGatOrmGmkeWqrSDWofCASVlMxNXdEcHIyX1UxZXJ2alI1bDJDbkNfbExnUEROb0pOLXNldmFoVUQ4RTV0S29IZGxkSmJvM0dEaGtsenVmXy0wZGpzZnZJNzJxeWt2UFBhcWZ5eFpRIIEC; bili_jct=0d2c2c7a03f5dd7caeb53a434d4e9340; sid=8g9jctlu; bp_video_offset_1732692=884092234730831922; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDQ5NDEzNzIsImlhdCI6MTcwNDY4MjExMiwicGx0IjotMX0.8EGEPb_DfI0lf05acacYrpnqgd3Mmw9L6-VB0gbxKq0; bili_ticket_expires=1704941312; buvid_fp=3796a42c86b7668fcf2f16c2b59062be; b_lsid=101DA7687_18CE74C1447",
    'Dnt': '1',
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/opus/883788966862520403?spm_id_from=333.999.0.0',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
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
    url = "https://api.bilibili.com/x/v2/reply/wbi/main?oid=883788966862520403&type=17&mode=3&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=0&web_location=1315875&w_rid=fd8e66fab22d92c1e8d2bc02d99e5bb5&wts=1704689318"
    while True:
        fetch_and_parse_json(url)
        time.sleep(300)  # 休眠300秒，即5分钟

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()

