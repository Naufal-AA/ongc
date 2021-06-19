from django import template
import os
from os.path import dirname, join
import timeago, datetime
from django.utils import timezone

register = template.Library()

@register.filter
def to_newline(value):
    return value.replace(",","\n")

@register.filter(name='times') 
def times(number):
    return range(1,number+1)

@register.filter
def to_filename(value):
    file = os.path.basename(value)
    return file[:-4]

@register.filter
def ago(value):
    #mydate = value.strftime("%Y/%d/%m %H:%M:%S")	
    #now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)
    now = timezone.now()
    mydate = value
    ago = timeago.format(mydate, now)
    return ago

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

@register.filter
def paymentmode(value):
    payment = human_format(float(value))
    return payment
