# aiovk
vk.com API python wrapper for asyncio

# Annotation
In all the examples below, I will give only the {code}

    async def func():
        {code}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())


# Authorisation
    >>> as = AuthSession(USER_LOGIN, USER_PASSWORD, APP_ID)
    >>> token = as.authorize()
    >>> token
    asdfa2321afsdf12eadasf123
