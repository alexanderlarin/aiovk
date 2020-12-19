vk.com API python wrapper for asyncio
=====================================
for old version of python you can use https://github.com/dimka665/vk

Features
--------
* asynchronous
* support python 3.5+ versions
* have only one dependency - ``aiohttp 3+``
* support two-factor authentication
* support socks proxy with ``aiohttp-socks``
* support rate limit of requests
* support Long Poll connection

TODO
----
* need refactoring tests for ``AsyncVkExecuteRequestPool``

Install
-------

.. code-block:: bash

    pip install aiovk

Examples
========
Annotation
----------
In all the examples below, I will give only the ``{code}``

.. code-block:: python

    async def func():
        {code}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())


Authorization
-------------
**TokenSession** - if you already have token or you use requests which don't require token

.. code-block:: python

    session = TokenSession()
    session = TokenSession(access_token='asdf123..')

**ImplicitSession** - client authorization in js apps and standalone (desktop and mobile) apps

.. code-block:: python

    >>> session = ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID)
    >>> await session.authorize()
    >>> session.access_token
    asdfa2321afsdf12eadasf123...

With scopes:

.. code-block:: python

    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify')
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify,friends')
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, ['notify', 'friends'])
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 3)  # notify and friends

Also you can use ``SimpleImplicitSessionMixin`` for entering confirmation code
or captcha key

**AuthorizationCodeSession** - authorization for server apps or Open API

See https://vk.com/dev/authcode_flow_user for getting the CODE

.. code-block:: python

    >>> session = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI, CODE)
    >>> await session.authorize()
    >>> session.access_token
    asdfa2321afsdf12eadasf123...

Or:

.. code-block:: python

    >>> session = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI)
    >>> await session.authorize(CODE)
    >>> session.access_token
    asdfa2321afsdf12eadasf123...

**Authorization using context manager** - you won't need to use session.close() after work

.. code-block:: python

    async with aiovk.TokenSession(access_token=YOUR_VK_TOKEN) as ses:
        api = API(ses)...

And your session will be closed after all done or code fail(similar to simple "with" usage)
Works with all types of authorization

Drivers
-------
**HttpDriver** - default driver for using ``aiohttp``

.. code-block:: python

    >>> driver = HttpDriver()
    >>> driver = HttpDriver(timeout=10)  # default timeout for all requests

.. code-block:: python

    >>> driver = ProxyDriver(PROXY_ADDRESS, PORT)  # 1234 is port
    >>> driver = ProxyDriver(PROXY_ADDRESS, PORT, timeout=10)
    >>> driver = ProxyDriver(PROXY_ADDRESS, PORT, PROXY_LOGIN, PROXY_PASSWORD, timeout=10)

How to use custom driver with session:

.. code-block:: python

    >>> session = TokenSession(..., driver=HttpDriver())

How to use driver with own loop:

.. code-block:: python

    >>> loop = asyncio.get_event_loop()
    >>> asyncio.set_event_loop(None)
    >>> session = TokenSession(driver=HttpDriver(loop=loop))  # or ProxyDriver

How to use driver with custom http session object:

Solve next problem: https://stackoverflow.com/questions/29827642/asynchronous-aiohttp-requests-fails-but-synchronous-requests-succeed

.. code-block:: python

    >>> connector = aiohttp.TCPConnector(verify_ssl=False)
    >>> session = aiohttp.ClientSession(connector=connector)
    >>> driver = HttpDriver(loop=loop, session=session)


**LimitRateDriverMixin** - mixin class what allow you create new drivers with speed rate limits

.. code-block:: python

    >>> class ExampleDriver(LimitRateDriverMixin, HttpDriver):
    ...     requests_per_period = 3
    ...     period = 1  #seconds

VK API
------
First variant:

.. code-block:: python

    >>> session = TokenSession()
    >>> api = API(session)
    >>> await api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]

Second variant:

.. code-block:: python

    >>> session = TokenSession()
    >>> api = API(session)
    >>> await api('users.get', user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]

Also you can add ``timeout`` argument for each request or define it in the session

See https://vk.com/dev/methods for detailed API guide.

Lazy VK API
-----------
It is useful when a bot has a large message flow

.. code-block:: python

    >>> session = TokenSession()
    >>> api = LazyAPI(session)
    >>> message = api.users.get(user_ids=1)
    >>> await message()
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]

Supports both variants like API object

User Long Poll
--------------
For documentation, see: https://vk.com/dev/using_longpoll

Use exist API object

.. code-block:: python

    >>> api = API(session)
    >>> lp = UserLongPoll(api, mode=2)  # default wait=25
    >>> await lp.wait()
    {"ts":1820350345,"updates":[...]}
    >>> await lp.wait()
    {"ts":1820351011,"updates":[...]}

Use Session object

.. code-block:: python

    >>> lp = UserLongPoll(session, mode=2)  # default wait=25
    >>> await lp.wait()
    {"ts":1820350345,"updates":[...]}
    >>> await lp.get_pts()  # return pts
    191231223
    >>> await lp.get_pts(need_ts=True)  # return pts, ts
    191231223, 1820350345

You can iterate over events

.. code-block:: python

    >>> async for event in lp.iter():
    ...     print(event)
    {"type":..., "object": {...}}

Notice that ``wait`` value only for long pool connection.

Real pause could be more ``wait`` time because of need time
for authorization (if needed), reconnect and etc.

Bots Long Poll
--------------
For documentation, see: https://vk.com/dev/bots_longpoll

Use exist API object

.. code-block:: python

    >>> api = API(session)
    >>> lp = BotsLongPoll(api, group_id=1)  # default wait=25
    >>> await lp.wait()
    {"ts":345,"updates":[...]}
    >>> await lp.wait()
    {"ts":346,"updates":[...]}

Use Session object

.. code-block:: python

    >>> lp = BotsLongPoll(session, group_id=1)  # default wait=25
    >>> await lp.wait()
    {"ts":78455,"updates":[...]}
    >>> await lp.get_pts()  # return pts
    191231223
    >>> await lp.get_pts(need_ts=True)  # return pts, ts
    191231223, 1820350345

BotsLongPoll supports iterating too

.. code-block:: python

    >>> async for event in lp.iter():
    ...     print(event)
    {"type":..., "object": {...}}

Notice that ``wait`` value only for long pool connection.

Real pause could be more ``wait`` time because of need time
for authorization (if needed), reconnect and etc.

Async execute request pool
--------------------------
For documentation, see: https://vk.com/dev/execute

.. code-block:: python

    from aiovk.pools import AsyncVkExecuteRequestPool

    async with AsyncVkExecuteRequestPool() as pool:
        response = pool.add_call('users.get', 'YOUR_TOKEN', {'user_ids': 1})
        response2 = pool.add_call('users.get', 'YOUR_TOKEN', {'user_ids': 2})
        response3 = pool.add_call('users.get', 'ANOTHER_TOKEN', {'user_ids': 1})
        response4 = pool.add_call('users.get', 'ANOTHER_TOKEN', {'user_ids': -1})

    >>> print(response.ok)
    True
    >>> print(response.result)
    [{'id': 1, 'first_name': 'Павел', 'last_name': 'Дуров'}]
    >>> print(response2.result)
    [{'id': 2, 'first_name': 'Александра', 'last_name': 'Владимирова'}]
    >>> print(response3.result)
    [{'id': 1, 'first_name': 'Павел', 'last_name': 'Дуров'}]
    >>> print(response4.ok)
    False
    >>> print(response4.error)
    {'method': 'users.get', 'error_code': 113, 'error_msg': 'Invalid user id'}

or

.. code-block:: python

    from aiovk.pools import AsyncVkExecuteRequestPool

    pool = AsyncVkExecuteRequestPool()
    response = pool.add_call('users.get', 'YOUR_TOKEN', {'user_ids': 1})
    response2 = pool.add_call('users.get', 'YOUR_TOKEN', {'user_ids': 2})
    response3 = pool.add_call('users.get', 'ANOTHER_TOKEN', {'user_ids': 1})
    response4 = pool.add_call('users.get', 'ANOTHER_TOKEN', {'user_ids': -1})
    await pool.execute()
    ...
