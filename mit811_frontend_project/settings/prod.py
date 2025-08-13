from .base import *

DEBUG = False
ALLOWED_HOSTS = ["bookhive.us", "www.bookhive.us"]

# this is the path to the static folder where css, js and images are stored
STATIC_DIR = BASE_DIR / '/home/speebndt/bookhive_frontend/static/'
# path to the media folder 
MEDIA_ROOT = BASE_DIR / '/home/speebndt/bookhive.us/media/'

STATIC_URL = 'static/'
STATIC_ROOT = '/home/speebndt/bookhive.us/static/'
MEDIA_URL = 'https://bookhive.us/media/'

STATICFILES_DIRS = [
    STATIC_DIR,
]