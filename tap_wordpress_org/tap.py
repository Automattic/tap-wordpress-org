"""WordPress.org tap class."""

from __future__ import annotations

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_wordpress_org.streams import (
    PluginsStream,
    ThemesStream,
    EventsStream,
    PatternsStream,
    WordPressStatsStream,
    PHPStatsStream,
    MySQLStatsStream,
    LocaleStatsStream,
)

STREAM_TYPES = [
    PluginsStream,
    ThemesStream,
    EventsStream,
    PatternsStream,
    WordPressStatsStream,
    PHPStatsStream,
    MySQLStatsStream,
    LocaleStatsStream,
]


class TapWordPressOrg(Tap):
    """WordPress.org tap class."""

    name = "tap-wordpress-org"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.wordpress.org",
            description="The URL for the WordPress.org API",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            default="tap-wordpress-org/0.1.0",
            description="User agent for API requests",
        ),
        th.Property(
            "events_location",
            th.StringType,
            description="Location for events search (e.g., 'Seattle, WA')",
        ),
        th.Property(
            "events_ip",
            th.StringType,
            description="IP address for events location detection",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self, name=stream_class.name) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapWordPressOrg.cli()