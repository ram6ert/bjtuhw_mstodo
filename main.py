#!/usr/bin/env python3
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

token = os.getenv("TOKEN")
tasklist_id = os.getenv("TASKLIST_ID")
student_id = os.getenv("STUDENT_ID")
assert student_id is not None
outfile = open(os.getenv("OUTFILE"), "w") or stdout

async def main():
    cp = CoursePlatform(student_id)
    await cp.login()
    hws = await cp.fetch_hw()
    hws = list(filter(lambda x: x.open_date is None or x.open_date > last_run, hws))
    hws.sort(key=lambda x: x.end_date)
    await cp.close()

    l = TodoList(token, tasklist_id)
    await l.add_todos([ms.Todo(title=f'{hw.course_name}: {hw.title}', end_date=hw.end_date) for hw in hws])

    config = {
        'LAST_RUN': int(datetime.now(tz=timezone.utc).timestamp()),
        'TOKEN': l.credential.refresh_token,
        'STUDENT_ID': student_id,
        'TASKLIST_ID': l.get_tasklist_id()
    }

    outfile.writelines([f'{k}={v}' for k, v in config.items()])
    outfile.close()

if __name__ == '__main__':
    asyncio.run(main())
