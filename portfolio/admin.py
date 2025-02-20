from django.contrib import admin
from .models import Portfolio, Nav, Transaction

admin.site.register(Nav)
admin.site.register(Portfolio)
admin.site.register(Transaction)

