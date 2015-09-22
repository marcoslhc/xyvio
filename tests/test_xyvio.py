#!/usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.test import Client
from xyvio.xivyo import app
from werkzeug.wrappers import BaseResponse
"""
test_xyvio
----------------------------------

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
