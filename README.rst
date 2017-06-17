vk.com API python wrapper for asyncio
=====================================
for old version of python you can use https://github.com/dimka665/vk

Features
--------
* asynchronous
* support python 3.5+ versions
* have only one dependency - ``aiohttp``
* support two-factor authentication
* support socks proxy with ``aiosocks``
* support rate limit of requests
* support Long Poll connection

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

    >>> driver = Socks5Driver(PROXY_ADDRESS, PORT)  # 1234 is port
    >>> driver = Socks5Driver(PROXY_ADDRESS, PORT, timeout=10)
    >>> driver = Socks5Driver(PROXY_ADDRESS, PORT, PROXY_LOGIN, PROXY_PASSWORD, timeout=10)

How to use custom driver with session:

.. code-block:: python

    >>> session = TokenSession(..., driver=HttpDriver())

How to use driver with own loop:

.. code-block:: python

    >>> loop = asyncio.get_event_loop()
    >>> asyncio.set_event_loop(None)
    >>> session = TokenSession(driver=HttpDriver(loop=loop))  # or Socks5Driver


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


Long Poll
---------
Use exist API object

.. code-block:: python

    >>> api = API(session)
    >>> lp = LongPoll(api, mode=2)  # default wait=25
    >>> await lp.wait()
    {"ts":1820350345,"updates":[...]}
    >>> await lp.wait()
    {"ts":1820351011,"updates":[...]}

Use Session object

.. code-block:: python

    >>> lp = LongPoll(session, mode=2)  # default wait=25
    >>> await lp.wait()
    {"ts":1820350345,"updates":[...]}
    >>> await lp.get_pts()  # return pts
    191231223
    >>> await lp.get_pts(need_ts=True)  # return pts, ts
    191231223, 1820350345

Notice that ``wait`` value only for long pool connection.

Real pause could be more ``wait`` time because of need time
for authorisation (if needed), reconnect and etc.
