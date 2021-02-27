import math
import uuid
from datetime import datetime, timedelta

import icalendar
import requests
from dateutil.relativedelta import relativedelta
from pytz import timezone

from config import Bilibili

cst_tz = timezone('Asia/Shanghai')
utc_tz = timezone('UTC')


def bilibili(bilibili_config: Bilibili):
    uid_list = {}
    calendar = icalendar.Calendar()
    calendar.update()
    with open('./ics/bilibili.ics', 'rb') as file:
        c = icalendar.Calendar.from_ical(file.read())
        for component in c.walk():
            if component.name == "VEVENT":
                if datetime.now(tz=cst_tz) - component.get('dtstart').dt < timedelta(days=14):
                    uid_list[(str(component.get('uid')))] = component
                    calendar.add_component(component)
    timeline = get_timeline()
    for i in range(math.ceil(bilibili_config.limit / 30)):
        limit = 30
        # 最后一页
        if i + 1 == math.ceil(bilibili_config.limit / 30):
            limit = bilibili_config.limit - i * 30
        bangumis = requests.get(
            f'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&pn={i + 1}&ps={limit}&vmid={bilibili_config.uid}').json()
        for bangumi in bangumis['data']['list']:
            # 非连载番剧
            if timeline.get(bangumi['season_id'], -1) == -1:
                continue
            title = f'{bangumi["title"]} {timeline[bangumi["season_id"]]["index"]}'
            uid = str(uuid.uuid5(uuid.NAMESPACE_OID, title)) + '@Dreace'

            datetime_start = datetime.fromtimestamp(timeline[bangumi['season_id']]['time'], cst_tz)
            datetime_end = datetime_start + relativedelta(minutes=30)
            event: icalendar.Event = uid_list.get(uid, None)
            if event:
                del event['dtstart']
                del event['dtend']
                event.add('dtstart', datetime_start)
                event.add('dtend', datetime_end)
            else:
                event = icalendar.Event()
                event.add('X-WR-TIMEZONE', 'Asia/Shanghai')
                event.add('uid', uid)
                event.add('summary', title)
                event.add('dtstart', datetime_start)
                event.add('dtend', datetime_end)
                event.add('TRIGGER', timedelta(minutes=-10))

                # 开播十分钟前提醒
                alarm = icalendar.Alarm()
                alarm.add("TRIGGER", timedelta(minutes=-10))
                alarm.add("ACTION", "DISPLAY")
                event.add_component(alarm)
                calendar.add_component(event)
    with open('./ics/bilibili.ics', 'wb') as ics_file:
        # 去掉换行
        ics_file.write(calendar.to_ical().replace('\r\n '.encode(), b''))


def get_timeline() -> dict:
    timeline_json = requests.get('https://bangumi.bilibili.com/web_api/timeline_global').json()
    timeline = {}
    for item_i in timeline_json['result']:
        for item_j in item_i['seasons']:
            timeline[item_j['season_id']] = {
                'time': item_j['pub_ts'],
                'index': item_j['pub_index']
            }
    return timeline
