from calendar import monthrange, nextmonth
from datetime import datetime


def get_cur_next_month_days_amount():
    now = datetime.now()
    cur_month_days_amount = monthrange(now.year, now.month)[1]
    next_month_days_amount = monthrange(*nextmonth(now.year, now.month))[1]
    return cur_month_days_amount, next_month_days_amount


def cut_into_weeks(data):
    weeked_data = []
    while len(data) > 7:
        weeked_data.append(data[:7])
        data = data[7:]
    if weeked_data:
        weeked_data.append(data)
    return weeked_data
