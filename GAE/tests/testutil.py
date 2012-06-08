
from datetime import datetime, timedelta


def create_datetime_from_weekday_and_hour(day=0, hour=9):
	today = datetime.today()
	day_diff = day - today.weekday()
	nd = today + timedelta(days=day_diff, weeks=1)
	next_weekday_at_hour = datetime(nd.year, nd.month, nd.day, hour)
	return next_weekday_at_hour


def next_monday_date_string():
	today = datetime.today()
	# monday is 0
	# TODO make this generic for any day of the week
	next_monday = today + timedelta(days=-today.weekday(), weeks=1)
	next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
	return next_monday_string