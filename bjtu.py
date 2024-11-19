import hashlib
from datetime import datetime, timezone, timedelta
import asyncio
from typing import NamedTuple

import aiohttp


BASE_URL = 'http://123.121.147.7:88/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
}

UTC_8 = timezone(timedelta(hours=8))
DISTANT_PAST = datetime(1970, 1, 1, tzinfo=UTC_8)
FUTURE = datetime(2077, 1, 1, tzinfo=UTC_8)

class Homework(NamedTuple):
    course_name: str
    open_at: datetime
    end_at: datetime
    created_at: datetime
    title: str
    content: str


def parse_date(date: str) -> datetime | None:
    if len(date) > 0:
        try:
            return datetime.strptime(date, '%Y-%m-%d %H:%M').replace(tzinfo=UTC_8)
        except ValueError:
            return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC_8)


class CoursePlatform:
    def __init__(self, student_id: str):
        self.cookie_jar = aiohttp.CookieJar(unsafe=True)
        self.session = aiohttp.ClientSession(base_url=BASE_URL, headers=HEADERS, cookie_jar=self.cookie_jar)
        self.student_id = student_id

    async def http_get(self, url: str, params: dict = None) -> aiohttp.ClientResponse:
        return await self.session.get('/ve' + url, headers=HEADERS, params=params)

    async def http_post(self, url: str, data: dict = None) -> aiohttp.ClientResponse:
        return await self.session.post('/ve' + url, headers=HEADERS, data=data, allow_redirects=True)

    async def login(self):
        # get cookies
        await self.http_get('/')

        # get passcode
        await self.http_get('/GetImg')
        resp = await self.http_get('/confirmImg')
        passcode = await resp.text()

        resp = await self.http_post('/s.shtml', {
            'login': 'main_2',
            'qxkt_type': '',
            'qxkt_url': '',
            'username': self.student_id,
            'password': hashlib.md5(f'Bjtu@{self.student_id}'.encode()).hexdigest(),
            'passcode': str(passcode)
        })

        if not 200 <= resp.status < 300:
            raise Exception('Failed logging in.')

    async def fetch_course_hw(self, course) -> list[Homework]:
        result = []
        for subType in [0, 2]:
            resp = await self.http_get('/back/coursePlatform/homeWork.shtml', {
                'method': 'getHomeWorkList',
                'cId': course,
                'subType': str(subType),
                'page': '1',
                'pagesize': '50'
            })

            j = await resp.json(content_type=None)
            if j['total'] == 0:
                continue
            hws = j['courseNoteList']

            result += [Homework(course_name=hw['course_name'],
                                open_at=parse_date(hw['open_date']) or DISTANT_PAST,
                                created_at=parse_date(hw['create_date']) or DISTANT_PAST,
                                end_at=parse_date(hw['end_time']),
                                content=hw['content'],
                                title=hw['title']) for hw in hws if not hw['subTime']]

            now = datetime.now(UTC_8)
            result = list(filter(lambda hw: hw.end_at and hw.end_at > now, result))
        return result

    async def fetch_hw(self) -> list[Homework]:
        # fetch semesters
        resp = await self.http_get('/back/rp/common/teachCalendar.shtml?method=queryCurrentXq')
        current_sem = (await resp.json(content_type=None))['result'][0]

        sem_id = str(current_sem['xqCode'])

        # fetch courses
        resp = await self.http_get('/back/coursePlatform/course.shtml', {
            'method': 'getCourseList',
            'pagesize': '100',
            'page': '1',
            'xqCode': sem_id
        })
        courseList = (await resp.json(content_type=None))['courseList']

        courses = [{'id': course['id'], 'name': course['name']} for course in courseList]
        hws = await asyncio.gather(*[self.fetch_course_hw(course['id']) for course in courses])
        return [i for chw in hws for i in chw]

    async def close(self):
        return await self.session.close()