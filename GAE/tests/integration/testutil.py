
from datetime import datetime, timedelta

def next_monday_date_string():
	today = datetime.today()
	# monday is 0
	# TODO make this generic for any day of the week
	next_monday = today + timedelta(days=-today.weekday(), weeks=1)
	next_monday_string = datetime.strftime(next_monday, "%Y-%m-%d")
	return next_monday_string