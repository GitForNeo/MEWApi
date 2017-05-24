# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random

from django import forms
from django.contrib import admin
from django.contrib import messages
from MewApi.models import *
from django.core.exceptions import ValidationError

# Register your models here.


class MewVersionAdmin(admin.ModelAdmin):
    list_display = ("version_string", "enabled", "created_at")
    search_fields = ["version_string"]
    list_filter = ["enabled"]
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        return request.user.is_superuser


class MewDeviceAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "enabled", "created_at")
    search_fields = ["unique_id"]
    list_filter = ["enabled"]

    def get_queryset(self, request):
        qs = super(MewDeviceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(related_user=request.user)
    
    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ["related_user"]


class MewCodeAdmin(admin.ModelAdmin):
    list_display = ("code_value", "bucket", "enabled", "bind_device", "used_at")
    search_fields = ["code_value", "bind_device"]
    list_filter = ["enabled", "bucket"]

    def get_queryset(self, request):
        qs = super(MewCodeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(related_user=request.user)
    
    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ["used_at", "bind_device"]
        else:
            return ["used_at", "bind_device", "related_user"]


class MewCodeBucketForm(forms.ModelForm):
    class Meta:
        model = MewCodeBucket
        fields = ["name", "code_count", "code_export", "related_user"]
        
    def clean_code_count(self):
        req_user = self.request.user
        record_m = MewAgentPointRecord.objects.filter(related_user=req_user)
        if len(record_m) == 0:
            raise ValidationError("Cannot access your point record, please contact the administrator.")
        record_n = record_m[0]
        remained_points = record_n.points
        code_count_val = self.cleaned_data['code_count']
        code_count = int(code_count_val)
        point_need = code_count * 100
        if remained_points < point_need:
            raise ValidationError("Your points are not enough. %s points needed, you have %s points." % (point_need,
                                                                                                         remained_points))
        return code_count_val


class MewCodeBucketAdmin(admin.ModelAdmin):
    
    form = MewCodeBucketForm
    list_display = ("name", "code_count", "created_at")
    search_fields = ["name"]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(MewCodeBucketAdmin, self).get_form(request, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super(MewCodeBucketAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(related_user=request.user)
    
    def save_model(self, request, obj, form, change):
        need_points = (obj.code_count * 100)
        if not request.user.is_superuser:
            record_m = MewAgentPointRecord.objects.get(related_user=request.user)
            remained_points = record_m.points - need_points
            record_m.points = remained_points
            record_m.save()
            messages.add_message(request, messages.SUCCESS,
                                 "You spent %d points to generate %d codes, and you have %d points left." % (need_points,
                                                                                                             obj.code_count,
                                                                                                             remained_points))
        code_export = ""
        obj.save()
        for i in range(0, obj.code_count):
            code_n = MewCode()
            code_n.related_user = request.user
            code_n.code_value = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ3456789") for _ in range(12))
            code_n.bucket = obj
            code_n.save()
            code_export += code_n.code_value + "\n"
        obj.related_user = request.user
        obj.code_export = code_export
        super(MewCodeBucketAdmin, self).save_model(request, obj, form, change)
        
    def get_readonly_fields(self, request, obj=None):
        readonly_f = ["code_export"]
        if obj is not None:
            readonly_f.append("code_count")
        if not request.user.is_superuser:
            readonly_f.append("related_user")
        return readonly_f


class MewCertificateAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        return request.user.is_superuser


class MewAgentRecordAdmin(admin.ModelAdmin):
    list_display = ("related_user", "points")

    def get_queryset(self, request):
        qs = super(MewAgentRecordAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(related_user=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_f = []
        if obj is not None:
            readonly_f.append("related_user")
        if not request.user.is_superuser:
            readonly_f.append("points")
        return readonly_f
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(MewVersion, MewVersionAdmin)
admin.site.register(MewDevice, MewDeviceAdmin)
admin.site.register(MewCode, MewCodeAdmin)
admin.site.register(MewCodeBucket, MewCodeBucketAdmin)
admin.site.register(MewCertificate, MewCertificateAdmin)
admin.site.register(MewAgentPointRecord, MewAgentRecordAdmin)
