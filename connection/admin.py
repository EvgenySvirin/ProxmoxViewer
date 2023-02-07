from django.contrib import admin

from .models import Connection
from .models import UserConnection


admin.site.register(Connection)
admin.site.register(UserConnection)

