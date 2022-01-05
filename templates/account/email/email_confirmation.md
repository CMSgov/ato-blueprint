{% extends "email/template" %}
{% load account %}
{% block content %}
{% user_display user as user_display %}
Hello {{user_display}},

Please confirm your email address at CMS Blueprint by following this link:

[{{activate_url}}]({{activate_url}})
{% endblock %}
