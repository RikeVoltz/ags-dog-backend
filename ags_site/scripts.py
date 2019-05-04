from calendar import monthrange
from datetime import datetime

from django.core.mail import send_mail


def nextmonth(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


def get_cur_month_days_amount(is_next_month=False):
    now = datetime.now()
    if is_next_month:
        month_days_amount = monthrange(*nextmonth(now.year, now.month))[1]
    else:
        month_days_amount = monthrange(now.year, now.month)[1]
    return month_days_amount


def cut_into_weeks(data):
    weeked_data = []
    while len(data) > 7:
        weeked_data.append(data[:7])
        data = data[7:]
    if weeked_data:
        weeked_data.append(data)
    return weeked_data


def send_message_to_email(data):
    subject = 'Новое обращение через форму на сайте agsdog.ru от ' + data['name']
    message = 'Имя пользователя: {name} Email пользователя: {email} {message}'.format(
        name=data['name'], email=data['email'], message=data['message'])
    html_message = '<p>Имя пользователя: {name}</p><p>Email пользователя: {email}</p><p>{message}</p>'.format(
        name=data['name'], email=data['email'], message=data['message'])
    send_mail(subject, message=message, from_email='admin@agsdog.ru', html_message=html_message,
              recipient_list=['rikevoltz@gmail.com'], fail_silently=False)
