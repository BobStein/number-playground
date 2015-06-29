import json

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
import os
from number import Number
from word import Word, System


@ensure_csrf_cookie
def number_playground(request):
    return render(request, 'number-playground.html')

    # return render_to_response('playground.html', {}, context_instance=RequestContext(request))

    # return render_to_response('playground.html')  #, {'aaa': ({'qstring':str(Number(x/256.0)), 'float':x/256.0} for x in range(-65536-256*10,65536+256*10+1))})

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
                    number_from_qstring = Number(form.cleaned_data['qstring'])
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
                        # TODO: support q-string by trying Number(floater) ?
                        return invalid_response("Either %s, or %s" % (float_error, int_error))
                    else:
                        qstring = Number(integer_typed).qstring()
                        return valid_response('qstring', qstring)
                else:
                    qstring = Number(floating_point_typed, qigits=7).qstring()
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
        return render(
            request,
            'qiki-playground.html',
            {
                'name': request.user.username,
                'email': request.user.email
            }
        )


def qiki_ajax(request):
    if request.method == 'POST':
        form = Playform(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'qiki_list':
                system = System(
                    language=os.environ['DATABASE_LANGUAGE'],
                    host=    os.environ['DATABASE_HOST'],
                    port=    os.environ['DATABASE_PORT'],
                    user=    os.environ['DATABASE_USER'],
                    password=os.environ['DATABASE_PASSWORD'],
                    database=os.environ['DATABASE_DATABASE'],
                    table=   os.environ['DATABASE_TABLE'],
                )
                ids = system.get_all_ids()
                report=""
                for _id in ids:
                    report += str(int(_id)) + " " + system(_id).description()
                    report += "\n"
                return valid_response('report', report)
            else:
                r = HttpResponse()
                r.status_code = 404
                r.reason_phrase = "Action '%s' not supported" % action
                return r
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
