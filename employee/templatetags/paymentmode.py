from django import template

register = template.Library()

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

@register.filter
def paymentmode(value):
    try:
        if not value:
            value=0
        payment = human_format(float(value))
        return payment
    except Exception :
        payment = 0


@register.filter(name='times') 
def times(number):
    return range(1,number+1)