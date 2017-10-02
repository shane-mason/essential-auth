import unittest
from essentialauth import EssentialAuth, SessionAssurance, ProfileNotFoundException, ProfileAlreadyExistsException, LoginAlreadyExistsException
from datetime import datetime, timedelta
import time
import random

def make_users(count=1):
    from essential_generators import DocumentGenerator
    template = {
        '_id': 'guid',
        'login': { 'typemap': 'email', 'unique': True},
        'fname': 'word',
        'mname': 'word',
        'lname': 'word',
        'email': 'email',
        'dob': 'large_int',
        'tags': ['admin', 'buildteam', 'dev', 'mgr'],
        'desc': 'sentence'
    }

    gen = DocumentGenerator()
    gen.set_template(template)
    return gen.documents(count)




class TestTropics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.profiles = make_users(1000)

    def setUp(self):
        config = {
            'db_location': "tropic.tests.db",
            'session_idle_timeout': 10,
            'session_absolute_timeout': 20
        }
        self.tropics = EssentialAuth(config)

    def tearDown(self):
        self.tropics._reset_all(True)

    def test_add_get_profile_by_ID(self):
        profile = random.choice(self.profiles)
        self.tropics.add_profile(profile)
        result = self.tropics.get_profile(id=profile['_id'])

        self.assertIsNotNone(result)
        self.assertEqual(result["login"], profile["login"])

    def test_add_get_profile_by_Login(self):
        profile = random.choice(self.profiles)
        self.tropics.add_profile(profile)
        result = self.tropics.get_profile(login=profile['login'])

        self.assertIsNotNone(result)
        self.assertEqual(result["_id"], profile["_id"])


    def test_add_get_profiles(self):
        self.tropics.add_profiles(self.profiles)
        results = self.tropics.get_profiles()
        self.assertEqual(len(results), 1000)

    def test_add_profile_existing(self):
        self.tropics.add_profiles(self.profiles)
        with self.assertRaises(ProfileAlreadyExistsException) as context:
            self.tropics.add_profile(random.choice(self.profiles))

        with self.assertRaises(LoginAlreadyExistsException) as context:
            profile = random.choice(self.profiles)
            profile['_id'] = "id-not-in-database"
            self.tropics.add_profile(profile)


    def test_update_profile(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        changedemail = "new@doesn'texist*&^*&^&^(*&^"
        profile["email"] = changedemail

        self.tropics.update_profile(profile)
        results = self.tropics.get_profile(profile["_id"])
        self.assertEqual(results['email'], changedemail)

    def test_update_null_profile(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        profile['_id'] = 'doesntexist'
        with self.assertRaises(ProfileNotFoundException) as context:
            self.tropics.update_profile(profile)

    def test_remove_profile(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        self.tropics.remove_profile(id=profile['_id'])
        results = self.tropics.get_profile(id=profile['_id'])
        self.assertIsNone(results)

    def test_set_passphrase(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "purple"
        self.tropics.set_passphrase(profile["login"], phrase)
        results = self.tropics.verify_by_passphrase(profile["login"], phrase)
        self.assertTrue(results)


    def test_set_passphrase_null_profile(self):
        self.tropics.add_profiles(self.profiles)
        phrase = "purples98723894"
        with self.assertRaises(ProfileNotFoundException) as context:
            self.tropics.set_passphrase("namecantexist___&^%&%", phrase)

    def test_verify_by_passphrase(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "purple"
        self.tropics.set_passphrase(profile["login"], phrase)
        results = self.tropics.verify_by_passphrase(profile["login"], "notpurple")
        self.assertFalse(results)

    def test_change_credentials(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase1 = "password1"
        phrase2 = "password2"
        self.tropics.set_passphrase(profile["login"], phrase1)
        results = self.tropics.verify_by_passphrase(profile["login"], phrase1)
        self.assertTrue(results)
        self.tropics.set_passphrase(profile["login"], phrase2)
        results = self.tropics.verify_by_passphrase(profile["login"], phrase1)
        self.assertFalse(results)
        results = self.tropics.verify_by_passphrase(profile["login"], phrase2)
        self.assertTrue(results)

    def test_remove_credentials(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "purple"
        self.tropics.set_passphrase(profile["login"], phrase)
        results = self.tropics.verify_by_passphrase(profile["login"], phrase)
        self.assertTrue(results)

        self.tropics.remove_passphrase(profile["login"])


    def test_start_session(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "purple"
        self.tropics.set_passphrase(profile["login"], phrase)
        token = self.tropics.start_session(profile["login"], phrase)
        self.assertIsNotNone(token)
        results = self.tropics.validate_session(token)
        self.assertIsNotNone(results)
        self.assertEqual(results['login'], profile['login'])


    def xxtest_session_timeouts(self):

        def check_valid(token, login):
            results = self.tropics.validate_session(token)
            self.assertNotEqual(results, False)
            self.assertEqual(results['login'], login)

        def check_invalid(token):
            results = self.tropics.validate_session(token)
            self.assertFalse(results)

        #setup profile with passphrase
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "green"
        self.tropics.set_passphrase(profile["login"], phrase)

        #create the session
        token = self.tropics.start_session(profile["login"], phrase)
        started = datetime.now()

        # tests that idle_timeout keeps updateting and that absolute eventually catches it
        check_valid(token, profile['login'])
        for i in range(25):
            time.sleep(1)

            if(datetime.now() > (started + timedelta(seconds=20))):
                check_invalid(token)
                break
            else:
                check_valid(token, profile["login"])


        # tests that idle timeout catches
        token = self.tropics.start_session(profile["login"], phrase)
        time.sleep(10.1)
        check_invalid(token)

    def test_end_session(self):
        self.tropics.add_profiles(self.profiles)
        profile = random.choice(self.profiles)
        phrase = "purple"
        self.tropics.set_passphrase(profile["login"], phrase)
        token = self.tropics.start_session(profile["login"], phrase)
        self.assertIsNotNone(token)
        results = self.tropics.validate_session(token)
        self.assertIsNotNone(results)
        self.assertEqual(results['login'], profile['login'])

        self.tropics.end_session(token)

class TestSessionAssurance(unittest.TestCase):

    def test_check_expired(self):
        now = datetime.now()
        start = now - timedelta(seconds=10)
        end = now + timedelta(seconds=10)
        before_window = now - timedelta(seconds=11)
        after_window = now + timedelta(seconds=11)

        self.assertTrue(SessionAssurance._in_time_window(start, end, now))
        self.assertFalse(SessionAssurance._in_time_window(start, end, before_window))
        self.assertFalse(SessionAssurance._in_time_window(start, end, after_window))
        self.assertFalse(SessionAssurance._in_time_window(start, end, start))
        self.assertFalse(SessionAssurance._in_time_window(start, end, end))




if __name__ == '__main__':
    unittest.main()