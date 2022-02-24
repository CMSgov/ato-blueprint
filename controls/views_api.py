import json
import logging
from collections import OrderedDict

import structlog
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from structlog import get_logger
from structlog.stdlib import LoggerFactory

from siteapp.models import User

from .models import Deployment, SystemAssessmentResult

logging.basicConfig()

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


@csrf_exempt
def manage_system_assessment_result_api(
    request, system_id, sar_id=None, methods=["GET", "POST"]
):
    """Create or edit system assessment result"""
    #
    # Example curl POST to api
    #  curl --header "Authorization: <api_key>" \
    #  -F "name=test_sar_api" \
    #  -F "system_id=86" \
    #  -F "deployment_id=23" \
    #  -F "data=@controls/data/test_data/test_sar1.json" \
    #  localhost:8000/api/v1/systems/86/assessment/new
    #

    # Get user from API key.
    api_key = request.META.get("HTTP_AUTHORIZATION", "").strip()
    if (
        len(api_key) < 32
    ):  # prevent null values from matching against users without api keys
        return JsonResponse(
            OrderedDict(
                [
                    ("status", "error"),
                    (
                        "error",
                        "An API key was not present in the Authorization header.",
                    ),
                ]
            ),
            json_dumps_params={"indent": 2},
            status=403,
        )
    # Check API key permissions and get user
    from django.db.models import Q

    # from siteapp.models import User, Project
    try:
        User.objects.get(
            Q(api_key_rw=api_key) | Q(api_key_ro=api_key) | Q(api_key_wo=api_key)
        )
    except User.DoesNotExist:
        return JsonResponse(
            OrderedDict(
                [
                    ("status", "error"),
                    (
                        "error",
                        "A valid API key was not present in the Authorization header.",
                    ),
                ]
            ),
            json_dumps_params={"indent": 2},
            status=403,
        )

    sar = json.loads(request.POST.get("sar_json"))

    if request.method == "POST":
        deployment_uuid = request.POST.get("deployment_uuid")
        if deployment_uuid is None or deployment_uuid == "None":
            # When deployment is not defined, leave blank and attach SAR to system only
            deployment = None
            deployment_id = None
        else:
            deployment = Deployment.objects.get(uuid=deployment_uuid)
            deployment_id = deployment.id
        # TODO Make sure deployment is associated with system

        sar = SystemAssessmentResult(
            name=sar["metadata"]["title"],
            description=sar["metadata"]["description"],
            system_id=request.POST.get("system_id"),
            deployment_id=deployment_id,
            assessment_results=sar,
        )
        sar.save()
        logger.info(
            event="create_system_assessment_result",
            object={
                "object": "system_assessment_result",
                "id": sar.id,
                "name": sar.name,
            },
        )

    # Send simple response
    # TODO: Improve the response
    ok = True
    return JsonResponse(
        OrderedDict(
            [
                ("status", "ok" if ok else "error"),
                # ("details", log),
            ]
        ),
        json_dumps_params={"indent": 2},
    )
