"""Tests for xtp.toml_writer — pure unit tests, no mocking."""

from __future__ import annotations

import tomllib

import pytest

from xtp.toml_writer import dumps


class TestFormatValues:
    def test_string(self):
        assert 'name = "hello"\n' == dumps({"name": "hello"})

    def test_string_with_quotes(self):
        result = dumps({"val": 'say "hi"'})
        assert r'"say \"hi\""' in result

    def test_bool_true(self):
        assert "flag = true\n" == dumps({"flag": True})

    def test_bool_false(self):
        assert "flag = false\n" == dumps({"flag": False})

    def test_int(self):
        assert "count = 42\n" == dumps({"count": 42})

    def test_float(self):
        assert "ratio = 3.14\n" == dumps({"ratio": 3.14})

    def test_unsupported_type(self):
        with pytest.raises(TypeError, match="Unsupported TOML value type"):
            dumps({"bad": [1, 2, 3]})


class TestSections:
    def test_sections_after_bare_keys(self):
        data = {"name": "test", "git": {"email": "a@b.c"}}
        lines = dumps(data).splitlines()
        assert lines[0] == 'name = "test"'
        assert "[git]" in lines

    def test_multiple_sections(self):
        data = {"s1": {"a": "1"}, "s2": {"b": "2"}}
        text = dumps(data)
        assert "[s1]" in text
        assert "[s2]" in text


class TestRoundTrip:
    def test_simple_round_trip(self):
        data = {"name": "test", "count": 5, "flag": True}
        assert tomllib.loads(dumps(data)) == data

    def test_sections_round_trip(self):
        data = {
            "name": "myprofile",
            "git": {"author_name": "Alice", "author_email": "a@b.c"},
            "aws": {"profile": "dev"},
        }
        assert tomllib.loads(dumps(data)) == data

    def test_empty_dict(self):
        assert tomllib.loads(dumps({})) == {}
