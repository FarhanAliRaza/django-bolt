
# Register your models here.

from django.contrib import admin

from .models import Blog, Author

admin.site.register(Blog)
admin.site.register(Author)

