import asyncio
from src.authorisation import AuthSession
from tests.test_auth_data import USER_LOGIN, USER_PASSWORD, APP_ID

async def test_auth():
    s = AuthSession(USER_LOGIN, USER_PASSWORD, APP_ID)
    b = await s.authorize()


loop = asyncio.get_event_loop()
loop.run_until_complete(test_auth())
