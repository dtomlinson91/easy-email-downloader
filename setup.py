# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_email_downloader']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easy-email-downloader',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Daniel Tomlinson',
    'author_email': 'dtomlinson@panaetius.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
