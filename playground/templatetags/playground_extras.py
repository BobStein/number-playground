import datetime

import six

import django.template

import qiki


register = django.template.Library()


ZERO_WIDTH_SPACE = u'\u200B'
EMPTY_BLING = ZERO_WIDTH_SPACE   # But nonzero height


# Obsolete?  Only used when "icon history" is enabled in qiki playground
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


@register.inclusion_tag('icon-diagram-call.html')
def icon_diagram(qoolified_verb, icon_entry, user_idn):
    """
    Draw an icon for a qool verb to appear next to its target.
    :param qoolified_verb: the verb that has been declared qool somewhere
           e.g. like=lex.verb(u'like'); lex.qool(like)
    :param icon_entry:  dictionary of info on usage of this verb, keyed by author.
    :param icon_entry[author]:  one author's involvement with this qool verb.
    :param icon_entry[author]['num']:  The author's latest magnitude for this verb.
    :param icon_entry[author]['history']:  List of words by this author on this qool verb.
    :param user_idn:  logged in (viewing) user
    :return:
    """
    assert isinstance(qoolified_verb, qiki.Word)
    assert isinstance(icon_entry, dict)
    assert isinstance(user_idn, qiki.Number)
    lex = qoolified_verb.lex
    iconify = lex(u'iconify')
    icon = lex.find_last(vrb=iconify, obj=qoolified_verb)
    # TODO:  icon = qoolified_verb.jbo(vrb=iconify)[-1]
    # TODO:  If NotFouind (i.e. not iconified) display some kind of gussied up name instead?

    icon_title = qoolified_verb.txt + ": "
    everybody_num = 0
    me_num = 0
    for author, author_entry in icon_entry.iteritems():
        assert isinstance(author, qiki.Word)
        assert isinstance(author_entry, dict)
        assert isinstance(author_entry['num'], qiki.Number)
        assert isinstance(author_entry['history'], list)
        author_num = int(author_entry['num'])   # TODO:  round(num,1)?  num.round(1)??  num.str(4) e.g. '4K'
        everybody_num += author_num
        if author.idn == user_idn:
            author_bling = " (me)"
            me_num = author_num
        else:
            author_bling = ""
        icon_title += "\n"
        icon_title += author.txt
        icon_title += author_bling
        icon_title += " "

        def rating_strings(uses):
            for use in uses:
                assert isinstance(use, qiki.Word)
                assert use.sbj == author
                assert use.vrb == qoolified_verb
                #      use.obj == the object of the qoolified verb, but icon_diagram is ignorant of that object
                yield str(int(use.num))

        icon_title += "-".join(rating_strings(author_entry['history']))

    if me_num == 0 and everybody_num == 0:
        return dict()

    return dict(
        icon_src=icon.txt,
        icon_title=icon_title,
        icon_sup=me_num if me_num not in (0,1) else EMPTY_BLING,
        icon_sub=everybody_num if everybody_num != me_num else EMPTY_BLING,
        me_nonzero='me-nonzero' if me_num != 0 else '',
        data_num=me_num,
        vrb_idn=qoolified_verb.idn,
    )



@register.inclusion_tag('word-diagram-call.html')
def word_diagram(word, show_idn=False, user_idn=None):
    """Render a word with its qool icon ratings.

    The word is expected to come out of lex.find_words() with the jbo_vrb set to a list of qool verbs.
    So the word has the wild and crazy jbo attribute.

    jbo_dict is a dictionary
    ------------------------
    It pre-processes the jbo attribute of the word.
    Tt breaks down the jbo container into a 2D dictionary
        first by icon (verb) and then by author (subject)
    The keys of the dictionary are themselves words
        the qool verb for the icon, DjangoUser() for the author.

    jbo_dict[icon]                     contains a dictionary, temporarily called icon_entry
    jbo_dict[icon][author]             contains a dictionary, temporarily called author_entry
    jbo_dict[icon][author]['history']  list of qool words in chronological order
                                       so this is a subset of jbo
    jbo_dict[icon][author]['num']      that author's latest num for that qool verb
                                       so same as jbo_dict[qool verb]['history'][-1].num
    """
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

    jbo_report = []
    jbo_dict = {}
    for q in word.jbo:
        author = q.sbj.txt
        jbo_report.append(author)
        try:
            icon_entry = jbo_dict[q.vrb]
        except KeyError:
            icon_entry = dict()
            jbo_dict[q.vrb.inchoate_copy()] = icon_entry
        try:
            author_entry = icon_entry[q.sbj]
        except KeyError:
            author_entry = {'history': []}
            icon_entry[q.sbj.inchoate_copy()] = author_entry
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
