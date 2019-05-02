import calendar
from datetime import datetime


def get_cur_month_days_amount(is_next_month=False):
    now = datetime.now()
    if is_next_month:
        month_days_amount = calendar.monthrange(*calendar.nextmonth(now.year, now.month))[1]
    else:
        month_days_amount = calendar.monthrange(now.year, now.month)[1]
    return month_days_amount


def cut_into_weeks(data):
    weeked_data = []
    while len(data) > 7:
        weeked_data.append(data[:7])
        data = data[7:]
    if weeked_data:
        weeked_data.append(data)
    return weeked_data
