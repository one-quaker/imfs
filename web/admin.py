from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from .models import Photo, Wallet, WalletConfig


FORMFIELD_OVERRIDES = {
    models.CharField: {'widget': TextInput(attrs={'size': '120'})},
    models.TextField: {'widget': Textarea(attrs={'rows': 30, 'cols': 100})},
}


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('dir', 'pk', 'file', 'created_at')
    list_filter = ('dir', 'created_at')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('address', 'pk', 'created_at')


@admin.register(WalletConfig)
class WalletConfigAdmin(admin.ModelAdmin):
    list_display = ('address', 'pk', 'created_at')
    formfield_overrides = FORMFIELD_OVERRIDES
