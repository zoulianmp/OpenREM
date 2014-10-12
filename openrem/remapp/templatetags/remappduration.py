from django import template
from datetime import datetime

register = template.Library()

def naturalduration(seconds):
    if not seconds:
        return ''

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    
    hplural = ''
    mplural = ''
    splural = ''
    
    if not h == 1:
        hplural = 's'
    if not m == 1:
        mplural = 's'
    if not s == 1:
        splural = 's'


    if h:
        duration = "{0:.0f} hour{1} and {2:.0f} minute{3}".format(h, hplural, m, mplural) 
    elif m:
        duration = "{0:.0f} minute{1} and {2:.0f} second{3}".format(m, mplural, s, splural)
    else:
        duration = "{0:.1f} second{1}".format(s, splural)

    return duration

register.filter('naturalduration',naturalduration)
