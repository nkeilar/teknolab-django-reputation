from django import template
from django.template import Node, NodeList, Template, Context, Variable, VariableDoesNotExist
from django.template.defaulttags import IfEqualNode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from django_utils.templatetag_helpers import resolve_variable, copy_context
from django_reputation.models import Reputation

register = template.Library()

@register.tag(name="associate_reputation")
def do_associate_reputation(parser,  token):
    """
    @object
    """
    try:
        tag, node  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError,  "%r tag requires one argument" % token.contents.split()[0]
    return AssociateReputation(node)

class AssociateReputation(template.Node):
    def __init__(self, node):
        self.node = node
        
    def render(self,  context):
        node = resolve_variable(self.node, context, self.node)
        node.reputation = Reputation.objects.reputation_for_user(node)
        return ''