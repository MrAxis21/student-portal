from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def unread_count(user):
    if user.is_authenticated:
        return user.notifications.filter(is_read=False).count()
    return 0

@register.filter
def split(value, key):
    return value.split(key)
