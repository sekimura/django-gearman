#!/usr/bin/env python
import os
import sys

from django.conf import settings

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
print TEST_ROOT

if not settings.configured:
    settings.configure(
        TEST_ROOT = TEST_ROOT,
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS = [
            'django_gearman',
            'django_gearman.tests.testapp',
        ],
        GEARMAN_JOB_NAME = '%(app)s.%(job)s',
        GEARMAN_SERVERS = ['127.0.0.1:9050'],
    )

from django.test.simple import run_tests


def runtests(*test_args):
    if not test_args:
        test_args = ['testapp']
    sys.path.insert(0, os.path.dirname(TEST_ROOT))
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
