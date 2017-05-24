# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class MewVersion(models.Model):
    class Meta(object):
        verbose_name = "版本"
        verbose_name_plural = "版本"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )  # OK
    
    version_string = models.CharField(
        verbose_name="版本号",
        max_length=16,
        default=""
    )
    
    enabled = models.BooleanField(
        verbose_name="启用",
        default=True
    )

    def __unicode__(self):
        return self.version_string


class MewDevice(models.Model):
    class Meta(object):
        verbose_name = "设备"
        verbose_name_plural = "设备"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )  # OK
    
    unique_id = models.CharField(
        verbose_name="设备号",
        max_length=40,
        default="",
        unique=True,
    )  # OK
    
    enabled = models.BooleanField(
        verbose_name="启用",
        default=True
    )

    related_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        verbose_name="所有者"
    )

    def __unicode__(self):
        return self.unique_id


class MewCodeBucket(models.Model):
    class Meta(object):
        verbose_name = "授权池"
        verbose_name_plural = "授权池"
    
    id = models.AutoField(
        primary_key=True,
        editable=False
    )
    
    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )
    
    name = models.CharField(
        verbose_name="名称",
        max_length=64,
        unique=True,
        default="未命名授权池"
    )
    
    code_count = models.IntegerField(
        verbose_name="数量",
        default=100,
        help_text="当前兑换比率: 100 点数 = 1 授权"
    )
    
    code_export = models.TextField(
        verbose_name="导出",
        blank=True
    )

    related_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        verbose_name="所有者"
    )
    
    def __unicode__(self):
        return self.name


class MewCode(models.Model):
    class Meta(object):
        verbose_name = "授权"
        verbose_name_plural = "授权"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )  # OK
    
    used_at = models.DateTimeField(
        verbose_name="使用时间",
        blank=True,
        null=True
    )  # OK

    code_value = models.CharField(
        verbose_name="授权码",
        max_length=16,
        default="",
        unique=True
    )  # OK
    
    bind_device = models.ForeignKey(
        MewDevice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="关联设备"
    )
    
    enabled = models.BooleanField(
        verbose_name="启用",
        default=True
    )
    
    bucket = models.ForeignKey(
        MewCodeBucket,
        editable=False,
        default=None,
        on_delete=models.CASCADE,
        verbose_name="授权池"
    )

    related_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        verbose_name="所有者"
    )

    def __unicode__(self):
        return self.code_value


class MewCertificate(models.Model):
    class Meta(object):
        verbose_name = "证书"
        verbose_name_plural = "证书"

    id = models.AutoField(
        primary_key=True,
        editable=False
    )

    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )
    
    private_key = models.TextField(
        verbose_name="私钥",
        blank=False,
        default=""
    )
    
    public_key = models.TextField(
        verbose_name="公钥",
        blank=False,
        default=""
    )
    
    checksum_salt = models.TextField(
        verbose_name="盐",
        blank=False,
        default=""
    )


class MewAgentPointRecord(models.Model):
    class Meta(object):
        verbose_name = "代理点数"
        verbose_name_plural = "代理点数"
    
    id = models.AutoField(
        primary_key=True,
        editable=False
    )
    
    created_at = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True
    )
    
    related_user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="所有者"
    )
    
    points = models.IntegerField(
        default=0,
        verbose_name="点数"
    )

    def __unicode__(self):
        return self.related_user.username + "(" + unicode(self.points) + ")"
