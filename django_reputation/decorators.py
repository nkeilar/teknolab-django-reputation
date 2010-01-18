from functools import update_wrapper

from django import http
from django.core.urlresolvers import reverse
from django.utils.functional import wraps
from django.utils.http import urlquote
from django.core.exceptions import ObjectDoesNotExist

from django_reputation.exceptions import ReputationException
from django_reputation.models import Permission, Reputation, ReputationAction

def reputation_required(permission_name):
    """
    checks to determine if the current logged in user has permissions to use
    a part of a the site based on permission_name and redirects
    to the reputation-required view if the reputation check fails
    @permission_name
    """
    def dec(view_func):
        return _ReputationRequired(permission_name, view_func)
    return dec

def log_reputation_action(user, reputation_action_name, object):
    """
    convenience decorator to log a reputation action
    @reputation_action_name
    @object
    """
    def dec(func):
        return _LogReputationAction(user, reputation_action_name, object, func)
    return dec

class _ReputationRequired(object):
    """
    checks to determine if the current logged in user has permissions to use
    a part of a the site based on permission_name and redirects
    to the reputation-required view if the reputation check fails
    @permission_name
    @view_func
    """
    def __init__(self, permission_name, view_func):
        self.permission_name = permission_name
        try:
            self.permission = Permission.objects.get(name = permission_name)
        except ObjectDoesNotExist:
            self.permission = None
        self.view_func = view_func
        update_wrapper(self, view_func)
    
    def __get__(self, obj, cls = None):
        view_func = self.view_func.__get__(obj, cls)
        return _CheckLogin(self.permission_name, view_func)
    
    def __call__(self,  request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if self.permission and Reputation.objects.reputation_for_user(user).reputation < self.permission.required_reputation:
                return http.HttpResponseRedirect(reverse('reputation-required',  args=[self.permission_name]))
            else:
                return self.view_func(request, *args, **kwargs)
        else:
            return http.HttpResponseRedirect(reverse('reputation-required',  args=[self.permission_name]))

class _LogReputationAction(object):
    """
    convenience decorator to log a reputation action
    @reputation_action_name
    @object
    @func
    """
    
    def __init__(self, user, reputation_action_name, object, func):
        self.reputation_action_name = reputation_action_name
        self.func = func
        self.user = user
        self.object = object
            
    def __call__(self, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            try:
                Reputation.objects.log_reputation_action(self.user, self.reputation_action_name, self.object)
            except ReputationException:
                pass
        return self.func(*args, **kwargs)
        