from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

import django_widgets.tag_helpers as template_helpers
from django_widgets.tag_helpers import resolve_variable
from django_reputation.models import Permission, Reputation

register = template.Library()

@register.tag(name="check_reputation")
def do_check_reputation(parser,  token):
    """
    BranchedReputationControl
    @user - user object
    @permission_action - name of a Permission object
    @target_template - template to redirect to
    """
    try:
        tag, user, permission_action, target_template  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires three arguments" % token.contents.split()[0]
    return BranchedReputationControl(user,  permission_action,  target_template)

class BranchedReputationControl(template.Node):
    """
    Convenience tag for providing the has_access variable at template render
    time to target_template.
    
    If a Permission object with name = permission_action exists and the user
    has reputation >= reputation_required, then has_access = True.
    
    If a Permission object does not exist, then has_access = True.
    
    Else, has_access = False.
    """
    
    def __init__(self, user_reputation,  permission_action,  target_template):
        self.permission_action = permission_action
        self.target_template = target_template
        self.user_reputation = user_reputation
        
    def render(self,  context):
        permission_action = resolve_variable(self.permission_action,  context,  self.permission_action)
        user_reputation = resolve_variable(self.user_reputation, context, self.user_reputation)
        
        try:
            permission_object = Permission.objects.get(name = permission_action)
        except ObjectDoesNotExist:
            permission_object = None
        
        if not user_reputation is None:
            has_access = not permission_object or user_reputation.reputatation >= permission_object.reputation_required
        else:
            has_access = False
            
        context['has_access'] = has_access
        return render_to_string(self.target_template,  {}, context)

@register.tag(name="reputation_overlay")
def do_check_reputation(parser,  token):
    """
    ReputationOverlay
    """
    try:
        tag,  prefix,  unique_id  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return ReputationOverlay(prefix,  unique_id)

class ReputationOverlay(template.Node):
    """
    Convenience tag for generating JavaScript that displays an overlay specified in the html element with
    id = prefix + unique_id.
    """
    
    def __init__(self, prefix, unique_id):
        self.prefix = prefix
        self.unique_id = unique_id
        
    def render(self,  context):
        unique_id = resolve_variable(self.unique_id,  context,  self.unique_id)
        prefix = resolve_variable(self.prefix,  context,  self.prefix)
        link_id = "%s%s" % (prefix,  unique_id)
        
        ajax_script = "<script type='text/javascript'>" + \
                                    '$("#' + str(link_id) + \
                                    '").overlay();' +\
                                "</script>"
        return_value = "\n" + ajax_script + "\n"
        return return_value

@register.tag(name="update_deny_message")
def do_update_deny_message(parser,  token):
    """
    DenyMessage
    """
    try:
        tag,  prefix,  unique_id,  overlay_id,  permission_name  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return DenyMessage(prefix,  unique_id,  overlay_id,  permission_name)

class DenyMessage(template.Node):
    """
    Convenience tag for generating JavaScript that changes the html of an html element with
    id = prefix + unique_id to the description of the specified Permission object.  Useful for
    display messages to users when they do not have enough reputation to access a section of 
    the site.
    """
    def __init__(self, prefix,  unique_id,  overlay_id, permission_name):
        self.prefix = prefix
        self.unique_id = unique_id
        self.overlay_id = overlay_id
        self.permission_name = permission_name
        
    def render(self,  context):
        unique_id = resolve_variable(self.unique_id,  context)
        prefix = resolve_variable(self.prefix,  context,  self.prefix)
        link_id = "%s%s" % (prefix,  unique_id)
        
        try:
            permission = Permission.objects.get(name = self.permission_name)
        except ObjectDoesNotExist:
            permission = None
        
        if permission:
            inner_function =  '$("#%s").html("%s");' % (self.overlay_id, permission.description) 
            ajax_script = """<script type='text/javascript'>$("#%s").bind("click", function() {%s return false;});</script>""" % (str(link_id), inner_function)
            return_value = "\n" + ajax_script + "\n"
        else:
            return_value = ''
        return return_value
