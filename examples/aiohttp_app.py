from aiohttp import web
from essential_auth.essentialauth import EssentialAuth, VerificationFailedException

async def auth_middleware(app, handler):
    async def middleware_handler(request):
        try:
            token = None
            profile = None
            if 'token' in request.cookies:
                token = request.cookies['token']
                profile = app['auth'].validate_session(token)
            request['token'] = token
            request['profile'] = profile
            response = await handler(request)

            if token:
                response.set_cookie('token', token)

            return response
        except web.HTTPException as ex:
            raise
    return middleware_handler


async def startup(app):
    auth_config = {
        'db_location': "aio_http_auth.db",
        'session_idle_timeout': 100,
        'session_absolute_timeout': 1000
    }
    app['auth'] = EssentialAuth(auth_config)



async def hello(request):
    print(request['token'])
    print(request['profile'])
    return web.Response(text="Hello, world")

async def login(request):
    data = await request.post()
    login = data['login']
    passphrase = data['passphrase']
    token = request.app['auth'].start_session(login, passphrase)
    if token:
        response = web.Response(text=str(token))
        response.set_cookie('token', token)

    return web.Response(text="Fail...")

app = web.Application(middlewares=[auth_middleware])
app.router.add_get('/', hello)
app.router.add_post('/login', login)
app.on_startup.append(startup)
web.run_app(app, port=8080)
def do_once():

    auth_config = {
        'db_location': "aio_http_auth.db",
        'session_idle_timeout': 100,
        'session_absolute_timeout': 1000
    }
    a = EssentialAuth(auth_config)
    _id = a.add_profile({'login': 'testuser'})
    a.set_passphrase('testuser', 'testpass')

#do_once()
