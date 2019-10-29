# aiovk

![](https://img.shields.io/github/issues/Fahreeve/aiovk?style=flat-square) 
![](https://img.shields.io/github/stars/Fahreeve/aiovk?style=flat-square) 
![](https://img.shields.io/github/license/Fahreeve/aiovk?style=flat-square) 
![](https://img.shields.io/pypi/pyversions/aiovk?style=flat-square)

VKontakte API wrapper for asyncio.

### Features

- Asynchronous
- Supports python 3.5+ versions (for older python versions, use [dimka665/vk](https://github.com/dimka665/vk))
- Have only one dependency - `aiohttp 3+`
- Supports two-factor authentication
- Supports socks proxy with `aiosocksy`
- Supports rate limit of requests
- Supports Long Poll connection

### TODO

- [ ] Replace `aiosocksy` to `aiohttp-socks`

### Install

```
pip install aiovk
```

## Examples

### Annotation

In all the examples below, I will give only the `{code}`

```python
async def func():
    {code}

loop = asyncio.get_event_loop()
loop.run_until_complete(func())
```

### Authorization

**TokenSession**

Authorization with token or without, if you use requests which don't require token.

```python
session = TokenSession()
session = TokenSession(access_token='asdf123..')
```

**ImplicitSession** 

Authorization for js and standalone (desktop and mobile) apps.

```python
>>> session = ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID)
>>> await session.authorize()
>>> session.access_token
asdfa2321afsdf12eadasf123...
```

If you want to use scopes:

```python
ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify')
ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify,friends')
ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, ['notify', 'friends'])
ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 3)  # notify and friends
```

Also, you can use `SimpleImplicitSessionMixin` for entering confirmation code or captcha key.

**AuthorizationCodeSession** 

Authorization for server apps or Open API. See [documentation](https://vk.com/dev/authcode_flow_user) for getting the `CODE`

```python
>>> session = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI, CODE)
>>> await session.authorize()
>>> session.access_token
asdfa2321afsdf12eadasf123...
```

Or:

```python
>>> session = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI)
>>> await session.authorize(CODE)
>>> session.access_token
asdfa2321afsdf12eadasf123...
```

**Authorization using context manager** 

Use this, if you don't want to manually `session.close()` after work.

```python
async with aiovk.TokenSession(access_token=YOUR_VK_TOKEN) as ses:
    api = API(ses)...
```

Your session will be closed after execution or code error (similar to python `with`). Works with all types of authortization.

### Drivers

**HttpDriver** 

Default driver for using `aiohttp`

```python
>>> driver = HttpDriver()
>>> driver = HttpDriver(timeout=10)  # default timeout for all requests
>>> driver = Socks5Driver(PROXY_ADDRESS, PORT)  # 1234 is port
>>> driver = Socks5Driver(PROXY_ADDRESS, PORT, timeout=10)
>>> driver = Socks5Driver(PROXY_ADDRESS, PORT, PROXY_LOGIN, PROXY_PASSWORD, timeout=10)
```

Custom driver with session:

```python
>>> session = TokenSession(..., driver=HttpDriver())
```

Driver with own loop:

```python
>>> loop = asyncio.get_event_loop()
>>> asyncio.set_event_loop(None)
>>> session = TokenSession(driver=HttpDriver(loop=loop))  # or Socks5Driver
```

Driver with custom http session object:

Solves [this problem](https://stackoverflow.com/questions/29827642/asynchronous-aiohttp-requests-fails-but-synchronous-requests-succeed).

```python
>>> connector = aiohttp.TCPConnector(verify_ssl=False)
>>> session = aiohttp.ClientSession(connector=connector)
>>> driver = HttpDriver(loop=loop, session=session)
```

**LimitRateDriverMixin** 

Mixin class what allow you create new drivers with speed rate limits

```python
>>> class ExampleDriver(LimitRateDriverMixin, HttpDriver):
...     requests_per_period = 3
...     period = 1  #seconds
```

### VK API

[Documentation](https://vk.com/dev/methods) of all VK methods.

Perform request:

```python
>>> session = TokenSession()
>>> api = API(session)
>>> await api.users.get(user_ids=1)
[{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
```

Passing string as method to api:

```python
>>> session = TokenSession()
>>> api = API(session)
>>> await api('users.get', user_ids=1)
[{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
```

Also, you can add `timeout` argument for each request or define it in the session.

### Lazy VK API

Useful, when a bot has a large message flow.

```python
>>> session = TokenSession()
>>> api = LazyAPI(session)
>>> message = api.users.get(user_ids=1)
>>> await message()
[{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
```

Supports both variants like API object.

### User Long Poll

[Documentation](https://vk.com/dev/using_longpoll)

Using API object:

```python
>>> api = API(session)
>>> lp = UserLongPoll(api, mode=2)  # default wait=25
>>> await lp.wait()
{"ts":1820350345,"updates":[...]}
>>> await lp.wait()
{"ts":1820351011,"updates":[...]}
```

Using Session object:

```python
>>> lp = UserLongPoll(session, mode=2)  # default wait=25
>>> await lp.wait()
{"ts":1820350345,"updates":[...]}
>>> await lp.get_pts()  # return pts
191231223
>>> await lp.get_pts(need_ts=True)  # return pts, ts
191231223, 1820350345
```

Notice, that `wait` value is only for long pool connection. Real pause could be more than `wait` time, because of  authorization (if needed), reconnect and etc.

### Bots Long Poll

[Documentation](https://vk.com/dev/bots_longpoll)

Using API object:

```python
>>> api = API(session)
>>> lp = BotsLongPoll(api, mode=2, group_id=1)  # default wait=25
>>> await lp.wait()
{"ts":345,"updates":[...]}
>>> await lp.wait()
{"ts":346,"updates":[...]}
```

Using Session object:

```python
>>> lp = BotsLongPoll(session, mode=2, group_id=1)  # default wait=25
>>> await lp.wait()
{"ts":78455,"updates":[...]}
>>> await lp.get_pts()  # return pts
191231223
>>> await lp.get_pts(need_ts=True)  # return pts, ts
191231223, 1820350345
```

Notice, that `wait` value is only for long pool connection. Real pause could be more than `wait` time, because of  authorization (if needed), reconnect and etc.
