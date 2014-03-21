import logging
import os
import platform
from fle_utils.settingshelper import import_installed_app_settings


##############################
# Functions for querying settings
##############################

def package_selected(package_name):
    global CONFIG_PACKAGE
    return bool(CONFIG_PACKAGE) and bool(package_name) and package_name.lower() in CONFIG_PACKAGE


##############################
# Basic setup
##############################

try:
    from local_settings import *
    import local_settings
except ImportError:
    local_settings = object()


# Used everywhere, so ... set it up top.
DEBUG          = getattr(local_settings, "DEBUG", False)

CENTRAL_SERVER = False  # Hopefully will be removed soon.


##############################
# Basic setup of logging
##############################

# Set logging level based on the value of DEBUG (evaluates to 0 if False, 1 if True)
LOGGING_LEVEL = getattr(local_settings, "LOGGING_LEVEL", logging.DEBUG if DEBUG else logging.INFO)
LOG = getattr(local_settings, "LOG", logging.getLogger("kalite"))
TEMPLATE_DEBUG = getattr(local_settings, "TEMPLATE_DEBUG", DEBUG)

logging.basicConfig()
LOG.setLevel(LOGGING_LEVEL)
logging.getLogger("requests").setLevel(logging.WARNING)  # shut up requests!


##############################
# Basic Django settings
##############################

# Not really a Django setting, but we treat it like one--it's eeeeverywhere.
PROJECT_PATH = os.path.realpath(getattr(local_settings, "PROJECT_PATH", os.path.dirname(os.path.realpath(__file__)))) + "/"
DATA_PATH = os.path.realpath(getattr(local_settings, "DATA_PATH", os.path.join(PROJECT_PATH, "..", "data"))) + "/"


LOCALE_PATHS   = getattr(local_settings, "LOCALE_PATHS", (PROJECT_PATH + "/../locale",))
LOCALE_PATHS   = tuple([os.path.realpath(lp) + "/" for lp in LOCALE_PATHS])

DATABASES      = getattr(local_settings, "DATABASES", {
    "default": {
        "ENGINE": getattr(local_settings, "DATABASE_TYPE", "django.db.backends.sqlite3"),
        "NAME"  : getattr(local_settings, "DATABASE_PATH", os.path.join(PROJECT_PATH, "database", "data.sqlite")),
        "OPTIONS": {
            "timeout": 60,
        },
    }
})

INTERNAL_IPS   = getattr(local_settings, "INTERNAL_IPS", ("127.0.0.1",))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE      = getattr(local_settings, "TIME_ZONE", None)
#USE_TZ         = True  # needed for timezone-aware datetimes (particularly in updates code)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE  = getattr(local_settings, "LANGUAGE_CODE", "en")

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N       = getattr(local_settings, "USE_I18N", True)

# If you set this to True, Django will format dates, numbers and
# calendars according to the current locale
USE_L10N       = getattr(local_settings, "USE_L10N", False)

MEDIA_URL      = getattr(local_settings, "MEDIA_URL", "/media/")
MEDIA_ROOT     = os.path.realpath(getattr(local_settings, "MEDIA_ROOT", PROJECT_PATH + "/media/")) + "/"
STATIC_URL     = getattr(local_settings, "STATIC_URL", "/static/")
STATIC_ROOT    = os.path.realpath(getattr(local_settings, "STATIC_ROOT", PROJECT_PATH + "/static/")) + "/"

 # Make this unique, and don't share it with anybody.
SECRET_KEY     = getattr(local_settings, "SECRET_KEY", "8qq-!fa$92i=s1gjjitd&%s@4%ka9lj+=@n7a&fzjpwu%3kd#u")

LANGUAGE_COOKIE_NAME    = "django_language"

ROOT_URLCONF = "distributed.urls"
INSTALLED_APPS = ("distributed",)
MIDDLEWARE_CLASSES = tuple()  # will be filled recursively via INSTALLED_APPS
TEMPLATE_DIRS  = tuple()  # will be filled recursively via INSTALLED_APPS
STATICFILES_DIRS = (os.path.join(PROJECT_PATH, '..', 'static'),)  # libraries common to all apps

DEFAULT_ENCODING = 'utf-8'

########################
# Storage and caching
########################

# Sessions use the default cache, and we want a local memory cache for that.
CACHES = {
    "default": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

<<<<<<< HEAD
# Local memory cache is to expensive to use for the page cache.
#   instead, use a file-based cache.
# By default, cache for maximum possible time.
#   Note: caching for 100 years can be too large a value
#   sys.maxint also can be too large (causes ValueError), since it's added to the current time.
#   Caching for the lesser of (100 years) or (5 years less than the max int) should work.
_5_years = 5 * 365 * 24 * 60 * 60
_100_years = 100 * 365 * 24 * 60 * 60
_max_cache_time = min(_100_years, sys.maxint - time.time() - _5_years)
CACHE_TIME = getattr(local_settings, "CACHE_TIME", _max_cache_time if not CENTRAL_SERVER else 0)
CACHE_NAME = getattr(local_settings, "CACHE_NAME", None)  # without a cache defined, None is fine

# Cache is activated in every case,
#   EXCEPT: if CACHE_TIME=0
if CACHE_TIME != 0:  # None can mean infinite caching to some functions
    KEY_PREFIX = version.VERSION_INFO[version.VERSION]["git_commit"][0:6]  # new cache for every build

    # File-based cache
    install_location_hash = hashlib.sha1(PROJECT_PATH).hexdigest()
    username = getpass.getuser() or "unknown_user"
    cache_dir_name = "kalite_web_cache_%s" % (username)
    CACHE_LOCATION = os.path.realpath(getattr(local_settings, "CACHE_LOCATION", os.path.join(tempfile.gettempdir(), cache_dir_name, install_location_hash))) + "/"
    CACHES["file_based_cache"] = {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_LOCATION, # this is kind of OS-specific, so dangerous.
        'TIMEOUT': CACHE_TIME, # should be consistent
        'OPTIONS': {
            'MAX_ENTRIES': getattr(local_settings, "CACHE_MAX_ENTRIES", 5*2000) #2000 entries=~10,000 files
        },
    }

    # Memory-based cache
    CACHES["mem_cache"] = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': CACHE_TIME, # should be consistent
        'OPTIONS': {
            'MAX_ENTRIES': getattr(local_settings, "CACHE_MAX_ENTRIES", 5*2000) #2000 entries=~10,000 files
        },
    }

    # The chosen cache
    CACHE_NAME = getattr(local_settings, "CACHE_NAME", "file_based_cache")
    if CACHE_NAME == "file_based_cache":
        LOG.debug("Cache location = %s" % CACHE_LOCATION)
    else:
        LOG.debug("Using %s caching" % CACHE_NAME)


########################
# Features
########################


if CENTRAL_SERVER:
    # Used for accessing the KA API.
    #   By default, things won't work--local_settings needs to specify good values.
    #   We do this so that we have control over our own key/secret (secretly, of course!)
    KHAN_API_CONSUMER_KEY = getattr(local_settings, "KHAN_API_CONSUMER_KEY", "")
    KHAN_API_CONSUMER_SECRET = getattr(local_settings, "KHAN_API_CONSUMER_SECRET", "")

    # Postmark settings, to enable sending registration/invitation emails
    POSTMARK_API_KEY = getattr(local_settings, "POSTMARK_API_KEY", "")
    POSTMARK_SENDER = getattr(local_settings, "POSTMARK_SENDER", CENTRAL_FROM_EMAIL)
    # Default to "test mode" if no API key, to print out the email to the console, rather than trying to send
    POSTMARK_TEST_MODE = getattr(local_settings, "POSTMARK_TEST_MODE", POSTMARK_API_KEY == "")

    # Used for redirecting to the actual installer executables
    INSTALLER_BASE_URL = getattr(local_settings, 'INSTALLER_BASE_URL', 'http://adhoc.learningequality.org:7007/media/installer/')

else:
    # enable this to use a background mplayer instance instead of playing the video in the browser, on loopback connections
    # TODO(jamalex): this will currently only work when caching is disabled, as the conditional logic is in the Django template
    USE_MPLAYER = getattr(local_settings, "USE_MPLAYER", False) if CACHE_TIME == 0 else False

    # Clock Setting disabled by default unless overriden.
    # Note: This will only work on Linux systems where the server is running as root.
    ENABLE_CLOCK_SET = False


# This has to be defined for main and central
# Should be a function that receives a video file (youtube ID), and returns a URL to a video stream
BACKUP_VIDEO_SOURCE = getattr(local_settings, "BACKUP_VIDEO_SOURCE", None)
BACKUP_THUMBNAIL_SOURCE = getattr(local_settings, "BACKUP_THUMBNAIL_SOURCE", None)
assert not BACKUP_VIDEO_SOURCE or CACHE_TIME == 0, "If BACKUP_VIDEO_SOURCE, then CACHE_TIME must be 0"


########################
# Debugging and testing
########################

# Django debug_toolbar config
if getattr(local_settings, "USE_DEBUG_TOOLBAR", False):
    assert CACHE_TIME == 0, "Debug toolbar must be set in conjunction with CACHE_TIME=0"
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'HIDE_DJANGO_SQL': False,
        'ENABLE_STACKTRACES' : True,
    }

if DEBUG:
    # add ?prof to URL, to see performance stats
    MIDDLEWARE_CLASSES += ('django_snippets.profiling_middleware.ProfileMiddleware',)

if not CENTRAL_SERVER and os.path.exists(PROJECT_PATH + "/testing/loadtesting/"):
        INSTALLED_APPS += ("testing.loadtesting",)

TEST_RUNNER = 'kalite.testing.testrunner.KALiteTestRunner'

TESTS_TO_SKIP = getattr(local_settings, "TESTS_TO_SKIP", ["long"])  # can be
assert not (set(TESTS_TO_SKIP) - set(["fast", "medium", "long"])), "TESTS_TO_SKIP must contain only 'fast', 'medium', and 'long'"
=======
# Separate session caching from file caching.
SESSION_ENGINE = getattr(local_settings, "SESSION_ENGINE", 'django.contrib.sessions.backends.cache' + (''))
>>>>>>> 893a82a4b5b75a35c54c06ccd9afcac7e35c4607

# Use our custom message storage to avoid adding duplicate messages
MESSAGE_STORAGE = 'fle_utils.django_utils.NoDuplicateMessagesSessionStorage'



########################
# After all settings, but before config packages,
#   import settings from other apps.
#
# This allows app-specific settings to be localized and augment
#   the settings here, while also allowing
#   config packages to override settings.
########################

import_installed_app_settings(INSTALLED_APPS, globals())


########################
# IMPORTANT: Do not add new settings below this line
#
# Everything that follows is overriding default settings, depending on CONFIG_PACKAGE

# config_package (None|RPi) alters some defaults e.g. different defaults for Raspberry Pi(RPi)
# autodetect if this is a Raspberry Pi-type device, and auto-set the config_package
#  to override the auto-detection, set CONFIG_PACKAGE=None in the local_settings
########################

CONFIG_PACKAGE = getattr(local_settings, "CONFIG_PACKAGE", "RPi" if (platform.uname()[0] == "Linux" and platform.uname()[4] == "armv6l") else [])

if isinstance(CONFIG_PACKAGE, basestring):
    CONFIG_PACKAGE = [CONFIG_PACKAGE]
CONFIG_PACKAGE = [cp.lower() for cp in CONFIG_PACKAGE]


# Config for Raspberry Pi distributed server
if package_selected("RPi"):
    logging.info("RPi package selected.")
    # nginx proxy will normally be on 8008 and production port on 7007
    # If ports are overridden in local_settings, run the optimizerpi script
    PRODUCTION_PORT = getattr(local_settings, "PRODUCTION_PORT", 7007)
    PROXY_PORT = getattr(local_settings, "PROXY_PORT", 8008)
    assert PRODUCTION_PORT != PROXY_PORT, "PRODUCTION_PORT and PROXY_PORT must not be the same"
    #SYNCING_THROTTLE_WAIT_TIME = getattr(local_settings, "SYNCING_THROTTLE_WAIT_TIME", 1.0)
    #SYNCING_MAX_RECORDS_PER_REQUEST = getattr(local_settings, "SYNCING_MAX_RECORDS_PER_REQUEST", 10)

    PASSWORD_ITERATIONS_TEACHER = getattr(local_settings, "PASSWORD_ITERATIONS_TEACHER", 2000)
    PASSWORD_ITERATIONS_STUDENT = getattr(local_settings, "PASSWORD_ITERATIONS_STUDENT", 500)

    ENABLE_CLOCK_SET = getattr(local_settings, "ENABLE_CLOCK_SET", True)


if package_selected("UserRestricted"):
    LOG.info("UserRestricted package selected.")

    if CACHE_TIME != 0 and not hasattr(local_settings, KEY_PREFIX):
        KEY_PREFIX += "|restricted"  # this option changes templates


if package_selected("Demo"):
    LOG.info("Demo package selected.")

    CENTRAL_SERVER_HOST = getattr(local_settings, "CENTRAL_SERVER_HOST",   "globe.learningequality.org:8008")
    SECURESYNC_PROTOCOL = "http"
    DEMO_ADMIN_USERNAME = getattr(local_settings, "DEMO_ADMIN_USERNAME", "admin")
    DEMO_ADMIN_PASSWORD = getattr(local_settings, "DEMO_ADMIN_PASSWORD", "pass")

    MIDDLEWARE_CLASSES += ('distributed.demo_middleware.StopAdminAccess','distributed.demo_middleware.LinkUserManual','distributed.demo_middleware.ShowAdminLogin',)
