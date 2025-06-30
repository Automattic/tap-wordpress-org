from setuptools import setup, find_packages

setup(
    name="tap-wordpress-org",
    version="0.1.0",
    description="Singer tap for WordPress.org",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "singer-sdk>=0.47.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "tap-wordpress-org=tap_wordpress_org.tap:TapWordPressOrg.cli",
        ],
    },
    python_requires=">=3.8",
)