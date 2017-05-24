# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import re
import time
import hashlib
import rsa
from base64 import b64encode, b64decode

from django.http import HttpResponse

from MewApi.models import *


# Create your views here.


def api_bind(request):
    result = {}
    if request.method == "POST":
        post = request.POST
        required_check = True
        missing_field = ""
        required_field_list = ["code", "unique_id", "version", "checksum", "ts"]
        for required_field in required_field_list:
            if required_field not in post:
                required_check = False
                missing_field = required_field
        if required_check:
            certificate = MewCertificate.objects.latest("checksum_salt")
            checksum_output = hashlib.sha1("version=%s&unique_id=%s&code=%s&ts=%s%s" % (post["version"], post["unique_id"], post["code"], post["ts"], certificate.checksum_salt)).hexdigest()
            if checksum_output == post["checksum"]:
                timestamp = post["ts"]
                if abs(int(timestamp) - time.time()) < 3600:
                    version = post["version"]
                    version_m = MewVersion.objects.filter(version_string=version)
                    if len(version_m) != 0:
                        code = post["code"].upper()
                        regex_code = re.compile("^[0-9A-Za-z]{12}$")
                        unique_id = post["unique_id"]
                        regex_unique_id = re.compile("^[0-9A-Fa-f]{40}$")
                        field_dismatch = ""
                        if not regex_code.match(code):
                            field_dismatch = "code"
                        elif not regex_unique_id.match(unique_id):
                            field_dismatch = "unique_id"
                        if regex_code.match(code) and regex_unique_id.match(unique_id):
                            code_m = MewCode.objects.filter(code_value=code)
                            if len(code_m) != 0:
                                code_n = code_m[0]
                                if code_n.enabled:
                                    if code_n.bind_device is None:
                                        old_device_m = MewDevice.objects.filter(unique_id=unique_id)
                                        if len(old_device_m) == 0:
                                            new_device = MewDevice()
                                            new_device.unique_id = unique_id
                                            new_device.related_user = code_n.related_user
                                            new_device.save()
                                            code_n.bind_device = new_device
                                            code_n.used_at = datetime.datetime.now()
                                            code_n.save()
                                            sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                            identify = json.dumps({
                                                "code": code_n.code_value,
                                                "unique_id": new_device.unique_id,
                                                "deadline": sec_used_at + 2592000,
                                            })
                                            result.update({
                                                "result": "succeed",
                                                "status": 200,
                                                "code": code_n.code_value,
                                                "unique_id": new_device.unique_id,
                                                "used_at": sec_used_at,
                                                "message": "授权码 %s 已成功绑定至 "
                                                           "设备 %s。" % (code, unique_id),
                                                "deadline": sec_used_at + 2592000,
                                                "identify": identify
                                            })  # bind new
                                            priv_key = rsa.importkey(certificate.private_key)
                                            sign_content = b64encode(rsa.sign(identify, priv_key, "SHA-1"))
                                            result.update({"signature": sign_content})
                                        else:
                                            old_device_n = old_device_m[0]
                                            if old_device_n.enabled:
                                                old_device_n.related_user = code_n.related_user
                                                old_device_n.save()
                                                code_n.bind_device = old_device_n
                                                code_n.used_at = datetime.datetime.now()
                                                code_n.save()
                                                sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                                identify = json.dumps({
                                                    "code": code_n.code_value,
                                                    "unique_id": old_device_n.unique_id,
                                                    "deadline": sec_used_at + 2592000,
                                                })
                                                result.update({
                                                    "result": "succeed",
                                                    "status": 201,
                                                    "code": code_n.code_value,
                                                    "unique_id": old_device_n.unique_id,
                                                    "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                                    "message": "授权码 '%s' 已成功绑定至 "
                                                               "设备 '%s'。" % (code, unique_id),
                                                    "deadline": sec_used_at + 2592000,
                                                    "identify": identify
                                                })  # change code
                                                priv_key = rsa.importkey(certificate.private_key)
                                                sign_content = b64encode(rsa.sign(identify, priv_key, "SHA-1"))
                                                result.update({"signature": sign_content})
                                            else:
                                                result.update({"result": "error", "status": 403,
                                                               "message": "授权码 '%s' 无法 "
                                                                          "绑定至该设备，可能是该设备已被禁用。" % code})
                                    else:
                                        if code_n.bind_device.unique_id == unique_id:
                                            if code_n.bind_device.enabled is True:
                                                sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                                identify = json.dumps({
                                                    "code": code_n.code_value,
                                                    "unique_id": code_n.bind_device.unique_id,
                                                    "deadline": sec_used_at + 2592000,
                                                })
                                                result.update({
                                                    "result": "succeed",
                                                    "status": 202,
                                                    "code": code_n.code_value,
                                                    "unique_id": code_n.bind_device.unique_id,
                                                    "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                                    "message": "授权码 '%s' 已成功绑定至 "
                                                               "设备 '%s'。" % (code, unique_id),
                                                    "deadline": sec_used_at + 2592000,
                                                    "identify": identify
                                                })  # already binded
                                                priv_key = rsa.importkey(certificate.private_key)
                                                sign_content = b64encode(rsa.sign(identify, priv_key, "SHA-1"))
                                                result.update({"signature": sign_content})
                                            else:
                                                result.update({"result": "error", "status": 403,
                                                               "message": "授权码 '%s' 无法 "
                                                                          "绑定至该设备，可能是该设备已被禁用。" % code})
                                        else:
                                            result.update({"result": "error", "status": 403,
                                                           "message": "授权码 '%s' 已经 "
                                                                      "绑定至其它设备。" % code})
                                else:
                                    result.update(
                                        {"result": "error", "status": 403, "message": "授权码 '%s' "
                                                                                      "目前不可用。" % code})
                            else:
                                result.update({"result": "error", "status": 404,
                                               "message": "找不到有效授权 '%s'。" % code})
                        else:
                            result.update({"result": "error", "status": 400, "message": "Field `%s` is invalid." % field_dismatch})
                    else:
                        result.update({"result": "error", "status": 400,
                                       "message": "版本号 '%s' 目前不可用。" % version})
                else:
                    result.update({"result": "error", "status": 400, "message": "Invalid value of `timestamp`."})
            else:
                result.update({"result": "error", "status": 400, "message": "Invalid value of `checksum`."})
        else:
            result.update({"result": "error", "status": 400, "message": "Field `%s` is missing." % missing_field})
    else:
        result.update({"result": "error", "status": 400, "message": "Method '%s' is not allowed." % request.method})
    result.update({"timestamp": int(time.time())})
    return HttpResponse(json.dumps(result), content_type='application/json')


def api_check(request):
    result = {}
    if request.method == "POST":
        post = request.POST
        required_check = True
        missing_field = ""
        required_field_list = ["unique_id", "version", "ts", "checksum"]
        for required_field in required_field_list:
            if required_field not in post:
                required_check = False
                missing_field = required_field
        if required_check:
            certificate = MewCertificate.objects.latest("checksum_salt")
            checksum_output = hashlib.sha1("version=%s&unique_id=%s&ts=%s%s" % (post["version"], post["unique_id"], post["ts"], certificate.checksum_salt)).hexdigest()
            if checksum_output == post["checksum"]:
                timestamp = post["ts"]
                if abs(int(timestamp) - time.time()) < 3600:
                    version = post["version"]
                    version_m = MewVersion.objects.filter(version_string=version)
                    if len(version_m) != 0:
                        unique_id = post["unique_id"]
                        regex_unique_id = re.compile("^[0-9A-Fa-f]{40}$")
                        field_dismatch = ""
                        if not regex_unique_id.match(unique_id):
                            field_dismatch = "unique_id"
                        if regex_unique_id.match(unique_id):
                            device = MewDevice.objects.filter(unique_id=unique_id)
                            if len(device) != 0:
                                device_m = device[0]
                                valid_codes = MewCode.objects.filter(bind_device=device_m, used_at__gt=datetime.datetime.fromtimestamp(time.time() - 2592000))
                                if len(valid_codes) != 0:
                                    code_n = valid_codes[0]
                                    if code_n.enabled:
                                        sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                        identify = json.dumps({
                                            "code": code_n.code_value,
                                            "unique_id": device_m.unique_id,
                                            "deadline": sec_used_at + 2592000,
                                        })
                                        result.update({
                                            "result": "succeed",
                                            "status": 202,
                                            "code": code_n.code_value,
                                            "unique_id": device_m.unique_id,
                                            "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                            "message": "授权码 '%s' 已成功绑定至 "
                                                       "设备 '%s'。" % (code_n.code_value, unique_id),
                                            "deadline": sec_used_at + 2592000,
                                            "identify": identify
                                        })  # already binded
                                        priv_key = rsa.importkey(certificate.private_key)
                                        sign_content = b64encode(rsa.sign(identify, priv_key, "SHA-1"))
                                        result.update({"signature": sign_content})
                                    else:
                                        result.update(
                                            {"result": "error", "status": 403, "message": "授权码 '%s' "
                                                                                          "目前不可用。" % code_n.code_value})
                                else:
                                    result.update({"result": "error", "status": 405,
                                                   "message": "设备 '%s' 授权已过期，请输入新授权码进行续费。" % unique_id})
                            else:
                                result.update({"result": "error", "status": 404,
                                               "message": "设备 '%s' 尚未授权，请输入授权码进行首次激活。" % unique_id})
                        else:
                            result.update({"result": "error", "status": 400, "message": "Field `%s` is invalid." % field_dismatch})
                    else:
                        result.update({"result": "error", "status": 400,
                                       "message": "版本号 '%s' 目前不可用。" % version})
                else:
                    result.update({"result": "error", "status": 400, "message": "Invalid value of `timestamp`."})
            else:
                result.update({"result": "error", "status": 400, "message": "Invalid value of `checksum`."})
        else:
            result.update({"result": "error", "status": 400, "message": "Field `%s` is missing." % missing_field})
    else:
        result.update({"result": "error", "message": "Method %s is not allowed." % request.method})
    result.update({"timestamp": int(time.time())})
    return HttpResponse(json.dumps(result), content_type='application/json')
