# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

# Create your models here.


class MewVersion(models.Model):
    class Meta(object):
        verbose_name = "Version"
        verbose_name_plural = "Versions"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )  # OK
    
    version_string = models.CharField(
        verbose_name="Version String",
        max_length=16,
        default=""
    )
    
    enabled = models.BooleanField(
        verbose_name="Enabled",
        default=True
    )

    def __unicode__(self):
        return self.version_string


class MewDevice(models.Model):
    class Meta(object):
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )  # OK
    
    unique_id = models.CharField(
        verbose_name="Unique ID",
        max_length=40,
        default="",
        unique=True,
    )  # OK
    
    enabled = models.BooleanField(
        verbose_name="Enabled",
        default=True
    )

    def __unicode__(self):
        return self.unique_id


class MewCodeBucket(models.Model):
    class Meta(object):
        verbose_name = "Code Bucket"
        verbose_name_plural = "Code Buckets"
    
    id = models.AutoField(
        primary_key=True,
        editable=False
    )
    
    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )
    
    name = models.CharField(
        verbose_name="Name",
        max_length=64,
        unique=True,
        default="Untitled Bucket"
    )
    
    code_count = models.IntegerField(
        verbose_name="Code Count",
        default=100,
    )
    
    code_export = models.TextField(
        verbose_name="Code Export",
        blank=True
    )
    
    def __unicode__(self):
        return self.name


class MewCode(models.Model):
    class Meta(object):
        verbose_name = "Code"
        verbose_name_plural = "Codes"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )  # OK
    
    used_at = models.DateTimeField(
        verbose_name="Used At",
        blank=True,
        null=True
    )  # OK

    code_value = models.CharField(
        verbose_name="Code Value",
        max_length=16,
        default="",
        unique=True,
    )  # OK
    
    bind_device = models.ForeignKey(
        MewDevice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    
    enabled = models.BooleanField(
        verbose_name="Enabled",
        default=True
    )
    
    bucket = models.ForeignKey(
        MewCodeBucket,
        editable=False,
        default=None,
        on_delete=models.CASCADE
    )

    def __unicode__(self):
        return self.code_value


class MewCertificate(models.Model):
    class Meta(object):
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True
    )
    
    private_key = models.TextField(
        verbose_name="Private Key",
        blank=False
    )
    
    public_key = models.TextField(
        verbose_name="Public Key",
        blank=False
    )
