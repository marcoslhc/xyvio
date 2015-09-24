#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path = [
    '/Users/marcoslh/Documents/xyvio',
    '/Users/marcoslh/Documents/xyvio/xyvio'
] + sys.path

from werkzeug.test import Client
from xyvio.xyvio import app
from werkzeug.wrappers import BaseResponse
"""
Tests for `xyvio` module.
"""

import unittest

from xyvio import xyvio


class TestXyvio(unittest.TestCase):

    def setUp(self):
        self.client = Client(app, BaseResponse)

    def test_base36_encode(self):
        pass

    def test_render_template(self):
        pass

    def test_dispatch_request(self):
        pass

    def test_on_new_url(self):
        pass

    def test_insert_url(self):
        pass

    def test_on_follow_short_link(self):
        pass

    def test_on_short_link_details(self):
        pass

    def test_is_valid_url(self):
        pass

    def tearDown(self):
        pass
