LOCAL_SETTINGS = True
from settings import *


# Choose your database and fill in the details below. If testing, you
# can use the sqlite3 database as it doesn't require any further configuration
# A Windows example path might be: 'C:/Users/myusername/Documents/OpenREM/openrem.db'
# Note, forward slashes are used in the config files, even for Windows.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/home/mcdonaghe/research/testChangeName/db/openrem.db', # Or path to database file if using sqlite3.
        'USER': '',                              # Not used with sqlite3.
        'PASSWORD': '',                          # Not used with sqlite3.
        'HOST': '',                              # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                              # Set to empty string for default. Not used with sqlite3.
    }
}


# Absolute filesystem path to the directory that will hold xlsx and csv
# exports patient size import files
# Linux example: "/var/openrem/media/"
# Windows example: "C:/Users/myusername/Documents/OpenREM/media/"
MEDIA_ROOT = '/home/mcdonaghe/research/testChangeName/media'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# You should generate a new secret key. Make this unique, and don't
# share it with anybody. See the docs.
SECRET_KEY = 'hmj#)-$smzqk*=wuz9^a46rex30^$_j$rghp+1#y&amp;i+pys5b@$'

# Debug mode is now set to False by default. If you need to troubleshoot, can turn it back on here:
# DEBUG = True

# Set the domain name that people will use to access your OpenREM server.
# This is required if the DEBUG mode is set to False (default)
# Example: '.doseserver.' or '10.23.123.123'. A dot before a name allows subdomains, a dot after allows for FQDN eg doseserver.ad.trust.nhs.uk
ALLOWED_HOSTS = [
    '192.168.56.102',
]
