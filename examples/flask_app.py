from essential_auth.essentialauth import EssentialAuth, VerificationFailedException
from flask import Flask, session, redirect, url_for, escape, request, g

app = Flask(__name__)

@app.before_request
def check_auth():
    g.auth = EssentialAuth(auth_config)

@app.route('/')
def index():
    if 'token' in session:
        profile = g.auth.validate_session(session['token'])
        if profile:
            return 'Logged in as %s' % escape(profile['login']);

    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passphrase = request.form['passphrase']
        try:
            a = g
            token = g.auth.start_session(username, passphrase)
            session['token'] = token
        except VerificationFailedException:
            return "<p>Bad login - try again</p>" + login_form

        return redirect(url_for('index'))
    else:
        return login_form

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
login_form =  '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=passphrase>
            <p><input type=submit value=Login>
        </form>
    '''

auth_config = {
    'db_location': "flask_app_auth.db",
    'session_idle_timeout': 100,
    'session_absolute_timeout': 1000
}


app.run()