from functools import update_wrapper

from django import http
from django.core.urlresolvers import reverse
from django.utils.functional import wraps
from django.utils.http import urlquote
from django.core.exceptions import ObjectDoesNotExist

from django_reputation.exceptions import ReputationException
from django_reputation.models import Permission, Reputation, ReputationAction

def ReputationRequired(view_func, permission_name):
    """
    Checks to determine if the current logged in user has permissions to use
    a part of a the site based on permission_name and redirects
    to the reputation-required view if the reputation check fails.
    
    @param permission_name
    """     
    def dec(target, request, *args, **kwargs):
        try:
            permission = Permission.objects.get(name = permission_name)
        except ObjectDoesNotExist:
            permission = None
        
        user = request.user
        if user.is_authenticated:
            if permission and Reputation.objects.reputation_for_user(user).reputation < permission.required_reputation:
                return http.HttpResponseRedirect(reverse('reputation-required',  args=[permission_name]))
            else:
                return view_func(target, request, *args, **kwargs)
        else:
            return http.HttpResponseRedirect(reverse('reputation-required',  args=[permission_name]))
    return dec

def reputation_required(permission_name):
    """
    Checks to determine if the current logged in user has permissions to use
    a part of a the site based on permission_name and redirects
    to the reputation-required view if the reputation check fails.
    
    @param permission_name
    """
    def dec(view_func):
        return _ReputationRequired(permission_name, view_func)
    return dec

class _ReputationRequired(object):
    """
    Checks to determine if the current logged in user has permissions to use
    a part of a the site based on permission_name and redirects
    to the reputation-required view if the reputation check fails.
    """
    def __init__(self, permission_name, view_func):
        self.permission_name = permission_name
        try:
            self.permission = Permission.objects.get(name = permission_name)
        except ObjectDoesNotExist:
            self.permission = None
        self.view_func = view_func
        update_wrapper(self, view_func)
    
    def __call__(self,  request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if self.permission and Reputation.objects.reputation_for_user(user).reputation < self.permission.required_reputation:
                return http.HttpResponseRedirect(reverse('reputation-required',  args=[self.permission_name]))
            else:
                return self.view_func(request, *args, **kwargs)
        else:
            return http.HttpResponseRedirect(reverse('reputation-required',  args=[self.permission_name]))
        