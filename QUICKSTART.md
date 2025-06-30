# Tap WordPress.org API - Quick Start Guide

## Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the tap
pip install -e .
```

## Configuration

Create a `config.json` file:

```json
{
    "api_url": "https://api.wordpress.org",
    "user_agent": "tap-wordpress-org/0.1.0",
    "events_location": "Seattle, WA",  // Optional: for events stream
    "events_ip": "1.2.3.4"            // Optional: for events stream
}
```

## Usage

### 1. Discover available streams

```bash
tap-wordpress-org --config config.json --discover > catalog.json
```

### 2. Run the tap

```bash
tap-wordpress-org --config config.json --catalog catalog.json
```

### 3. Run with state (for incremental loads)

```bash
tap-wordpress-org --config config.json --catalog catalog.json --state state.json
```

## Available Streams

1. **plugins** - WordPress plugin repository data
   - Primary key: `slug`
   - Fields: name, author, ratings, active installs, download links, etc.

2. **themes** - WordPress theme repository data
   - Primary key: `slug`
   - Fields: name, author, ratings, downloads, screenshots, etc.

3. **events** - WordPress events (WordCamps, meetups)
   - Primary key: `id`
   - Fields: title, location, date, type, etc.

4. **patterns** - Block patterns
   - Primary key: `id`
   - Fields: title, content, categories, keywords, etc.

5. **wordpress_stats** - WordPress version usage statistics
   - Primary key: `version`
   - Fields: version, count, percent

6. **php_stats** - PHP version usage statistics
   - Primary key: `version`
   - Fields: version, count, percent

7. **mysql_stats** - MySQL version usage statistics
   - Primary key: `version`
   - Fields: version, count, percent

8. **locale_stats** - Language/locale usage statistics
   - Primary key: `locale`
   - Fields: locale, count, percent

## Integration with Meltano

Add to your `meltano.yml`:

```yaml
extractors:
- name: tap-wordpress-org
  namespace: tap_wordpress_org_api
  pip_url: tap-wordpress-org
  capabilities:
  - state
  - catalog
  - discover
  settings:
  - name: api_url
    kind: string
    value: https://api.wordpress.org
    description: The URL for the WordPress.org API
  - name: user_agent
    kind: string
    value: tap-wordpress-org/0.1.0
    description: User agent for API requests
```

## Example Output

```json
{"type":"RECORD","stream":"plugins","record":{"name":"Contact Form 7","slug":"contact-form-7","active_installs":10000000,"rating":80,"last_updated":"2025-04-10 6:47am GMT"}}
```

## Development

To modify the tap:
1. Edit stream definitions in `tap_wordpress_org_api/streams.py`
2. Update schemas as needed
3. Test with: `python -m tap_wordpress_org_api.tap --config config.json --discover`