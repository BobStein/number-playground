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
    obj_txt = obj.txt
    if obj_txt == '':
        obj_txt = "Word {}".format(render_num(obj.idn))
        # TODO:  This will have to be smarter.  Comment objects shouldn't be indentified by txt alone.  Arrows??
    return dict(
        show_idn=show_idn,
        idn=render_num(word.idn),
        idn_qstring=word.idn.qstring(underscore=1),
        sbj=sbj.txt,
        vrb=vrb.txt,
        obj=obj_txt,
        txt=word.txt,
        num=render_num(word.num),
        num_qstring=word.num.qstring(),
        is_a_what=is_a_what,
        yyyy_mmdd_hhmm_ss_mmm=time_code,
        sbj_idn=sbj.idn.qstring(),
        vrb_idn=vrb.idn.qstring(),
        obj_idn=obj.idn.qstring(),
    )

def render_num(num):
    if num.is_whole():
        return str(int(num))
    else:
        return str(float(num))
