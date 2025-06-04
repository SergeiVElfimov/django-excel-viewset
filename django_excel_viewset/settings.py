import pytz
from environs import Env

env = Env()
env.read_env(override=True)

DJANGO_EXCEL_VIEWSET_LOCAL_TIMEZONE = env.str("DJANGO_EXCEL_VIEWSET_LOCAL_TIMEZONE", "Europe/Moscow")
LOCAL_TIMEZONE = pytz.timezone(DJANGO_EXCEL_VIEWSET_LOCAL_TIMEZONE)
