from __future__ import print_function
import datetime
import json
import re
import sys

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound
import django.shortcuts
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
logger = logging.getLogger(__name__)
logger.info("{now}".format(now=datetime.datetime.now().strftime("%Y.%m%d.%H%M.%S")))
# FIXME:  Timestamp in the log.  (effing django)

import templatetags.playground_extras

import qiki
try:
    import secure.credentials
    # noinspection PyStatementEffect
    secure.credentials.for_playground_database
except (ImportError, AttributeError) as import_or_attribute_error:
    if isinstance(import_or_attribute_error, AttributeError):
        try:
            # noinspection PyUnboundLocalVariable
            wrong_variable = [m for m in dir(secure.credentials) if m[:2] != '__'][0]
        except KeyError:
            print("Missing secure/credentials.py?")
        else:
            print(
                "Wrong secure/credentials.py?  "
                "It should define for_playground_database. "
                "(Instead it defines {}.)".format(wrong_variable)
            )
    secure = None
    print("""
        Example secure/credentials.py

            for_playground_database = dict(
                language= 'MySQL',
                host=     'localhost',
                port=     8000,
                user=     'user',
                password= 'password',
                database= 'database',
                table=    'word',
            )

        You also need an empty secure/__init__.py
    """)
    logger.exception(import_or_attribute_error)
    sys.exit(1)


@ensure_csrf_cookie
def number_playground(request):
    return django.shortcuts.render(request, 'number-playground.html')

    # return render_to_response('playground.html', {}, context_instance=RequestContext(request))

    # return render_to_response('playground.html')  #, {'aaa': ({'qstring':str(qiki.Number(x/256.0)), 'float':x/256.0} for x in range(-65536-256*10,65536+256*10+1))})

    # t = loader.get_template('playground.html')
    # c = RequestContext(request)
    # return HttpResponse(t.render(c))


class NumberPlaygroundForm(forms.Form):
    action  = forms.CharField(required=False)
    qstring = forms.CharField(required=False)
    floater = forms.CharField(required=False)


def number_playground_submission(request):
    if request.method == 'POST':
        form = NumberPlaygroundForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'qstring_to_float':
                try:
                    number_from_qstring = qiki.Number(form.cleaned_data['qstring'])
                    floater = str(float(number_from_qstring))
                except Exception as e:
                    return invalid_response(str(e))
                else:
                    return valid_response('floater', floater)
            elif action == 'float_to_qstring':
                try:
                    floating_point_typed = float(form.cleaned_data['floater'])
                except Exception as e:
                    float_error = str(e)
                    try:
                        integer_typed = int(form.cleaned_data['floater'], 0)
                    except Exception as e:
                        int_error = str(e)
                        # TODO: support q-string by trying qiki.Number(floater) ?
                        return invalid_response("Either %s, or %s" % (float_error, int_error))
                    else:
                        qstring = qiki.Number(integer_typed).qstring()
                        return valid_response('qstring', qstring)
                else:
                    qstring = qiki.Number(floating_point_typed, qigits=7).qstring()
                    # XXX:  Why qigits=7 here?  The negative round-off bug?  To examine it??
                    return valid_response('qstring', qstring)
            else:
                r = HttpResponse()
                r.status_code = 404
                r.reason_phrase = "Action '%s' not supported" % action
                return r
        else:
            return HttpResponse('whoa %s' % repr(form.errors))
    else:
        return HttpResponse('Oops, this is a POST-only URL.')


def strip_response_empty_html_comments(response):
    response.content = strip_empty_html_comments(response.content)
    return response


def strip_empty_html_comments(html):
    return re.sub(r'<!--[ \r\n\t]*-->', '', html)


# @strip_empty_html_comments
@login_required
def qiki_playground(request):
    if request.user.is_anonymous():
        return "Log in"
    else:
        qool = lex.verb(u'qool')
        qool_declarations = lex.find_words(vrb=qool.idn)
        qool_idns = {w.obj for w in qool_declarations}
        words = lex.find_words(jbo_vrb=qool_idns)
        for word in words:
            word.vrb_is_qool = u'vrb-is-qool' if word.vrb in qool_idns else u''
        return strip_response_empty_html_comments(django.shortcuts.render(
            request,
            'qiki-playground.html',
            {
                'user_id': request.user.id,
                'user_name': request.user.username,
                'user_email': request.user.email,
                'words': words,
                'user_idn': DjangoUser(qiki.Number(request.user.id)).idn
            }
        ))


class DjangoUser(qiki.Listing):
    def lookup(self, index, callback):
        try:
            user_name = User.objects.get(id=int(index)).username
            # THANKS: http://stackoverflow.com/a/2568955/673991
        except User.DoesNotExist:
            raise self.NotFound
        callback(user_name, qiki.Number(1))


lex = qiki.LexMySQL(**secure.credentials.for_playground_database)
listing = lex.noun(u'listing')
# qiki.Listing.install(listing)   # No need to do this, right?
django_user = lex.define(listing, u'django_user')
DjangoUser.install(django_user)
qoolbar = qiki.QoolbarSimple(lex)


# def install_qoolbar_verbs():
#     qool = lex.verb(u'qool')
#     iconify = lex.verb(u'iconify')
#
#     # def icon(name, width, url):
#     #     qool_verb = lex.verb(name)
#     #     # lex.says(qool, qool_verb, 1, use_already=True)
#     #     # lex.says(iconify, qool_verb, width, url, use_already=True)
#     #     lex(qool, use_already=True)[qool_verb] = 1
#     #     lex(iconify, use_already=True)[qool_verb] = width, url
#     #
#     # icon(u'like', 16, u'http://tool.qiki.info/icon/thumbsup_16.png')
#     # icon(u'delete', 16, u'http://tool.qiki.info/icon/delete_16.png')
#
#
#     like = lex.verb(u'like')
#     lex(qool, use_already=True)[like] = 1
#     lex(iconify, use_already=True)[like] = 16, u'http://tool.qiki.info/icon/thumbsup_16.png'
#
#     delete = lex.verb(u'delete')
#     lex(qool, use_already=True)[delete] = 1
#     lex(iconify, use_already=True)[delete] = 16, u'http://tool.qiki.info/icon/delete_16.png'
#
#
# install_qoolbar_verbs()


class QikiActionForm(forms.Form):
    action  = forms.CharField(required=True)
    comment = forms.CharField(required=False)


class QikiActionSentenceForm(QikiActionForm):
    vrb_idn = forms.CharField(required=False)
    vrb_txt = forms.CharField(required=False)
    obj_idn = forms.CharField(required=True)
    num = forms.CharField(required=False, initial='1')
    num_add = forms.CharField(required=False, initial='0')
    txt = forms.CharField(required=False)

# @strip_empty_html_comments
@login_required
def qiki_ajax(request):
    if request.user.is_anonymous():
        return HttpResponse("Log in")
    else:
        if request.method == 'POST':
            form = QikiActionForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data['action']
                if action == 'qiki_list':
                    idns = lex.get_all_idns()
                    report=""
                    for idn in idns:
                        word = lex[idn]
                        report += str(int(idn)) + " " + word.description()
                        report += "\n"
                    return valid_response('report', report)
                elif action == 'qoolbar_list':
                    return valid_response('verbs', list(qoolbar.get_verb_dicts()))

                    # verbs = qoolbar.get_verbs()
                    # # TODO:  Make Word json serializable, http://stackoverflow.com/a/3768975/673991
                    # # Then we wouldn't have to translate verbs to verb_dicts:
                    # verb_dicts = []
                    # for verb in verbs:
                    #     verb_dicts.append(dict(
                    #         idn=verb.idn.qstring(),
                    #         name=verb.txt,
                    #         icon_url=verb.icon_url
                    #     ))
                    # return valid_response('verbs', verb_dicts)

                    # Used by:
                    #     number_playground/playground/static/qoolbar.js
                    #     number_playground/playground/templatetags/playground_extras.py ?

                    # iconify = lex[u'iconify']
                    # qool_verbs = lex.find_words(vrb=lex[u'define'], obj=lex[u'qool'])
                    # report = ""
                    # verbs = []
                    # for qool_verb in qool_verbs:
                    #     icons = lex.find_words(vrb=iconify, obj=qool_verb)
                    #     # TODO:  Limit find_words to latest iconify using sql.
                    #     icon = icons[-1]
                    #     report += """
                    #         {number}. <img src="{url}"> {name}<br>
                    #     """.format(
                    #         number=str(int(icon.idn)),
                    #         url=icon.txt,
                    #         name=qool_verb.txt,
                    #     )
                    #     verbs.append(dict(
                    #         idn=qool_verb.idn.qstring(),
                    #         icon_url=icon.txt,
                    #         name=qool_verb.txt,
                    #     ))
                    # return valid_responses(dict(
                    #     report=report,
                    #     verbs=verbs,
                    # ))

                elif action == 'sentence':
                    sentence_form = QikiActionSentenceForm(request.POST)
                    me = DjangoUser(qiki.Number(request.user.id))
                    if sentence_form.is_valid():

                        vrb_txt = sentence_form.cleaned_data['vrb_txt']
                        vrb_idn = sentence_form.cleaned_data['vrb_idn']
                        if vrb_idn != '':
                            try:
                                vrb = lex[qiki.Number.from_qstring(vrb_idn)]
                            except ValueError:
                                return invalid_response("Verb idn {} is not valid.".format(vrb_idn))
                            if not vrb.exists():
                                return invalid_response("Verb idn {} does not exist".format(vrb_idn))
                        elif vrb_txt != '':
                            vrb = lex[vrb_txt]
                            if not vrb.exists():
                                return invalid_response("Verb txt '{}' does not exist".format(vrb_txt))
                        else:
                            return invalid_response("Neither verb idn nor txt specified.")
                        if not vrb.is_a_verb():
                            return invalid_response("Verb {} is not a verb.".format(repr(vrb)))

                        obj_idn = qiki.Number(sentence_form.cleaned_data['obj_idn'])

                        num_field     = sentence_form.cleaned_data.get('num',     None)
                        num_add_field = sentence_form.cleaned_data.get('num_add', None)
                        try:
                            num     = None if num_field     == '' else qiki.Number(num_field)
                            num_add = None if num_add_field == '' else qiki.Number(num_add_field)
                        except qiki.Number.ConstructorValueError as e:
                            return invalid_response(
                                "Invalid num ({num}) or num_add ({num_add}):  {message}.".format(
                                    num=num_field,
                                    num_add=num_add_field,
                                    message=str(e),
                                )
                            )
                        if num is None and num_add is None:
                            return invalid_response("Both num and num_add are empty.")

                        txt = sentence_form.cleaned_data.get('txt', '')

                        obj=lex[obj_idn]
                        if not obj.exists():
                            return invalid_response("Object idn {} does not exist.".format(obj_idn))

                        word = me.says(
                            vrb=vrb,
                            obj=obj,
                            num=num,
                            num_add=num_add,
                            txt=txt,
                        )
                        assert word.idn == lex.max_idn(), "NEW SENTENCE {} isn't as new as {}.".format(word.idn, lex.max_idn)

                        # return django.shortcuts.redirect('/qiki-playground/')
                        # jbo = lex.find_words(obj=obj, vrb=vrb)
                        # jbo = lex.find_words(idn=obj, jbo_vrb=vrb)[0]

                        word_dict = templatetags.playground_extras.organize_words_by_vrb_and_sbj(
                            lex.find_words(obj=obj, vrb=vrb)
                        )
                        try:
                            icon_entry = word_dict[vrb]
                        except KeyError:
                            raise RuntimeError("Could not find {vrb} in {word_dict}".format(
                                vrb=repr(vrb),
                                word_dict=repr(word_dict)
                            ))
                        icon_html = strip_empty_html_comments(render_to_string(
                            'icon-diagram-call.html',
                            templatetags.playground_extras.icon_diagram(
                                vrb,
                                icon_entry,
                                me.idn
                            )
                        ))
                        return valid_responses(dict(
                            report="[{sbj}]-->({vrb})-->[{obj}] Number({num}) '{txt}'".format(
                                sbj=me.idn.qstring(),
                                vrb=vrb.idn.qstring(),
                                obj=obj_idn.qstring(),
                                num=word.num.qstring(),
                                txt=txt,
                            ),
                            icon_html=icon_html
                            # + repr(jbo),
                            # icon_html=repr(templatetags.playground_extras.icon_diagram(
                            #     vrb,
                            #     {},
                            #     qiki.Number()
                            # )),
                            # icon_html=render_to_string(
                            #     'icon-rebuilt.html',
                            #     dict(
                            #         vrb=vrb,
                            #         icon_entry={me: {'num': qiki.Number(1), 'history': []}},
                            #         user_idn=me.idn,
                            #     )
                            # ),

                            # SEE:  Inclusion tag rendering, http://stackoverflow.com/questions/3513990/django-rendering-inclusion-tag-from-a-view
                        ))
                    else:
                        actual_keys = list(sentence_form.cleaned_data.keys())
                        return invalid_response("Sentence needs sbj, vrb, obj, num, txt.\n"
                                                "Only got: {}".format(
                            ", ".join(actual_keys)
                        ))
                        # XXX:  Why does this "form" include a 'comment' field?!?
                elif action == 'comment':
                    comment_text = form.cleaned_data['comment']
                    # me = DjangoUser(qiki.Number(request.user.id))
                    # comment = lex.verb(u'comment')
                    # me.says(comment, lex, qiki.Number(1), comment_text)
                    DjangoUser(request.user.id)(u'comment')[lex] = comment_text
                    # # me.comment(lex, 1, comment_text)
                    # # TODO:  Would this work if there were a me.lex?
                    # comment_word = lex.spawn(
                    #     sbj=me.idn,
                    #     vrb=comment.idn,
                    #     obj=lex.idn,
                    #     txt=comment_text,
                    #     num=qiki.Number(1),
                    # )
                    # comment_word.save()
                    return django.shortcuts.redirect('/qiki-playground/')
                else:
                    return HttpResponseNotFound("Action '%s' is not supported" % action)
            else:
                return HttpResponse("Whoa %s" % repr(form.errors))
        else:
            return HttpResponse("Oops, this is a POST-only URL.")


def valid_response(name, value):
    """Good conclusion, one name=value pair to return to the browser."""
    response_dict = dict(
        is_valid=True,
        error_message=''
    )
    response_dict[name] = value
    return HttpResponse(json.dumps(response_dict))

def valid_responses(valid_dictionary):
    """Good conclusion, multiple name=value pairs to return to the browser."""
    response_dict = dict(
        is_valid=True,
        error_message=''
    )
    response_dict.update(valid_dictionary)
    return HttpResponse(json.dumps(response_dict))

def invalid_response(error_message):
    response_dict = dict(
        is_valid=False,
        error_message=error_message
    )
    return HttpResponse(json.dumps(response_dict))



# SEE about Django template dot notation versatility, very helpful, http://stackoverflow.com/a/1700726/673991