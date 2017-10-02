from essentialdb import EssentialDB
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import datetime, timedelta

class LoginAlreadyExistsException(Exception):
    pass

class ProfileAlreadyExistsException(Exception):
    pass

class ProfileNotFoundException(Exception):
    pass

class VerificationFailedException(Exception):
    pass

class SessionAlreadyExistsException(Exception):
    pass


class PBKDF2Hash:

    @staticmethod
    def hash(phrase):
        return pbkdf2_sha256.hash(phrase)

    @staticmethod
    def verify(phrase, hash):
        return pbkdf2_sha256.verify(phrase, hash)

class EssentialTropicsStorage:

    def __init__(self, filepath):
        self.db = EssentialDB(filepath=filepath)
        self.db.sync()

    def profile(self, id=None, login=None ):
        if id:
            return self._profiles().get(id)
        if login:
            return self._profiles().find_one({'login': login})

    def profiles(self):
        return self._profiles().find()

    def store_profile(self, profile):
        with self._profiles() as profiles:
            return profiles.insert_one(profile)

    def store_profiles(self, profiles):
        with self._profiles() as profile_store:
            return profile_store.insert_many(profiles)

    def remove_profile(self, profile_id):
        with self._profiles() as profiles:
            return profiles.remove({'_id': profile_id})

    def credential(self, id=None, login=None ):
        if id:
            return self._credentials().get(id)
        elif login:
            return self._credentials().find_one({'login': login})
        return None

    def store_credential(self, credential):
        with self._credentials() as credential_collection:
            credential_collection.insert_one(credential)

    def remove_credential(self, id=None, login=None ):
        with self._credentials() as credential_collection:
            if id:
                return credential_collection.remove({'_id': id})
            elif login:
                return credential_collection.remove({'login': login})
            return None

    def session(self, token=None, login=None, profile_id=None):
        if token:
            return self._sessions().get(token)
        elif profile_id:
            return self._sessions().find_one({'profile_id': profile_id})
        else:
            return self._sessions().find_one({'login': login})

    def store_session(self, session):
        with self._sessions() as credential_collection:
           return credential_collection.insert_one(session)

    def remove_session(self, token):
        with self._sessions() as session_collection:
            return session_collection.remove({'_id': token})

    def _profiles(self):
        return self.db.get_collection("profiles")

    def _credentials(self):
        return self.db.get_collection("credentials")

    def _sessions(self):
        return self.db.get_collection("sessions")

    def _reset_all(self, seriously):
        if seriously:
            with self._profiles() as profiles:
                profiles.remove()
            with self._credentials() as credentials:
                credentials.remove()
            return True

        return False

class SessionAssurance:

    @staticmethod
    def _in_time_window(start_time, stop_time, to_check_time):
        if stop_time < start_time:
            return False
        if to_check_time > start_time and to_check_time < stop_time:
            return True
        return False

    @staticmethod
    def check_time(session, idle_timeout=None, absolute_timeout=None):
        if not idle_timeout and not absolute_timeout:
            raise AttributeError("No timeouts were specified - please set idle_timeout or absolute_timeout")

        now = datetime.now()
        if idle_timeout:
            idle_expires = session['last_seen'] + timedelta(seconds=idle_timeout)
            if not SessionAssurance._in_time_window(session['last_seen'], idle_expires, now):
                return False

        if absolute_timeout:
            absolute_expires = session['started'] + timedelta(seconds=absolute_timeout)
            if not SessionAssurance._in_time_window(session['started'], absolute_expires, now):
                return False

        return True



class EssentialAuth:

    default_config = {
        'db_location': "tropics.db",
        'allow_multi_sessions': True,
        'session_idle_timeout': 10,
        'session_absolute_timeout': 20
    }

    def __init__(self, config=None, store_class=EssentialTropicsStorage, hash_class=PBKDF2Hash ):
        self.config = EssentialAuth.default_config.copy()
        if not config:
            config = {}
        self.config.update(config)

        self.store = store_class(self.config['db_location'])
        self.hasher = hash_class()


    def _reset_all(self, seriously):
        self.store._reset_all(seriously)

    def check_login_available(self, login):
        existing = self.get_profile_by_login(login)
        return not existing

    def add_profile(self, profile):
        """
        Fails if user exists!
        """
        if self.store.profile(id=profile['_id']):
           raise(ProfileAlreadyExistsException())
        elif self.store.profile(login=profile['login']):
            raise(LoginAlreadyExistsException())

        return self.store.store_profile(profile)


    def add_profiles(self, profiles):
        for profile in profiles:
            if self.store.profile(id=profile['_id']):
                raise (ProfileAlreadyExistsException())
            elif self.store.profile(login=profile['login']):
                raise (LoginAlreadyExistsException())

        self.store.store_profiles(profiles)

        return len(profiles)

    def update_profile(self, profile):
        existing = self.store.profile(id=profile['_id'])
        if not existing:
           raise(ProfileNotFoundException())

        return self.store.store_profile(profile)

    def get_profile(self, id=None, login=None):
        return self.store.profile(id, login)

    def get_profiles(self):
        return self.store.profiles()

    def remove_profile(self, id=None, login=None):
        profile = self.get_profile(id=id, login=login)
        if not profile:
            return False
        return self.store.remove_profile(profile['_id'])


    def set_passphrase(self, login, passphrase):
        #TODO: check password rules
        creds = self.store.credential(login=login)
        if not creds:
            profile = self.store.profile(login=login)
            if not profile:
                raise ProfileNotFoundException("Login '%s' does not exist." % login)
            creds = {
                '_id': profile['_id'],
                'login': login,
                'hash': None,
                'last': 0
            }
        creds['updated'] = datetime.now()
        creds['hash'] = self.hasher.hash(passphrase)
        return self.store.store_credential(creds)


    def verify_by_passphrase(self, login, passphrase):
        creds = self.store.credential(login=login)
        if not creds or 'hash' not in creds or not creds['hash']:
            return False
        else:
            return self.hasher.verify(passphrase, creds['hash'])

    def remove_passphrase(self, login):
        return self.store.remove_credential(login=login)


    def start_session(self, login, passphrase):
        """
        Raises:
            UserVerificaitonFailedException if login & passphrase can not be verified.
            SessionAlreadyExistsException if allow_multi_sessions is false and a session exists for the login
        """

        if not self.verify_by_passphrase(login, passphrase):
            raise VerificationFailedException()

        # Allow multi-sessions
        if not self.config['allow_multi_sessions']:
            if self.session(login=login):
                raise SessionAlreadyExistsException

        profile = self.store.profile(login=login)

        token = uuid.uuid4()

        now = datetime.now()

        session = {
            '_id': token,
            'profile_id': profile["_id"],
            'login': profile['login'],
            'started': now,
            'last_seen': now
        }

        if self.store.store_session(session):
            return token
        else:
            return None


    def validate_session(self, token):
        session = self.store.session(token=token)

        # first, was it present?
        if not session:
            return False

        # is it valid still?
        if not SessionAssurance.check_time(session, self.config['session_idle_timeout'], self.config['session_absolute_timeout']):
            self.store.remove_session(token)
            return False

        # looks go so far, so update and store
        session['last_seen'] = datetime.now()
        self.store.store_session(session)
        return self.get_profile(id=session['profile_id'])

    def end_session(self, token):
        session = self.store.session(token=token)

        # first, was it present?
        if not session:
            return False

        return self.store.remove_session(token)
