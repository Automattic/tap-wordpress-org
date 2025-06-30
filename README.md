# tap-wordpress-org

![Tests](https://github.com/Automattic/tap-wordpress-org/actions/workflows/test.yml/badge.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

Singer tap for WordPress.org, built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from PyPI:

```bash
pipx install tap-wordpress-org
```

Install from source:

```bash
git clone https://github.com/your-org/tap-wordpress-org.git
cd tap-wordpress-org
pip install .
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-wordpress-org --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config keys will be namespaced using the format `TAP_WORDPRESS_ORG_{CONFIG_KEY}`. For example:

```bash
export TAP_WORDPRESS_ORG_API_URL=https://api.wordpress.org
export TAP_WORDPRESS_ORG_USER_AGENT=my-app/1.0
```

### Configuration options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| api_url | False | https://api.wordpress.org | The URL for the WordPress.org API |
| user_agent | False | tap-wordpress-org/0.1.0 | User agent for API requests |
| events_location | False | None | Location for events search (e.g., 'Seattle, WA') |
| events_ip | False | None | IP address for events location detection |

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Supported Python Versions

* 3.9
* 3.10
* 3.11
* 3.12

## Streams

| Stream | Primary Key | Replication Method | Notes |
|:-------|:-----------:|:------------------:|:------|
| `plugins` | `slug` | FULL_TABLE | WordPress plugin repository data |
| `themes` | `slug` | FULL_TABLE | WordPress theme repository data |
| `events` | `id` | FULL_TABLE | WordPress events (WordCamps and meetups) |
| `patterns` | `id` | FULL_TABLE | Block patterns |
| `wordpress_stats` | `version` | FULL_TABLE | WordPress version usage statistics |
| `php_stats` | `version` | FULL_TABLE | PHP version usage statistics |
| `mysql_stats` | `version` | FULL_TABLE | MySQL version usage statistics |
| `locale_stats` | `locale` | FULL_TABLE | Language/locale usage statistics |

## Usage

You can easily run `tap-wordpress-org` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-wordpress-org --version
tap-wordpress-org --help
tap-wordpress-org --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-wordpress-org` CLI interface directly using `poetry run`:

```bash
poetry run tap-wordpress-org --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-wordpress-org
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-wordpress-org --version
# OR run a test `elt` pipeline:
meltano elt tap-wordpress-org target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.