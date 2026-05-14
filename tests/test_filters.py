
from redatui.filters import filter_keys, fuzzy_match, glob_match, regex_match


class TestFuzzyMatch:
    def test_simple_fuzzy_match(self):
        assert fuzzy_match("app", "application") is True
        assert fuzzy_match("key", "my-key-name") is True
        assert fuzzy_match("xyz", "application") is False

    def test_case_insensitive(self):
        assert fuzzy_match("KEY", "my-key") is True
        assert fuzzy_match("Key", "MyKey") is True

    def test_empty_pattern(self):
        assert fuzzy_match("", "anything") is True


class TestGlobMatch:
    def test_wildcard_match(self):
        assert glob_match("user:*", "user:1000") is True
        assert glob_match("user:*", "group:1000") is False

    def test_question_mark_match(self):
        assert glob_match("key???", "key123") is True
        assert glob_match("key???", "key12") is False

    def test_exact_match(self):
        assert glob_match("exact", "exact") is True
        assert glob_match("exact", "exactlyy") is False


class TestRegexMatch:
    def test_simple_regex(self):
        assert regex_match(r"\w+:\d+", "user:1000") is True
        assert regex_match(r"^test", "testing") is True
        assert regex_match(r"^test", "atest") is False

    def test_invalid_regex(self):
        assert regex_match(r"[invalid", "text") is False


class TestFilterKeys:
    keys = ["user:1000", "user:2000", "session:abc123", "cache:data"]

    def test_fuzzy_filter(self):
        result = filter_keys(self.keys, "user")
        assert "user:1000" in result
        assert "user:2000" in result
        assert "session:abc123" not in result

    def test_glob_filter(self):
        result = filter_keys(self.keys, "user:*")
        assert "user:1000" in result
        assert "user:2000" in result
        assert len(result) == 2

    def test_regex_filter(self):
        result = filter_keys(self.keys, r"/:\d+$/")
        assert "user:1000" in result
        assert "user:2000" in result
        assert "session:abc123" not in result

    def test_empty_pattern(self):
        result = filter_keys(self.keys, "")
        assert result == self.keys
