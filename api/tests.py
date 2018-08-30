# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .api import Micro, MockMicro, get_micro
import responses

API = {
    "foo": {
        "base_url": "https://foo.com",
        "resources": {
            "bar": {
                "path": "foo/bar/baz/"
            }
        }
    },
}

class MicroAPITestCase(TestCase):

    def setUp(self):
        self.micro = Micro(API, "foo")
        self.mock_micro = MockMicro(self.micro)

    def test_get_micro(self):
        m = get_micro("foo", 1)
        assert m.headers.get('X_AUTHENTICATED_USERID') == '1'
        assert isinstance(m ,Micro)

    @responses.activate
    def test_can_list(self):
        self.mock_micro.expect("bar")
        result, data, is_ok = self.micro.list("bar")

    @responses.activate
    def test_can_get(self):
        self.mock_micro.expect("bar", 1)
        result, data, is_ok = self.micro.get("bar", 1)


