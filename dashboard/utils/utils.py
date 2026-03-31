from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def get_period_range(period):
    now = timezone.now()
    start_date = None
    end_date = now  # By default, until today

    if period == "all_time":
        return None, None

    # If they don't give us a period, or they ask us for "this_year"
    if period is None or period == "this_year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)

    elif period == "last_month":
        # From day 1 to the last day of last month
        last_month = now - relativedelta(months=1)
        start_date = last_month.replace(day=1, hour=0, minute=0, second=0)
        # The `.replace()` method of a `datetime` object creates a new object identical to the original but with the fields you choose changed. It does not modify the original (dates in Python are immutable).
        end_date = start_date + relativedelta(months=1) - timedelta(seconds=1)

    elif period == "3_months":
        start_date = now - timedelta(days=90)

    elif period == "6_months":
        start_date = now - timedelta(days=180)

    elif period == "12_months":
        start_date = now - timedelta(days=365)

    elif period == "last_year":
        last_year = now.year - 1
        start_date = now.replace(year=last_year, month=1, day=1, hour=0, minute=0)
        end_date = now.replace(year=last_year, month=12, day=31, hour=23, minute=59)

    return start_date, end_date
