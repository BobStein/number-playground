import datetime

import six

import django.template


register = django.template.Library()


@register.inclusion_tag('jbo-diagram-call.html')
def jbo_diagram(x):
    lex = x.lex
    iconify = lex(u'iconify')
    icons = lex.find_words(vrb=iconify, obj=x.vrb)
    # TODO:  Limit find_words to latest iconify using sql.
    icon = icons[-1]
    sbj = x.spawn(x.sbj)
    return dict(
        icon_src=icon.txt,
        num_if_not_one=str(int(x.num)) if x.num != 1 else '',
        sbj_txt=sbj.txt
    )

@register.inclusion_tag('icon-diagram-call.html')
def icon_diagram(vrb, icon_entry):
    lex = icon_entry['lex']
    iconify = lex(u'iconify')
    icons = lex.find_words(vrb=iconify, obj=vrb)
    # TODO:  Limit find_words to latest iconify using sql.
    icon = icons[-1]
    icon_title = lex(vrb).txt + ": "
    icon_sup = 0
    for author_idn, author_entry in icon_entry.iteritems():
        if isinstance(author_idn, six.string_types):
            pass
        else:
            icon_sup += int(author_entry['num'])
            icon_title += "\n"
            icon_title += lex(author_idn).txt + " "
            icon_title += "-".join([str(int(w.num)) for w in author_entry['history']])
    return dict(
        icon_src=icon.txt,
        icon_title=icon_title,
        icon_sup=icon_sup,
        icon_sub='&nbsp;',
    )


# jbo_dict is a dictionary
# jbo_dict[idn of a qool verb] contains a dictionary, temporarily called icon_entry
#     [sbj in a qool sentence] contains a dictionary, temporarily called author_entry
#         ['history'] == list of qool words in chronological order
#         ['num'] == that author's latest num for that qool verb
#

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

    lex = word.lex
    jbo_report = []
    jbo_dict = {}
    for q in word.jbo:
        author = lex(q.sbj).txt
        jbo_report.append(author)
        try:
            icon_entry = jbo_dict[q.vrb]
        except KeyError:
            icon_entry = {'lex': lex}
            jbo_dict[q.vrb] = icon_entry
        try:
            author_entry = icon_entry[q.sbj]
        except KeyError:
            author_entry = {'history': []}
            icon_entry[q.sbj] = author_entry
        author_entry['history'].append(q)
        author_entry['num'] = q.num
    obj_txt = obj.txt
    if obj_txt == '':
        obj_txt = "Word {}".format(render_num(obj.idn))
        # TODO:  This will have to be smarter.  Comment objects shouldn't be identified by txt alone.  Arrows??
    return dict(
        show_idn=show_idn,
        idn=render_num(word.idn),
        idn_qstring=word.idn.qstring(underscore=1),
        sbj_txt=sbj.txt,
        vrb_txt=vrb.txt,
        obj_txt=obj_txt,
        txt=word.txt,
        num=render_num(word.num),
        num_qstring=word.num.qstring(),
        is_a_what=is_a_what,
        yyyy_mmdd_hhmm_ss_mmm=time_code,
        sbj_idn=sbj.idn.qstring(),
        vrb_idn=vrb.idn.qstring(),
        obj_idn=obj.idn.qstring(),
        jbo=word.jbo,
        jbo_report=jbo_report,
        jbo_dict=jbo_dict,
    )

def render_num(num):
    if num.is_whole():
        return str(int(num))
    else:
        return str(float(num))
