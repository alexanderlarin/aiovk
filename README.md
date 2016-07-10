# aiovk
vk.com API python wrapper for asyncio  
this module only for python 3.5!  
for old version of python you can use https://github.com/dimka665/vk

# Annotation
In all the examples below, I will give only the {code}

    async def func():
        {code}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())


# Authorisation
**TokenSession** - if you already have token or you use requests which don't require token

    >>> session = TokenSession()
    >>> session = TokenSession(access_token='asdf123..')

**ImplicitSession** - for client authorisation in js apps and standalone (desktop and mobile) apps

    >>> session = ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID)
    >>> await session.authorize()
    >>> session.access_token
    asdfa2321afsdf12eadasf123...

With scopes:

    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify')
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 'notify,friends')
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, ['notify', 'friends'])
    ImplicitSession(USER_LOGIN, USER_PASSWORD, APP_ID, 3)  # notify and friends

Also you can use `SimpleImplicitSession` for entering confirmation code
or captcha key
