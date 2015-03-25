# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from helpers import is_valid_email, reset_pass
from profiles.models import SavedMovie
from movies.models import Movie

__author__ = 'hector'


def login_user(request):
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect("/main/")
    if request.method == "POST":
        if 'email' in request.POST and request.POST['email']:
            if is_valid_email(request.POST['email']):
                # reset password
                user = User.objects.get(email=request.POST['email'])
                reset_pass(request.POST['email'], user)
                error = "En breve recibirá un correo con su nueva contraseña."
            else:
                error = 'El correo proporcionado no es v&aacute;lido'
        else:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if 'rememberme' not in request.POST:
                        request.session.set_expiry(900)

                    login(request, user)
                    url = "/index/"
                    try:
                        ur_get = request.META['HTTP_REFERER']
                    except KeyError:
                        pass
                    else:
                        ur_get = ur_get.split("next=")
                        if len(ur_get) > 1:
                            url = ur_get[1]
                    return HttpResponseRedirect(url)
                else:
                    error = "Tu cuenta ha sido desactivada, por favor " \
                            "ponte en contacto con tu administrador"
            else:
                error = "Tu nombre de usuario o contrase&ntilde;a son " \
                        "incorrectos."
    variables = dict(error=error)
    variables_template = RequestContext(request, variables)
    return render_to_response("login.html", variables_template)


def index(request):
    saved_pks = SavedMovie.objects.filter(user=request.user)\
        .values_list('movie__pk', flat=True)
    movies = Movie.objects.exclude(pk__in=saved_pks).aggregate()[:16]

