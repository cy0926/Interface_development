# coding=utf-8
import unittest
import requests


class GetEventListTest(unittest.TestCase):
    ''' 查询发布会信息（带用户认证） '''

    def setUp(self):
        self.base_url = "http://127.0.0.1:8000/api/sec_get_event_list/"
        self.auth_user = ('admin', 'admin123456')

    def test_get_event_list_auth_null(self):
        ''' auth 为空'''
        r = requests.get(self.base_url, params={'eid': ''})
        result = r.json()
        self.assertEqual(result['status'], 10011)
        self.assertEqual(result['message'], 'user auth null')

    def test_get_event_list_auth_error(self):
        ''' auth 错误'''
        r = requests.get(self.base_url, auth=('abc', '123'), params={'eid': ''})
        result = r.json()
        self.assertEqual(result['status'], 10012)
        self.assertEqual(result['message'], 'user auth fail')

    # 以下用户认证成功后的操作
    def test_get_event_list_eid_error(self):
        '''eid=901 查询结果为空'''
        r = requests.get(self.base_url, auth=self.auth_user, params={'eid': 901})
        self.result = r.json()
        self.assertEqual(self.result['status'], 10022)
        self.assertEqual(self.result['message'], 'query result is empty')

    def test_get_event_list_eid_success(self):
        '''根据eid查询结果成功'''
        r = requests.get(self.base_url, auth=self.auth_user, params={'eid': 1})
        self.result = r.json()
        self.assertEqual(self.result['status'], 200)
        self.assertEqual(self.result['message'], 'success')
        self.assertEqual(self.result['data']['name'], u'红米Pro发布会')
        self.assertEqual(self.result['data']['address'], u'北京会展中心')

    def test_get_event_list_name_result_null(self):
        '''关键字abc查询'''
        r = requests.get(self.base_url, auth=self.auth_user, params={'name': 'abc'})
        self.result = r.json()
        self.assertEqual(self.result['status'], 10022)
        self.assertEqual(self.result['message'], 'query result is empty')

    def test_get_event_list_name_find(self):
        '''关键字“发布会”模糊查询'''
        r = requests.get(self.base_url, auth=self.auth_user, params={'name': '发布会'})
        self.result = r.json()
        self.assertEqual(self.result['status'], 200)
        self.assertEqual(self.result['message'], 'success')
        self.assertEqual(self.result['data'][0]['name'], u'红米Pro发布会')
        self.assertEqual(self.result['data'][0]['address'], u'北京会展中心')
