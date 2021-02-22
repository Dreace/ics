import uuid
from datetime import datetime
import math
import icalendar
import requests
from dateutil.relativedelta import relativedelta
from pytz import timezone

from config import Bilibili

cst_tz = timezone('Asia/Shanghai')
utc_tz = timezone('UTC')


def bilibili(bilibili_config: Bilibili):
    calendar = icalendar.Calendar()
    for i in range(math.ceil(bilibili_config.limit / 30)):
        limit = 30
        # 最后一页
        if i + 1 == math.ceil(bilibili_config.limit / 30):
            limit = bilibili_config.limit - i * 30
        bangumis = requests.get(
            f'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&pn={i + 1}&ps={limit}&vmid={bilibili_config.uid}').json()
        for bangumi in bangumis['data']['list']:
            title = f'{bangumi["title"]} 第 {bangumi["new_ep"]["title"]} 话 {bangumi["new_ep"].get("long_title", "")}'
            datetime_start = datetime.strptime(bangumi["new_ep"]["pub_time"], '%Y-%m-%d %H:%M:%S')
            datetime_end = datetime_start + relativedelta(minutes=30)

            event = icalendar.Event()
            event.add('X-WR-TIMEZONE', 'Asia/Shanghai')
            event.add('uid', str(uuid.uuid5(uuid.NAMESPACE_OID, title)) + '@Dreace')
            event.add('summary', title)
            event.add('dtstamp', datetime.now())
            event.add('dtstart', datetime_start.replace(tzinfo=cst_tz).astimezone(cst_tz))
            event.add('dtend', datetime_end.replace(tzinfo=cst_tz).astimezone(cst_tz))
            calendar.add_component(event)
    with open('./ics/bilibili.ics', 'wb') as ics_file:
        # 去掉换行
        ics_file.write(calendar.to_ical().replace('\r\n '.encode(), b''))
