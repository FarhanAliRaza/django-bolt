from django.template import loader

from .responses import Response


def render(
    request, template_name : str, context=None, content_type=None, status=200, using=None
):
    """
    Return an HttpResponse whose content is filled with the result of calling
    django.template.loader.render_to_string() with the passed arguments.
    """
    content = loader.render_to_string(template_name, context, request, using=using)
    return Response(content=content, media_type=content_type, status_code=status)
