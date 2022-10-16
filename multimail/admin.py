from django.contrib import admin
from .models import EmailAddress


class EmailAddressAdmin(admin.ModelAdmin):
    pass

admin.site.register(EmailAddress, EmailAddressAdmin)
