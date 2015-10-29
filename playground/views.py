import json
import datetime

import django.shortcuts
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, HttpResponseNotFound
from django import forms
from django.contrib.auth.decorators import login_required
import sys
import logging
logger = logging.getLogger(__name__)
logger.info("".format(now=datetime.datetime.now().strftime("%Y.%m%d.%H%M.%S")))   # FIXME:  effing django

import qiki
try:
    import secure.credentials
except ImportError as import_error:
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
    logger.exception(import_error)
    sys.exit(1)

QIKI_AJAX_URL = "/qiki-ajax"


@ensure_csrf_cookie
def number_playground(request):
    return django.shortcuts.render(request, 'number-playground.html')

    # return render_to_response('playground.html', {}, context_instance=RequestContext(request))

    # return render_to_response('playground.html')  #, {'aaa': ({'qstring':str(qiki.Number(x/256.0)), 'float':x/256.0} for x in range(-65536-256*10,65536+256*10+1))})

    # t = loader.get_template('playground.html')
    # c = RequestContext(request)
    # return HttpResponse(t.render(c))


class Playform(forms.Form):
    action  = forms.CharField(required=False)
    qstring = forms.CharField(required=False)
    floater = forms.CharField(required=False)


def qikinumber(request):
    if request.method == 'POST':
        form = Playform(request.POST)
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
        return django.shortcuts.render(
            request,
            'qiki-playground.html',
            {
                'user_id': request.user.id,
                'user_name': request.user.username,
                'user_email': request.user.email,
                'QIKI_AJAX_URL': QIKI_AJAX_URL,
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


def get_system():
    system = qiki.SystemMySQL(**secure.credentials.for_playground_database)
    listing = system.noun('listing')
    qiki.Listing.install(listing)
    django_user = listing('django_user')
    DjangoUser.install(django_user)
    # raise Exception
    return system


class QikiPlaygroundForm(forms.Form):
    action  = forms.CharField(required=True)
    comment = forms.CharField(required=False)


@login_required
def qiki_ajax(request):
    if request.user.is_anonymous():
        return HttpResponse("Log in")
    else:
        if request.method == 'POST':
            form = QikiPlaygroundForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data['action']
                if action == 'qiki_list':
                    system = get_system()
                    idns = system.get_all_idns()
                    report=""
                    for idn in idns:
                        report += str(int(idn)) + " " + system(idn).description()
                        report += "\n"
                    return valid_response('report', report)
                elif action == 'comment':
                    comment_text = form.cleaned_data['comment']
                    system = get_system()
                    comment = system.verb('comment')   # Is this needed?
                    me = DjangoUser(qiki.Number(request.user.id))
                    me.comment(system, comment_text, qiki.Number(1))
                    # # me.comment(system, 1, comment_text)
                    # # TODO:  Would this work if there were a me.system?
                    # comment_word = system.spawn(
                    #     sbj=me.idn,
                    #     vrb=comment.idn,
                    #     obj=system.idn,
                    #     txt=comment_text,
                    #     num=qiki.Number(1),
                    # )
                    # comment_word.save()
                    return django.shortcuts.redirect('/qiki-playground/')
                else:
                    return HttpResponseNotFound("Action '%s' is not supported" % action)
            else:
                return HttpResponse('whoa %s' % repr(form.errors))
        else:
            return HttpResponse('Oops, this is a POST-only URL.')


def valid_response(name, value):
    response_dict = dict(
        is_valid=True,
        error_message=''
    )
    response_dict[name] = value
    return HttpResponse(json.dumps(response_dict))

def invalid_response(why):
    response_dict = dict(
        is_valid=False,
        error_message=why
    )
    return HttpResponse(json.dumps(response_dict))
