import json
from django.utils.translation import get_language
from django import template
register = template.Library()

@register.simple_tag(name='translated_node_title')
def translated_node_title(node):
    try:
        jtitle = json.loads(node.title_lang)
        lang = get_language()
        if lang in jtitle:
            return jtitle[lang]
        else:
            return node.title
    except:
        return node.title


@register.simple_tag(name='translated_node_desc')
def translated_node_desc(node):
    try:
        jdesc = json.loads(node.description_lang)
        lang = get_language()
        if lang in jdesc:
            return jdesc[lang]
        else:
            return node.description
    except:
        return node.description


@register.filter
def dictkeyvalue(dict, key):
    return dict[key]


@register.filter
def underscore_to_space(value):
    return value.replace("_"," ")
