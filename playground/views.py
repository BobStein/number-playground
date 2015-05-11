from django.shortcuts import render
from django.shortcuts import render_to_response
from Number import Number
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.template import Template, loader, RequestContext
from django.http import HttpResponse
from django import forms
import json

@ensure_csrf_cookie
def playground(request):
    return render(request, 'playground.html')

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

    def valid_response(name, value):
        response_dict = {
            'is_valid'     : True,
            'error_message': '',
        }
        response_dict[name] = value;
        return HttpResponse(json.dumps(response_dict))

    def invalid_response(why):
        response_dict = {
            'is_valid'     : False,
            'error_message': why,
        }
        return HttpResponse(json.dumps(response_dict))

    if request.method == 'POST':
        form = Playform(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'qstring_to_float':
                try:
                    number_from_qstring = Number(form.cleaned_data['qstring'])
                    floater = str(float(number_from_qstring))
                except Exception as e:
                    return invalid_response(str(e));
                else:
                    return valid_response('floater', floater);
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
                        return invalid_response("Either %s, or %s" % (float_error, int_error));
                    else:
                        qstring = Number(integer_typed).qstring()
                        return valid_response('qstring', qstring)
                else:
                    qstring = Number(floating_point_typed, qigits=7).qstring()
                    return valid_response('qstring', qstring);
            else:
                r = HttpResponse()
                r.status_code = 404
                r.reason_phrase = "Action '%s' not supported" % action
                return r
        else:
            return HttpResponse('whoa %s' % repr(form.errors))
    else:
        return HttpResponse('Oops, this is a POST-only URL.')