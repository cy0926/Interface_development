from django.test import TestCase, Client
from sign.models import Event, Guest
from django.contrib.auth.models import User
from datetime import datetime


# Create your tests here.
class ModelsTest(TestCase):
    '''模型测试'''

    def setUp(self):
        Event.objects.create(id=1, name="oneplus 3 event", status=True, limit=2000,
                             address='shenzhen', start_time='2016-08-31 02:18:22')
        Guest.objects.create(id=1, event_id=1, realname='alen', phone='13350326115',
                             email='alen@mail.com', sign=False)

    def test_event_models(self):
        result = Event.objects.get(name="oneplus 3 event")
        self.assertEqual(result.address, "shenzhen")
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(phone='13350326115')
        self.assertEqual(result.realname, "alen")
        # self.assertTrue(result.sign)


class LoginActionTest(TestCase):
    ''' 测试登录函数'''

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        self.c = Client()

    def test_login_action_username_password_null(self):
        ''' 用户名密码为空 '''
        test_data = {'username': '', 'password': ''}
        response = self.c.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or password null", response.content)

    def test_login_action_username_password_error(self):
        ''' 用户名密码错误 '''
        test_data = {'username': 'abc', 'password': '123'}
        response = self.c.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or password error", response.content)

    def test_login_action_success(self):
        ''' 登录成功'''
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.c.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)


class EventManageTest(TestCase):
    '''发布会管理'''

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=2, name='xiaomi5', limit=2000, status=True,
                             address='beijing', start_time=datetime(2016, 8, 10, 14, 0, 0))
        login_user = {"username": "admin", "password": "admin123456"}
        self.client.post('/login_action/', data=login_user)  # 预先登录

    def test_event_manage_success(self):
        '''测试发布会：xiaomo5'''
        response = self.client.get('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"xiaomi5", response.content)
        self.assertIn(b"beijing", response.content)

    def test_event_manage_search(self):
        '''测试发布会搜索'''
        response = self.client.get('/search_name/', {'search_name': 'xiaomi5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)


class GuestManageTest(TestCase):
    '''嘉宾管理'''

    def setUp(self):
        Event.objects.create(id=1, name="xiaomi5", limit=2000,
                             address='beijing', status=1, start_time=datetime(2016, 8, 10, 14, 0, 0))
        Guest.objects.create(realname='alen', phone=13350326100,
                             email='alen@mail.com', sign=0, event_id=1)
        User.objects.create_user('admin', 'admin@mail', 'admin123456')
        login_user = {'username': 'admin', 'password': 'admin123456'}
        self.client.post('/login_action/', data=login_user)  # 预先登录

    def test_guest_manage_success(self):
        '''测试嘉宾信息：alen'''
        response = self.client.get('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'13350326100', response.content)

    def test_guest_manage_search_success(self):
        '''测试嘉宾搜索'''
        response = self.client.get('/search_phone/', {'phone': '13350326100'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'13350326100', response.content)


class SignIndexActionTest(TestCase):
    '''发布会签到'''

    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing',
                             status=1, start_time=datetime(2017, 8, 10, 12, 30, 0))
        Event.objects.create(id=2, name='oneplus4', limit=2000, address='shenzhen',
                             status=1, start_time=datetime(2017, 7, 10, 10, 30, 0))
        Guest.objects.create(realname='alen', phone=13350321110, email='alen@mail.com',
                             sign=0, event_id=1)
        Guest.objects.create(realname='rose', phone=13350321112, email='rose@mail.com',
                             sign=1, event_id=2)
        login_user = {'username': 'admin', 'password': 'admin123456'}
        self.client.post('/login_action/', data=login_user)

    def test_sign_index_action_phone_null(self):
        '''手机号为空'''
        response = self.client.post('/sign_index_action/1/', {'phone': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'phone error.', response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        '''手机号或发布会id错误'''
        response = self.client.post('/sign_index_action/2/', {'phone': '13350321110'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'event id or phone error.', response.content)

    def test_sign_action_user_sign_has(self):
        '''用户已签到'''
        response = self.client.post('/sign_index_action/2/', {'phone': 13350321112})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user has sign in.', response.content)

    def test_sign_action_sign_success(self):
        '''签到成功'''
        response = self.client.post('/sign_index_action/1/', {'phone': '13350321110'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sign in success!', response.content)
