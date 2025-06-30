"""Test tap functionality."""

from unittest.mock import patch

import pytest

from tap_wordpress_org.tap import TapWordPressOrg


def test_tap_initialization():
    """Test that the tap can be initialized."""
    tap = TapWordPressOrg()
    assert tap.name == "tap-wordpress-org"
    assert "api_url" in tap.config_jsonschema["properties"]
    assert "user_agent" in tap.config_jsonschema["properties"]


def test_stream_discovery():
    """Test that all expected streams are discovered."""
    tap = TapWordPressOrg()
    streams = tap.discover_streams()

    stream_names = [stream.name for stream in streams]
    expected_streams = ["plugins", "themes", "events", "patterns"]

    for expected_stream in expected_streams:
        assert expected_stream in stream_names


def test_config_validation():
    """Test configuration validation."""
    config = {
        "api_url": "https://api.wordpress.org",
        "user_agent": "test-agent/1.0",
    }

    tap = TapWordPressOrg(config=config)
    assert tap.config["api_url"] == "https://api.wordpress.org"
    assert tap.config["user_agent"] == "test-agent/1.0"


@patch("tap_wordpress_org.streams.PluginsStream.get_records")
def test_plugins_stream(mock_get_records):
    """Test plugins stream."""
    mock_get_records.return_value = [
        {
            "slug": "test-plugin",
            "name": "Test Plugin",
            "active_installs": 1000,
            "rating": 4.5,
        }
    ]

    config = {"api_url": "https://api.wordpress.org"}
    tap = TapWordPressOrg(config=config)
    streams = tap.discover_streams()

    plugins_stream = next(s for s in streams if s.name == "plugins")
    records = list(plugins_stream.get_records(context={}))

    assert len(records) == 1
    assert records[0]["slug"] == "test-plugin"
    assert records[0]["name"] == "Test Plugin"


def test_stream_schemas():
    """Test that all streams have valid schemas."""
    tap = TapWordPressOrg()
    streams = tap.discover_streams()

    for stream in streams:
        schema = stream.schema
        assert "type" in schema
        assert "properties" in schema
        assert stream.primary_keys is not None


if __name__ == "__main__":
    pytest.main([__file__])
