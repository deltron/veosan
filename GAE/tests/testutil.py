
from datetime import datetime, timedelta


MONDAY = 0
TUESDAY = 1

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


def next_weekday_date_string(weekday):
	today = datetime.today()
	today_weekday = today.weekday()
	if weekday > today_weekday:
		day_delta =  weekday - today_weekday
	else:
		day_delta = 7 +  weekday - today_weekday
	next_day_of_the_week = today + timedelta(days=day_delta)
	next_day_string = datetime.strftime(next_day_of_the_week, "%Y-%m-%d")
	return next_day_string

