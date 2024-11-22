#!/usr/bin/env python3
import math
import os
from sys import stdout

from bjtu import CoursePlatform
from datetime import datetime, timezone
import asyncio
import ms
from ms import TodoList

last_run = os.getenv("LAST_RUN")
if last_run is None:
    last_run = datetime(2024, 9, 1, tzinfo=timezone.utc)
else:
    last_run = datetime.fromtimestamp(int(last_run), tz=timezone.utc)

latest_hw = os.getenv("LATEST_HW")
if latest_hw is None:
    latest_hw = last_run
else:
    latest_hw = datetime.fromtimestamp(int(latest_hw), tz=timezone.utc)

token = os.getenv("TOKEN")
tasklist_id = os.getenv("TASKLIST_ID")
student_id = os.getenv("STUDENT_ID")
assert student_id is not None
password_pattern = os.getenv("PASSWORD")
outfile = os.getenv("OUTFILE")


async def main():
    global latest_hw

    l = TodoList(token, tasklist_id)
    await l.force_login()

    cp = CoursePlatform(student_id, password_pattern)
    await cp.login()
    hws = await cp.fetch_hw()
    latest_hw = max(hws, key=lambda x: x.created_at).created_at
    hws = list(filter(lambda x: x.created_at is None or x.created_at > latest_hw, hws))
    hws.sort(key=lambda x: x.end_at)
    await cp.close()

    await l.add_todos([ms.Todo(title=f'{hw.course_name}: {hw.title}', end_date=hw.end_at, content=hw.content) for hw in hws])

    config = {
        'LAST_RUN': int(datetime.now(tz=timezone.utc).timestamp()),
        'LATEST_HW': math.ceil(latest_hw.timestamp()),
        'TOKEN': l.credential.refresh_token,
        'STUDENT_ID': student_id,
        'PASSWORD': f'hash:{cp.password_hash}',
        'TASKLIST_ID': l.get_tasklist_id()
    }

    global outfile
    if outfile is None:
        outfile = stdout
    else:
        outfile = open(outfile, 'w')
    outfile.writelines([f'{k}={v}\n' for k, v in config.items()])
    outfile.close()

if __name__ == '__main__':
    asyncio.run(main())
