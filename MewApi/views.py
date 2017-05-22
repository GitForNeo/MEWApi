import datetime
import json
import re
import time

from django.http import HttpResponse

from MewApi.models import *


# Create your views here.


def api_bind(request):
    result = {}
    if request.method == "POST":
        post = request.POST
        required_check = True
        missing_field = ""
        required_field_list = ["code", "unique_id", "version"]
        for required_field in required_field_list:
            if required_field not in post:
                required_check = False
                missing_field = required_field
        if required_check:
            version = post["version"]
            version_m = MewVersion.objects.filter(version_string=version)
            if len(version_m) != 0:
                code = post["code"]
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
                                    new_device.save()
                                    code_n.bind_device = new_device
                                    code_n.used_at = datetime.datetime.now()
                                    code_n.save()
                                    sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                    result.update({
                                        "result": "succeed",
                                        "status": 200,
                                        "code": code_n.code_value,
                                        "unique_id": new_device.unique_id,
                                        "used_at": sec_used_at,
                                        "message": "`Code`.`code_value` %s has been successfully "
                                                   "binded to the new `Device`.`unique_id` %s." % (code, unique_id),
                                        "deadline": sec_used_at + 2592000
                                    })  # bind new
                                else:
                                    old_device_n = old_device_m[0]
                                    if old_device_n.enabled:
                                        code_n.bind_device = old_device_n
                                        code_n.used_at = datetime.datetime.now()
                                        code_n.save()
                                        sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                        result.update({
                                            "result": "succeed",
                                            "status": 201,
                                            "code": code_n.code_value,
                                            "unique_id": old_device_n.unique_id,
                                            "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                            "message": "`Code`.`code_value` '%s' has been successfully "
                                                       "binded to an old `Device`.`unique_id` '%s'." % (code, unique_id),
                                            "deadline": sec_used_at + 2592000
                                        })  # change code
                                    else:
                                        result.update({"result": "error", "status": 403,
                                                       "message": "`Code`.`code_value` '%s' cannot "
                                                                  "be binded to this device." % code})
                            else:
                                if code_n.bind_device.unique_id == unique_id:
                                    if code_n.bind_device.enabled is True:
                                        sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                                        result.update({
                                            "result": "succeed",
                                            "status": 202,
                                            "code": code_n.code_value,
                                            "unique_id": code_n.bind_device.unique_id,
                                            "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                            "message": "`Code`.`code_value` '%s' is already binded "
                                                       "to the `Device`.`unique_id` '%s'." % (code, unique_id),
                                            "deadline": sec_used_at + 2592000
                                        })  # already binded
                                    else:
                                        result.update({"result": "error", "status": 403,
                                                       "message": "`Code`.`code_value` '%s' cannot "
                                                                  "be binded to this device." % code})
                                else:
                                    result.update({"result": "error", "status": 403,
                                                   "message": "`Code`.`code_value` '%s' has "
                                                              "been binded by another device." % code})
                        else:
                            result.update(
                                {"result": "error", "status": 403, "message": "`Code`.`code_value` '%s' "
                                                                              "is not available now." % code})
                    else:
                        result.update({"result": "error", "status": 404,
                                       "message": "Cannot find `Code`.`code_value` equals '%s'." % code})
                else:
                    result.update({"result": "error", "status": 400, "message": "Field `%s` is invalid." % field_dismatch})
            else:
                result.update({"result": "error", "status": 400,
                               "message": "Cannod find `Version`.`version_string` equals '%s'." % version})
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
        required_field_list = ["unique_id", "version"]
        for required_field in required_field_list:
            if required_field not in post:
                required_check = False
                missing_field = required_field
        if required_check:
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
                            sec_used_at = int(time.mktime(code_n.used_at.timetuple()))
                            result.update({
                                "result": "succeed",
                                "status": 202,
                                "code": code_n.code_value,
                                "unique_id": device_m.unique_id,
                                "used_at": int(time.mktime(code_n.used_at.timetuple())),
                                "message": "`Code`.`code_value` '%s' is already binded "
                                           "to the `Device`.`unique_id` '%s'." % (code_n.code_value, unique_id),
                                "deadline": sec_used_at + 2592000
                            })  # already binded
                        else:
                            result.update({"result": "error", "status": 405,
                                           "message": "No matching valid `Code` for `Device`.`unique_id` '%s'." % unique_id})
                    else:
                        result.update({"result": "error", "status": 404,
                                       "message": "Cannot find `Device`.`unique_id` equals '%s'." % unique_id})
                else:
                    result.update({"result": "error", "status": 400, "message": "Field `%s` is invalid." % field_dismatch})
            else:
                result.update({"result": "error", "status": 400,
                               "message": "Cannod find `Version`.`version_string` equals '%s'." % version})
        else:
            result.update({"result": "error", "status": 400, "message": "Field `%s` is missing." % missing_field})
    else:
        result.update({"result": "error", "message": "Method %s is not allowed." % request.method})
    result.update({"timestamp": int(time.time())})
    return HttpResponse(json.dumps(result), content_type='application/json')
