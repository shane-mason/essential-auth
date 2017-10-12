from aiohttp import web
from essential_auth.essentialauth import EssentialAuth, VerificationFailedException
import aiohttp_jinja2
import jinja2

async def auth_middleware(app, handler):
    async def middleware_handler(request):
        try:
            token = None
            profile = None
            if 'token' in request.cookies:
                token = request.cookies['token']
                profile = app['auth'].validate_session(token)
                print("Request from:" + token)
                print(profile)
            request['token'] = token
            request['profile'] = profile
            response = await handler(request)


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
    return web.Response(text="Hello, world")




async def login(request):
    context = {}
    token = None
    if request.method == "POST":
        data = await request.post()
        login_name = data['login_name']
        passphrase = data['passphrase']
        token = request.app['auth'].start_session(login_name, passphrase)

        if token:
            context = {'logged_in': True}
        else:
            context = {'logged_in' : False}

    else:
        valid = False
        if 'token' in request.cookies:
            valid = request.app['auth'].validate_session(request.cookies['token'])
            token = None

        context = {'logged_in': valid}


    response =  aiohttp_jinja2.render_template('login.html', request, context)

    if token:
        response.set_cookie('token', token)

    return response

app = web.Application(middlewares=[auth_middleware])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app.router.add_get('/', hello)
app.router.add_post('/login', login)
app.router.add_get('/login', login)

app.on_startup.append(startup)
web.run_app(app, port=8080)
def do_once():

    auth_config = {
        'db_location': "aio_http_auth.db",
        'session_idle_timeout': 86400,
        'session_absolute_timeout': 1800
    }
    a = EssentialAuth(auth_config)
    _id = a.add_profile({'login': 'testuser'})
    a.set_passphrase('testuser', 'testpass')

#do_once()
