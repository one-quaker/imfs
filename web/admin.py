from django.contrib import admin
from .models import Photo, Wallet


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('dir', 'pk', 'file', 'created_at')
    list_filter = ('dir', 'created_at')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('address', 'pk', 'created_at')
