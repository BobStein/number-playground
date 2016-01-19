import datetime
import json
import sys

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound
import django.shortcuts
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
logger = logging.getLogger(__name__)
logger.info("{now}".format(now=datetime.datetime.now().strftime("%Y.%m%d.%H%M.%S")))
# FIXME:  Timestamp in the log.  (effing django)

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


@login_required
def qiki_playground(request):
    if request.user.is_anonymous():
        return "Log in"
    else:
        lex = get_lex()
        idns = lex.get_all_idns()
        words = []
        for idn in idns:
            word = lex(idn)
            word.do_not_call_in_templates = True
            words.append(word)
        return django.shortcuts.render(
            request,
            'qiki-playground.html',
            {
                'user_id': request.user.id,
                'user_name': request.user.username,
                'user_email': request.user.email,
                'words': words,
            }
        )


class DjangoUser(qiki.Listing):
    def lookup(self, index, callback):
        try:
            user_name = User.objects.get(id=int(index)).username
            # THANKS: http://stackoverflow.com/a/2568955/673991
        except User.DoesNotExist:
            raise self.NotFound
        callback(user_name, qiki.Number(1))


def get_lex():
    lex = qiki.LexMySQL(**secure.credentials.for_playground_database)
    listing = lex.noun('listing')
    qiki.Listing.install(listing)
    django_user = listing('django_user')
    DjangoUser.install(django_user)
    # raise Exception
    return lex


def build_qoolbar():
    lex = get_lex()
    lex.verb('qool')
    lex.verb('iconify')

    like = lex.verb('like')
    lex.qool(like, qiki.Number(1), use_already=True)
    lex.iconify(like, qiki.Number(16), 'http://tool.qiki.info/icon/thumbsup_16.png', use_already=True)

    delete = lex.verb('delete')
    lex.qool(delete, qiki.Number(1), use_already=True)
    lex.iconify(delete, qiki.Number(16), 'http://tool.qiki.info/icon/delete_16.png', use_already=True)
build_qoolbar()


class QikiActionForm(forms.Form):
    action  = forms.CharField(required=True)
    comment = forms.CharField(required=False)


class QikiActionSentenceForm(QikiActionForm):
    vrb = forms.CharField(required=True)
    obj = forms.CharField(required=True)
    num = forms.CharField(required=True)
    txt = forms.CharField(required=False)

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
                    lex = get_lex()
                    idns = lex.get_all_idns()
                    report=""
                    for idn in idns:
                        word = lex(idn)
                        report += str(int(idn)) + " " + word.description()
                        report += "\n"
                    return valid_response('report', report)
                elif action == 'qoolbar_list':
                    lex = get_lex()
                    qool = lex('qool')
                    define = lex('define')
                    iconify = lex('iconify')
                    qool_verbs = lex.find(vrb=define, obj=qool)
                    report = ""
                    verbs = []
                    for qool_verb in qool_verbs:
                        icons = lex.find(vrb=iconify, obj=qool_verb)
                        icon = icons[-1]
                        report += """
                            {number}. <img src="{url}"> {name}<br>
                        """.format(
                            number=str(int(icon.idn)),
                            url=icon.txt,
                            name=qool_verb.txt,
                        )
                        verbs.append(dict(
                            idn=str(int(qool_verb.idn)),
                            icon_url=icon.txt,
                            name=qool_verb.txt,
                        ))
                    return valid_responses(dict(
                        report=report,
                        verbs=verbs,
                    ))
                elif action == 'sentence':
                    sentence_form = QikiActionSentenceForm(request.POST)
                    me = DjangoUser(qiki.Number(request.user.id))
                    lex = get_lex()
                    if sentence_form.is_valid():
                        try:
                            vrb_idn = lex(sentence_form.cleaned_data['vrb']).idn
                        except qiki.Number.ConstructorTypeError:
                            vrb_idn = qiki.Number(sentence_form.cleaned_data['vrb'])
                        obj_idn = qiki.Number(sentence_form.cleaned_data['obj']) # e.g. '0x82_2A'
                        num = qiki.Number(sentence_form.cleaned_data['num'])
                        txt = sentence_form.cleaned_data['txt']

                        vrb=lex(vrb_idn)
                        if not vrb.exists:
                            return invalid_response("Verb '{}' does not exist.".format(
                                sentence_form.cleaned_data['vrb']))
                        if not vrb.is_a_verb():
                            return invalid_response("Word '{}' is not a verb.".format(
                                sentence_form.cleaned_data['vrb']))

                        obj=lex(obj_idn)
                        if not obj.exists:
                            return invalid_response("Object '{}' does not exist.".format(
                                sentence_form.cleaned_data['obj']))

                        lex.sentence(
                            sbj=me,
                            vrb=vrb,
                            obj=obj,
                            num=num,
                            txt=txt,
                        )
                        # return django.shortcuts.redirect('/qiki-playground/')
                        return valid_responses(dict(
                            report="[{sbj}]-->({vrb})-->[{obj}] Number({num}) '{txt}'".format(
                                sbj=me.idn.qstring(),
                                vrb=vrb_idn.qstring(),
                                obj=obj_idn.qstring(),
                                num=num.qstring(),
                                txt=txt,
                            )
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
                    lex = get_lex()
                    me = DjangoUser(qiki.Number(request.user.id))
                    lex.verb('comment')
                    me.comment(lex, qiki.Number(1), comment_text)
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
    response_dict = dict(
        is_valid=True,
        error_message=''
    )
    response_dict[name] = value
    return HttpResponse(json.dumps(response_dict))

def valid_responses(valid_dictionary):
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
