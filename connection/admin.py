from django.contrib import admin

from .models import Connection
from .models import UserConnection
from .models import NodePassword

admin.site.register(Connection)
admin.site.register(UserConnection)
admin.site.register(NodePassword)


