import datetime

import six

import django.template


register = django.template.Library()


# Obsolete?
@register.inclusion_tag('jbo-diagram-call.html')
def jbo_diagram(x):
    lex = x.lex
    iconify = lex(u'iconify')
    icons = lex.find_words(vrb=iconify, obj=x.vrb)
    # TODO:  Limit find_words to latest iconification sentence using sql.
    icon = icons[-1]
    sbj = x.spawn(x.sbj)
    return dict(
        icon_src=icon.txt,
        num_if_not_one=str(int(x.num)) if x.num != 1 else '',
        sbj_txt=sbj.txt
    )

ZERO_WIDTH_SPACE = u'\u200B'
EMPTY_BLING = ZERO_WIDTH_SPACE   # But nonzero height

@register.inclusion_tag('icon-diagram-call.html')
def icon_diagram(vrb, icon_entry, user_idn):
    lex = icon_entry['lex']
    iconify = lex(u'iconify')
    icons = lex.find_words(vrb=iconify, obj=vrb)
    # TODO:  Limit find_words to latest iconify using sql.
    icon = icons[-1]
    icon_title = lex(vrb).txt + ": "
    everybodys_num = 0
    my_num = 0
    for author_idn, author_entry in icon_entry.iteritems():
        if isinstance(author_idn, six.string_types):
            pass
        else:
            this_guys_num =  int(author_entry['num'])
            everybodys_num += this_guys_num
            if author_idn.idn == user_idn:
                # TODO:  Whoa, why is author_idn a word!?
                author_bling = "*"
                my_num = this_guys_num
            else:
                author_bling = ""
            icon_title += "\n"
            icon_title += lex(author_idn).txt
            icon_title += author_bling
            icon_title += " "
            icon_title += "-".join([str(int(w.num)) for w in author_entry['history']])
    return dict(
        icon_src=icon.txt,
        icon_title=icon_title,
        icon_sup=my_num if my_num != 0 else EMPTY_BLING,
        icon_sub=everybodys_num if everybodys_num != my_num else EMPTY_BLING,
        user_idn=user_idn,
        me_nonzero='me-nonzero' if my_num != 0 else '',
        data_num=my_num,
        vrb_idn=vrb.idn,
    )


# jbo_dict is a dictionary
# jbo_dict[a qool verb -- the word itself] contains a dictionary, temporarily called icon_entry
#     [sbj in a qool sentence] contains a dictionary, temporarily called author_entry
#         ['history'] == list of qool words in chronological order
#         ['num'] == that author's latest num for that qool verb
#

@register.inclusion_tag('word-diagram-call.html')
def word_diagram(word, show_idn=False, user_idn=None):
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
    obj_txt = word.obj.txt
    if obj_txt == '':
        obj_txt = "Word {}".format(render_num(word.obj.idn))
        # TODO:  This will have to be smarter.  Comment objects shouldn't be identified by txt alone.  Arrows??
    return dict(
        word=word,
        show_idn=show_idn,
        idn=render_num(word.idn),
        idn_qstring=word.idn.qstring(underscore=1),
        me_sbj='me-sbj' if user_idn == word.sbj.idn else '',
        sbj_idn=word.sbj.idn.qstring(),
        vrb_idn=word.vrb.idn.qstring(),
        vrb_txt=word.vrb.txt,
        obj_idn=word.obj.idn.qstring(),
        obj_txt=obj_txt,
        txt=word.txt,
        num=render_num(word.num),
        num_qstring=word.num.qstring(),
        is_a_what=is_a_what,
        yyyy_mmdd_hhmm_ss_mmm=time_code,
        jbo=word.jbo,
        jbo_report=jbo_report,
        jbo_dict=jbo_dict,
        user_idn=user_idn,
    )

def render_num(num):
    if num.is_whole():
        return str(int(num))
    else:
        return str(float(num))
