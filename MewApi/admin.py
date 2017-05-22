# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import string

from django.contrib import admin
from MewApi.models import *
import random

# Register your models here.


class MewVersionAdmin(admin.ModelAdmin):
    list_display = ("version_string", "enabled", "created_at")
    search_fields = ["version_string"]
    list_filter = ["enabled"]


class MewDeviceAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "enabled", "created_at")
    search_fields = ["unique_id"]
    list_filter = ["enabled"]


class MewCodeAdmin(admin.ModelAdmin):
    list_display = ("code_value", "bucket", "enabled", "bind_device", "used_at")
    search_fields = ["code_value", "bind_device"]
    list_filter = ["enabled", "bucket"]
    readonly_fields = ["used_at", "bind_device"]
    
    def has_add_permission(self, request):
        return False


class MewCodeBucketAdmin(admin.ModelAdmin):
    
    list_display = ("name", "code_count", "created_at")
    search_fields = ["name"]
    
    def save_model(self, request, obj, form, change):
        code_export = ""
        obj.save()
        for i in range(0, obj.code_count):
            code_n = MewCode()
            code_n.code_value = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ3456789") for _ in range(12))
            code_n.bucket = obj
            code_n.save()
            code_export += code_n.code_value + "\n"
        obj.code_export = code_export
        super(MewCodeBucketAdmin, self).save_model(request, obj, form, change)
        
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ["code_export"]
        else:
            return ["code_export", "code_count"]


class MewCertificateAdmin(admin.ModelAdmin):
    pass


admin.site.register(MewVersion, MewVersionAdmin)
admin.site.register(MewDevice, MewDeviceAdmin)
admin.site.register(MewCode, MewCodeAdmin)
admin.site.register(MewCodeBucket, MewCodeBucketAdmin)
admin.site.register(MewCertificate, MewCertificateAdmin)
