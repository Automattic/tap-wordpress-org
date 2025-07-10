"""Test stream functionality."""

from unittest.mock import Mock

import pytest

from tap_wordpress_org.streams import (
    EventsStream,
    LocaleStatsStream,
    MySQLStatsStream,
    PatternsStream,
    PHPStatsStream,
    PluginsStream,
    ThemesStream,
    WordPressStatsStream,
)


class TestStreams:
    """Test stream classes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "api_url": "https://api.wordpress.org",
            "user_agent": "test-agent/1.0",
        }

    def test_plugins_stream_properties(self):
        """Test plugins stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PluginsStream(tap=tap_mock)

        assert stream.name == "plugins"
        assert stream.path == "/plugins/info/1.2/"
        assert stream.primary_keys == ["slug"]
        assert stream.records_jsonpath == "$.plugins[*]"

    def test_themes_stream_properties(self):
        """Test themes stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = ThemesStream(tap=tap_mock)

        assert stream.name == "themes"
        assert stream.path == "/themes/info/1.2/"
        assert stream.primary_keys == ["slug"]
        assert stream.records_jsonpath == "$.themes[*]"

    def test_events_stream_properties(self):
        """Test events stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = EventsStream(tap=tap_mock)

        assert stream.name == "events"
        assert stream.path == "/events/1.0/"
        assert stream.primary_keys == ["id"]
        assert stream.records_jsonpath == "$.events[*]"

    def test_patterns_stream_properties(self):
        """Test patterns stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PatternsStream(tap=tap_mock)

        assert stream.name == "patterns"
        assert stream.path == "/patterns/1.0/"
        assert stream.primary_keys == ["id"]
        assert stream.records_jsonpath == "$.patterns[*]"

    def test_plugins_url_params(self):
        """Test plugins stream URL parameters."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PluginsStream(tap=tap_mock)
        params = stream.get_url_params(context={}, next_page_token=None)

        assert params["action"] == "query_plugins"
        assert params["per_page"] == 100
        assert params["browse"] == "updated"

    def test_plugins_pagination(self):
        """Test plugins stream pagination."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PluginsStream(tap=tap_mock)

        # Test first page
        params = stream.get_url_params(context={}, next_page_token=None)
        assert "page" not in params

        # Test subsequent page
        params = stream.get_url_params(context={}, next_page_token=2)
        assert params["page"] == 2

    def test_stream_schemas_contain_required_fields(self):
        """Test that all streams have required schema fields."""
        tap_mock = Mock()
        tap_mock.config = self.config
        streams = [
            PluginsStream(tap=tap_mock),
            ThemesStream(tap=tap_mock),
            EventsStream(tap=tap_mock),
            PatternsStream(tap=tap_mock),
        ]

        for stream in streams:
            schema = stream.schema
            assert "properties" in schema

            # Check primary key fields exist in schema
            for key in stream.primary_keys:
                assert key in schema["properties"]

    def test_wordpress_stats_stream_properties(self):
        """Test WordPress stats stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = WordPressStatsStream(tap=tap_mock)

        assert stream.name == "wordpress_stats"
        assert stream.path == "/stats/wordpress/1.0/"
        assert stream.primary_keys == ["version"]
        assert stream.records_jsonpath == "$[*]"

    def test_php_stats_stream_properties(self):
        """Test PHP stats stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PHPStatsStream(tap=tap_mock)

        assert stream.name == "php_stats"
        assert stream.path == "/stats/php/1.0/"
        assert stream.primary_keys == ["version"]
        assert stream.records_jsonpath == "$[*]"

    def test_mysql_stats_stream_properties(self):
        """Test MySQL stats stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = MySQLStatsStream(tap=tap_mock)

        assert stream.name == "mysql_stats"
        assert stream.path == "/stats/mysql/1.0/"
        assert stream.primary_keys == ["version"]
        assert stream.records_jsonpath == "$[*]"

    def test_locale_stats_stream_properties(self):
        """Test Locale stats stream properties."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = LocaleStatsStream(tap=tap_mock)

        assert stream.name == "locale_stats"
        assert stream.path == "/stats/locale/1.0/"
        assert stream.primary_keys == ["locale"]
        assert stream.records_jsonpath == "$[*]"

    def test_stats_parse_response(self):
        """Test stats streams parse_response method."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = WordPressStatsStream(tap=tap_mock)

        # Mock response with sample data
        mock_response = Mock()
        mock_response.json.return_value = {
            "6.4": "12345",
            "6.3": "54321",
            "6.2": "9876",
        }

        records = stream.parse_response(mock_response)

        assert len(records) == 3
        assert records[0]["version"] == "6.4"
        assert records[0]["count"] == 12345
        assert "percent" in records[0]

        # Test total percentage sums to 100
        total_percent = sum(record["percent"] for record in records)
        assert abs(total_percent - 100.0) < 0.01  # Allow for floating point precision

    def test_all_stats_stream_schemas(self):
        """Test that all stats streams have required schema fields."""
        tap_mock = Mock()
        tap_mock.config = self.config

        stats_streams = [
            WordPressStatsStream(tap=tap_mock),
            PHPStatsStream(tap=tap_mock),
            MySQLStatsStream(tap=tap_mock),
            LocaleStatsStream(tap=tap_mock),
        ]

        for stream in stats_streams:
            schema = stream.schema
            assert "properties" in schema

            # Check primary key fields exist in schema
            for key in stream.primary_keys:
                assert key in schema["properties"]

            # Check common stats fields
            assert "count" in schema["properties"]
            assert "percent" in schema["properties"]

    def test_incremental_replication_key(self):
        """Test replication key configuration for streams."""
        tap_mock = Mock()
        tap_mock.config = self.config

        plugins_stream = PluginsStream(tap=tap_mock)
        themes_stream = ThemesStream(tap=tap_mock)

        # Plugins stream uses incremental sync
        assert plugins_stream.replication_key == "last_updated"

        # Themes stream uses full table sync (no replication key)
        assert themes_stream.replication_key is None

        # Stats streams should not have replication keys (full table)
        wordpress_stats = WordPressStatsStream(tap=tap_mock)
        assert wordpress_stats.replication_key is None

    def test_post_process_transformations(self):
        """Test custom transformations in post_process method."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = PluginsStream(tap=tap_mock)

        # Test HTML entity decoding
        test_record = {
            "slug": "test-plugin",
            "name": "Plugin &#8211; Test &amp; More",
            "short_description": "Description &#8211; Test &amp; More",
            "requires_php": False,
            "requires": False,
            "tested": "6.0",
        }

        result = stream.post_process(test_record, context={})

        assert result["name"] == "Plugin – Test & More"
        assert result["short_description"] == "Description – Test & More"
        assert result["requires_php"] is None  # False converted to None
        assert result["requires"] is None  # False converted to None
        assert result["tested"] == "6.0"  # String values unchanged

    def test_themes_post_process_transformations(self):
        """Test custom transformations in themes post_process method."""
        tap_mock = Mock()
        tap_mock.config = self.config
        stream = ThemesStream(tap=tap_mock)

        test_record = {
            "slug": "test-theme",
            "name": "Theme &#8211; Beautiful &amp; Clean",
            "requires_php": False,
            "requires": False,
        }

        result = stream.post_process(test_record, context={})

        assert result["name"] == "Theme – Beautiful & Clean"
        assert result["requires_php"] is None
        assert result["requires"] is None

    def test_get_starting_timestamp(self):
        """Test incremental sync starting timestamp logic."""

        tap_mock = Mock()
        tap_mock.config = {"start_date": "2024-01-01T00:00:00Z"}
        stream = PluginsStream(tap=tap_mock)

        # Mock the get_context_state method
        stream.get_context_state = Mock(return_value={})

        # Should return config start_date when no state
        timestamp = stream.get_starting_timestamp(context={})
        assert timestamp == "2024-01-01T00:00:00Z"

        # Test with state
        stream.get_context_state = Mock(
            return_value={"replication_key_value": "2024-06-01T12:00:00Z"}
        )
        timestamp = stream.get_starting_timestamp(context={})
        assert timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__])
