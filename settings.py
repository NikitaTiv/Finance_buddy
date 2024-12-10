import os

from dotenv import load_dotenv


load_dotenv()

MAX_CATEGORY_PER_USER = int(os.environ.get('MAX_CATEGORY_PER_USER', 20))
MAX_CATEGORY_PER_PAGE = 10
SENTRY_TOKEN = os.environ.get('SENTRY_TOKEN')
