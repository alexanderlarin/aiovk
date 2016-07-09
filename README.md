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
    >>> as = AuthSession(USER_LOGIN, USER_PASSWORD, APP_ID)
    >>> token = as.authorize()
    >>> token
    asdfa2321afsdf12eadasf123

Also you can use `SimpleAuthSession` for entering confirmation code
or captcha key
