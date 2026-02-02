"""Stream type classes for tap-wordpress-org."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from singer_sdk import typing as th

from tap_wordpress_org.client import WordPressOrgAPIStream


class PluginsStream(WordPressOrgAPIStream):
    """Plugins stream."""

    name = "plugins"
    path = "/plugins/info/1.2/"
    primary_keys = ["slug"]
    replication_key = "last_updated"
    records_jsonpath = "$.plugins[*]"

    schema = th.PropertiesList(
        th.Property("slug", th.StringType, description="Plugin slug"),
        th.Property("name", th.StringType, description="Plugin name"),
        th.Property(
            "short_description", th.StringType, description="Short description"
        ),
        th.Property("author", th.StringType, description="Plugin author"),
        th.Property("author_profile", th.StringType, description="Author profile URL"),
        th.Property(
            "contributors",
            th.CustomType({"type": ["object", "array", "null"]}),
            description="Contributors",
        ),
        th.Property(
            "requires",
            th.StringType,
            description="Minimum WordPress version",
        ),
        th.Property(
            "tested",
            th.StringType,
            description="Tested up to WordPress version",
        ),
        th.Property(
            "requires_php",
            th.StringType,
            description="Minimum PHP version",
        ),
        th.Property("rating", th.NumberType, description="Plugin rating"),
        th.Property(
            "ratings",
            th.CustomType({"type": ["object", "array", "null"]}),
            description="Rating breakdown",
        ),
        th.Property("num_ratings", th.IntegerType, description="Number of ratings"),
        th.Property(
            "active_installs", th.IntegerType, description="Active installations"
        ),
        th.Property("downloaded", th.IntegerType, description="Total downloads"),
        th.Property("last_updated", th.StringType, description="Last update date"),
        th.Property("added", th.StringType, description="Date added"),
        th.Property("homepage", th.StringType, description="Plugin homepage"),
        th.Property("sections", th.ObjectType(), description="Plugin sections"),
        th.Property(
            "tags",
            th.CustomType({"type": ["object", "array", "null"]}),
            description="Plugin tags",
        ),
        th.Property("versions", th.ObjectType(), description="Available versions"),
        th.Property("donate_link", th.StringType, description="Donation link"),
        th.Property("download_link", th.StringType, description="Download link"),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return URL parameters for plugin search."""
        params = {
            "action": "query_plugins",
            "per_page": 100,
            "browse": "updated",  # Use 'updated' for better incremental sync
        }
        if next_page_token:
            params["page"] = next_page_token

        return params

    def get_starting_timestamp(self, context: Optional[dict]) -> Optional[datetime]:
        """Get starting timestamp for incremental replication."""
        state = self.get_context_state(context)
        rep_key_value = state.get("replication_key_value")
        if rep_key_value:
            return datetime.fromisoformat(rep_key_value.replace("Z", "+00:00"))

        # Fall back to config start_date
        start_date = self.config.get("start_date")
        if start_date:
            return start_date

        return None

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """Post-process record with custom transformations."""
        try:
            # Validate required fields
            if not row.get("slug"):
                self.logger.warning(
                    f"Skipping plugin record missing required 'slug' field: {row}"
                )
                return None

            # Custom transformation: HTML entity decoding
            if row.get("name"):
                row["name"] = row["name"].replace("&#8211;", "–").replace("&amp;", "&")

            if row.get("short_description"):
                row["short_description"] = (
                    row["short_description"]
                    .replace("&#8211;", "–")
                    .replace("&amp;", "&")
                )

            # Custom transformation: Normalize boolean fields to null
            for field in ["requires_php", "requires", "tested"]:
                if row.get(field) is False:
                    row[field] = None

            # Handle invalid date values
            if row.get("last_updated") == "0000-00-00 00:00:00":
                row["last_updated"] = None

            return self._filter_by_replication_key(row, context)

        except Exception as e:
            self.logger.error(
                f"Error processing plugin record {row.get('slug', 'unknown')}: {e}"
            )
            # Return original record rather than failing completely
            return row

    def get_next_page_token(self, response, previous_token) -> Optional[Any]:
        """Return the next page token."""
        if self._stop_pagination:
            return None

        data = response.json()
        if "info" in data:
            current_page = data["info"].get("page", 1)
            total_pages = data["info"].get("pages", 1)
            if current_page < total_pages:
                return current_page + 1
        return None


class ThemesStream(WordPressOrgAPIStream):
    """Themes stream."""

    name = "themes"
    path = "/themes/info/1.2/"
    primary_keys = ["slug"]
    replication_key = "last_updated_time"
    records_jsonpath = "$.themes[*]"

    schema = th.PropertiesList(
        th.Property("slug", th.StringType, description="Theme slug"),
        th.Property("name", th.StringType, description="Theme name"),
        th.Property("version", th.StringType, description="Theme version"),
        th.Property("preview_url", th.StringType, description="Preview URL"),
        th.Property("author", th.ObjectType(), description="Theme author"),
        th.Property("screenshot_url", th.StringType, description="Screenshot URL"),
        th.Property("rating", th.NumberType, description="Theme rating"),
        th.Property("num_ratings", th.IntegerType, description="Number of ratings"),
        th.Property("downloaded", th.IntegerType, description="Total downloads"),
        th.Property("last_updated", th.StringType, description="Last update date"),
        th.Property(
            "last_updated_time", th.StringType, description="Last update timestamp"
        ),
        th.Property("homepage", th.StringType, description="Theme homepage"),
        th.Property("sections", th.ObjectType(), description="Theme sections"),
        th.Property("tags", th.ObjectType(), description="Theme tags"),
        th.Property("download_link", th.StringType, description="Download link"),
        th.Property("parent", th.StringType, description="Parent theme slug"),
        th.Property(
            "requires",
            th.StringType,
            description="Minimum WordPress version",
        ),
        th.Property(
            "requires_php",
            th.StringType,
            description="Minimum PHP version",
        ),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return URL parameters for theme search."""
        params = {
            "action": "query_themes",
            "request[per_page]": 100,
            "request[browse]": "updated",
            "request[fields][last_updated]": "true",
        }
        if next_page_token:
            params["request[page]"] = next_page_token

        return params

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """Post-process record with custom transformations."""
        try:
            # Validate required fields
            if not row.get("slug"):
                self.logger.warning(
                    f"Skipping theme record missing required 'slug' field: {row}"
                )
                return None

            # Custom transformation: HTML entity decoding
            if row.get("name"):
                row["name"] = row["name"].replace("&#8211;", "–").replace("&amp;", "&")

            # Custom transformation: Normalize boolean fields to null
            for field in ["requires_php", "requires"]:
                if row.get(field) is False:
                    row[field] = None

            # Handle invalid date values
            if row.get("last_updated") == "0000-00-00 00:00:00":
                row["last_updated"] = None

            return self._filter_by_replication_key(row, context)

        except Exception as e:
            self.logger.error(
                f"Error processing theme record {row.get('slug', 'unknown')}: {e}"
            )
            # Return original record rather than failing completely
            return row

    def get_next_page_token(self, response, previous_token) -> Optional[Any]:
        """Return the next page token."""
        if self._stop_pagination:
            return None

        data = response.json()
        if "info" in data:
            current_page = data["info"].get("page", 1)
            total_pages = data["info"].get("pages", 1)
            if current_page < total_pages:
                return current_page + 1
        return None


class EventsStream(WordPressOrgAPIStream):
    """Events stream."""

    name = "events"
    path = "/events/1.0/"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.events[*]"

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Event ID"),
        th.Property("title", th.StringType, description="Event title"),
        th.Property("url", th.StringType, description="Event URL"),
        th.Property(
            "location",
            th.ObjectType(
                th.Property("latitude", th.NumberType),
                th.Property("longitude", th.NumberType),
                th.Property("country", th.StringType),
                th.Property("location", th.StringType),
            ),
            description="Event location",
        ),
        th.Property("date", th.StringType, description="Event date"),
        th.Property("end_date", th.StringType, description="Event end date"),
        th.Property("type", th.StringType, description="Event type"),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return URL parameters for events."""
        params = {
            "number": 100,
        }
        if self.config.get("events_location"):
            params["location"] = self.config.get("events_location")
        if self.config.get("events_ip"):
            params["ip"] = self.config.get("events_ip")
        return params


class PatternsStream(WordPressOrgAPIStream):
    """Block patterns stream."""

    name = "patterns"
    path = "/patterns/1.0/"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.patterns[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, description="Pattern ID"),
        th.Property(
            "title",
            th.ObjectType(
                th.Property("raw", th.StringType),
                th.Property("rendered", th.StringType),
            ),
            description="Pattern title",
        ),
        th.Property(
            "content",
            th.ObjectType(
                th.Property("raw", th.StringType),
                th.Property("rendered", th.StringType),
            ),
            description="Pattern content",
        ),
        th.Property(
            "categories", th.ArrayType(th.IntegerType), description="Category IDs"
        ),
        th.Property(
            "keywords", th.ArrayType(th.IntegerType), description="Keyword IDs"
        ),
        th.Property(
            "pattern_meta",
            th.ObjectType(
                th.Property("viewport_width", th.IntegerType),
            ),
            description="Pattern metadata",
        ),
        th.Property(
            "category_slugs", th.ArrayType(th.StringType), description="Category slugs"
        ),
        th.Property(
            "keyword_slugs", th.ArrayType(th.StringType), description="Keyword slugs"
        ),
        th.Property(
            "meta",
            th.ObjectType(
                th.Property("author_name", th.StringType),
                th.Property("author_username", th.StringType),
                th.Property("is_web_only", th.BooleanType),
            ),
            description="Pattern metadata",
        ),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return URL parameters for patterns."""
        params = {
            "per_page": 100,
        }
        if next_page_token:
            params["offset"] = next_page_token
        return params

    def get_next_page_token(self, response, previous_token) -> Optional[Any]:
        """Return the next page token."""
        data = response.json()
        if "patterns" in data and len(data["patterns"]) == 100:
            current_offset = previous_token or 0
            return current_offset + 100
        return None


class WordPressStatsStream(WordPressOrgAPIStream):
    """WordPress version statistics stream."""

    name = "wordpress_stats"
    path = "/stats/wordpress/1.0/"
    primary_keys = ["version"]
    replication_key = None
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("version", th.StringType, description="WordPress version"),
        th.Property("count", th.IntegerType, description="Number of installations"),
        th.Property(
            "percent", th.NumberType, description="Percentage of total installations"
        ),
    ).to_dict()

    def parse_response(self, response):
        """Parse the WordPress stats response."""
        data = response.json()
        records = []
        for version, count in data.items():
            records.append(
                {
                    "version": version,
                    "count": int(count),
                    "percent": (
                        float(count) / sum(int(v) for v in data.values()) * 100
                        if data
                        else 0
                    ),
                }
            )
        return records


class PHPStatsStream(WordPressOrgAPIStream):
    """PHP version statistics stream."""

    name = "php_stats"
    path = "/stats/php/1.0/"
    primary_keys = ["version"]
    replication_key = None
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("version", th.StringType, description="PHP version"),
        th.Property("count", th.IntegerType, description="Number of installations"),
        th.Property(
            "percent", th.NumberType, description="Percentage of total installations"
        ),
    ).to_dict()

    def parse_response(self, response):
        """Parse the PHP stats response."""
        data = response.json()
        records = []
        for version, count in data.items():
            records.append(
                {
                    "version": version,
                    "count": int(count),
                    "percent": (
                        float(count) / sum(int(v) for v in data.values()) * 100
                        if data
                        else 0
                    ),
                }
            )
        return records


class MySQLStatsStream(WordPressOrgAPIStream):
    """MySQL version statistics stream."""

    name = "mysql_stats"
    path = "/stats/mysql/1.0/"
    primary_keys = ["version"]
    replication_key = None
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("version", th.StringType, description="MySQL version"),
        th.Property("count", th.IntegerType, description="Number of installations"),
        th.Property(
            "percent", th.NumberType, description="Percentage of total installations"
        ),
    ).to_dict()

    def parse_response(self, response):
        """Parse the MySQL stats response."""
        data = response.json()
        records = []
        for version, count in data.items():
            records.append(
                {
                    "version": version,
                    "count": int(count),
                    "percent": (
                        float(count) / sum(int(v) for v in data.values()) * 100
                        if data
                        else 0
                    ),
                }
            )
        return records


class LocaleStatsStream(WordPressOrgAPIStream):
    """Locale/Language statistics stream."""

    name = "locale_stats"
    path = "/stats/locale/1.0/"
    primary_keys = ["locale"]
    replication_key = None
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("locale", th.StringType, description="Locale code"),
        th.Property("count", th.IntegerType, description="Number of installations"),
        th.Property(
            "percent", th.NumberType, description="Percentage of total installations"
        ),
    ).to_dict()

    def parse_response(self, response):
        """Parse the locale stats response."""
        data = response.json()
        records = []
        for locale, count in data.items():
            records.append(
                {
                    "locale": locale,
                    "count": int(count),
                    "percent": (
                        float(count) / sum(int(v) for v in data.values()) * 100
                        if data
                        else 0
                    ),
                }
            )
        return records
