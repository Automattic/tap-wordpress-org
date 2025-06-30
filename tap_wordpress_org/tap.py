"""WordPress.org tap class."""

from __future__ import annotations

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

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
        th.Property(
            "stream_selection",
            th.ArrayType(th.StringType),
            description="List of stream names to sync (default: all streams)",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Start date for incremental replication (plugins/themes)",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        all_streams = [
            stream_class(tap=self, name=stream_class.name)
            for stream_class in STREAM_TYPES
        ]

        # Filter streams based on configuration
        stream_selection = self.config.get("stream_selection")
        if stream_selection:
            selected_streams = [s for s in all_streams if s.name in stream_selection]
            self.logger.info(
                f"Selected {len(selected_streams)} streams: "
                f"{[s.name for s in selected_streams]}"
            )
            return selected_streams

        return all_streams


if __name__ == "__main__":
    TapWordPressOrg.cli()
