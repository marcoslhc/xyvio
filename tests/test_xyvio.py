#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

sys.path = [
    '/Users/marcoslh/Documents/xyvio',
    '/Users/marcoslh/Documents/xyvio/xyvio'
] + sys.path

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.wsgi import SharedDataMiddleware
from xyvio.xyvio import Shortly, base36_encode
from .util.datastore import TestDataStore
"""
Tests for `xyvio` module.
"""

import unittest

testData = TestDataStore()
app = Shortly(dataStore=testData)
app.insert_url('http://google.com')
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/static':  os.path.join(os.path.dirname(__file__), 'static')
})


class TestXyvio(unittest.TestCase):

    def setUp(self):
        self.client = Client(app, BaseResponse)

    def test_base36_encode(self):
        self.assertEqual('1', base36_encode(1))
        self.assertEqual('a', base36_encode(10))
        self.assertEqual('10', base36_encode(36))
        self.assertEqual('20', base36_encode(72))

    def test_new_url(self):
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code)

    def test_follow_short_link(self):
        resp = self.client.get('/some_other_random')
        self.assertEqual(404, resp.status_code)
        resp = self.client.get('/1')
        self.assertEqual(302, resp.status_code)

    def test_short_link_details(self):
        resp = self.client.get('/+')
        self.assertEqual(404, resp.status_code)
        resp = self.client.get('/1+')
        self.assertEqual(200, resp.status_code)

    def test_is_valid_url(self):
        pass

    def tearDown(self):
        pass
