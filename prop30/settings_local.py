import os

#This flag allows debug messages to be output as the HTTP response if there is an error
DEBUG = True
TEMPLATE_DEBUG = DEBUG

#Tuple of admins for this site
ADMINS = (
     ('Sanjay Krishnan', 'sanjaykrishnan@berkeley.edu'),
)

#sets the url root for the site, this makes sure all the paths/stylesheets/scripts work
URL_ROOT='http://opinion.berkeley.edu/ca-prop-30-awareness/'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'y*wkv+^lamxfu577jyj6b@ijrugjz@8xl0zdk&+o8g2p63)f5w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'prop30.urls'

TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'prop30',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#Destroy the cookie after browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

"""
Algorithm parameters
"""
PARENT_CHILD_DECAY_RATE = 2 #parent gets 1/rate points from child
PROPAGATION_LIMIT = 10 #to ensure constant time updates we propagate points back only to this limit 

"""
Score display parameters
"""
MAX_CHILD_LEVELS = 5

"""
Use Re-Captcha
"""
USE_RECAPTCHA = False
RECAPTCHA_PUBLIC_KEY = '6LdQN9YSAAAAAL96sFwlNHo77Lx1pPDF4jdxXAWh'
RECAPTCHA_PRIVATE_KEY = '6LdQN9YSAAAAAEldH_ZoQGcrW4EYv5u5cwU2gDbI'

