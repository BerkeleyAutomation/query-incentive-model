import os
import sys

os.environ['HOME'] = '/tmp'
os.environ['DJANGO_SETTINGS_MODULE'] = 'prop30.settings'

import django.core.handlers.wsgi

site_path = '/var/www/opinion.berkeley.edu/landing/ca-prop-30-awareness/'
opinion_path = '/var/www/opinion.berkeley.edu/landing/ca-prop-30-awareness/prop30/'
sys.path.append(site_path)
sys.path.append(opinion_path)

application = django.core.handlers.wsgi.WSGIHandler()
