import asyncio
from typing import Dict, Any, Optional, Callable, NamedTuple

from azure.core.credentials import TokenCredential, AccessToken
from azure.core.credentials_async import AsyncTokenCredential
from msal import PublicClientApplication
from msgraph import GraphServiceClient, GraphRequestAdapter
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from msgraph.generated.models.todo_task import TodoTask
from msgraph.generated.models.todo_task_list import TodoTaskList
from msgraph.generated.users.item.todo.lists.item.todo_task_list_item_request_builder import \
    TodoTaskListItemRequestBuilder
from msgraph_core import AzureIdentityAuthenticationProvider
from datetime import datetime, timezone

CLIENT_ID = "19072e73-7895-42cb-9ce9-af24d559a2f6"

class PersistentDeviceCodeCredential(AsyncTokenCredential):
    def __init__(self, refresh_token: str = None, callback: Callable[[str, str], None] = None):
        self.callback = callback
        self.refresh_token = refresh_token

        self.app = PublicClientApplication(
            client_id=CLIENT_ID,
            authority="https://login.microsoftonline.com/consumers",
        )

    def device_code_login(self, scopes) -> dict:
        flow = self.app.initiate_device_flow(scopes=list(scopes))
        if self.callback is None:
            print(flow['message'])
        else:
            self.callback(flow['verification_uri'], flow['user_code'])
        return self.app.acquire_token_by_device_flow(flow)

    async def get_token(
            self,
            *scopes: str,
            claims: Optional[str] = None,
            tenant_id: Optional[str] = None,
            enable_cae: bool = False,
            **kwargs: Any,
    ) -> AccessToken:
        result = {}
        if self.refresh_token is not None:
            result = self.app.acquire_token_by_refresh_token(self.refresh_token, list(scopes))
        if 'access_token' not in result:
            result = self.device_code_login(scopes)
        self.refresh_token = result['refresh_token']

        if 'access_token' not in result:
            raise Exception('Failure logging in.')
        return AccessToken(result['access_token'], int(datetime.now(timezone.utc).timestamp()) + result['expires_in'])

class Todo(NamedTuple):
    title: str
    end_date: datetime
    content: str


class TodoList:
    def __init__(self, token: str = None, tasklist_id: str = None):
        self.tasklist_id = tasklist_id
        self.credential = PersistentDeviceCodeCredential(refresh_token=token, callback=self.login_callback)
        self.client = GraphServiceClient(
            request_adapter=
                GraphRequestAdapter(
                    AzureIdentityAuthenticationProvider(credentials=self.credential, scopes=["Tasks.ReadWrite"])))

    async def force_login(self):
        try:
            await self.client.me.get()
        except:
            pass

    def login_callback(self, uri, code):
        print(f'Login at {uri} with {code}.')


    async def create_task_list_if_not_exist(self) -> TodoTaskListItemRequestBuilder:
        l = None
        try:
            if self.tasklist_id:
                l = self.client.me.todo.lists.by_todo_task_list_id(self.tasklist_id)
                await l.get()
        except ODataError:
            l = None
        if l is None:
            l = await self.client.me.todo.lists.post(TodoTaskList(display_name="BJTU Homework"))
            self.tasklist_id = l.id

            l = self.client.me.todo.lists.by_todo_task_list_id(l.id)
        return l


    async def add_todos(self, todos: list[Todo]):
        l = await self.create_task_list_if_not_exist()
        tasks = []
        for todo in todos:
            tasks.append(l.tasks.post(TodoTask(title=todo.title,
                                body=ItemBody(content_type=BodyType("html"),
                                              content=todo.content),
                                                due_date_time=DateTimeTimeZone(
                                                    date_time=todo.end_date.strftime("%Y-%m-%dT%H:%M"),
                                                    time_zone="Asia/Shanghai"))))
        for task in tasks:
            await task
            # try not to exceed the limit
            await asyncio.sleep(1)

        # await asyncio.gather(*tasks)

    def get_tasklist_id(self):
        return self.tasklist_id
