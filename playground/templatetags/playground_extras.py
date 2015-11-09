import datetime

import django


register = django.template.Library()


@register.inclusion_tag('word-diagram-call.html')
def word_diagram(word, show_idn=False):
    sbj = word.spawn(word.sbj)
    vrb = word.spawn(word.vrb)
    obj = word.spawn(word.obj)
    if word.is_defined():
        if word.is_a_verb():
            is_a_what = "verb"
        elif word.is_a_noun():
            is_a_what = "noun"
        else:
            is_a_what = "nothing"
    else:
        is_a_what = "else"
    datetime_object = datetime.datetime.fromtimestamp(float(word.whn))
    time_code = datetime_object.strftime("%Y.%m%d.%H%M.%S.%f")[:-3]
    return dict(
        show_idn=show_idn,
        idn=render_num(word.idn),
        sbj=sbj.txt,
        vrb=vrb.txt,
        obj=obj.txt,
        txt=word.txt,
        num=render_num(word.num),
        is_a_what=is_a_what,
        yyyy_mmdd_hhmm_ss_mmm=time_code,
    )

def render_num(num):
    if num.is_whole():
        return str(int(num))
    else:
        return str(float(num))
