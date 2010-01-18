from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.template.context import Context

from django_utils.templatetag_helpers import resolve_variable, combine_variable_list
from django_reputation.models import Permission, Reputation
import django_reputation.config as config

register = template.Library()

@register.tag(name="reputation_overlay")
def do_check_reputation(parser,  token):
    """
    ReputationOverlay
    """
    try:
        args_list  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return ReputationOverlay(args_list[1:])

class ReputationOverlay(template.Node):
    """
    tag for generating JS that displays an overlay for handling javascript
    based reputation checks.
    
    depends on jquery.overlay at http://flowplayer.org/tools/overlay.html
    """
    
    def __init__(self, args):
        self.args = args
        
    def render(self,  context):
        link_id = combine_variable_list(self.args, context)
        
        ajax_script = """<script type='text/javascript'>$("#%s").overlay({expose: {color: '#333', loadSpeed: 200, opacity: 0.9}});</script>""" % (link_id)
        return_value = "\n" + ajax_script + "\n"
        return return_value

@register.tag(name="update_deny_message")
def do_update_deny_message(parser,  token):
    """
    DenyMessage
    """
    try:
        tag, unique_id,  overlay_id,  permission_name  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires two arguments" % token.contents.split()[0]
    return DenyMessage(unique_id,  overlay_id,  permission_name)

class DenyMessage(template.Node):
    """
    convenience tag for generating JavaScript that changes the html of an html element with
    id = unique_id to the description of the specified Permission object.  Useful for
    displaying messages to users when they do not have enough reputation to access a section of 
    the site.
    """
    def __init__(self, unique_id,  overlay_id, permission_name):
        self.unique_id = unique_id
        self.overlay_id = overlay_id
        self.permission_name = permission_name
        
    def render(self,  context):
        unique_id = resolve_variable(self.unique_id,  context, self.unique_id)
        
        try:
            permission = Permission.objects.get(name = self.permission_name)
        except ObjectDoesNotExist:
            permission = None
        
        if permission:
            inner_function =  '$("#%s").html("%s");' % (self.overlay_id, permission.description) 
            ajax_script = """<script type='text/javascript'>$("#%s").bind("click", function() {%s});</script>""" % (str(unique_id), inner_function)
            return_value = "\n" + ajax_script + "\n"
        else:
            return_value = ''
        return return_value
