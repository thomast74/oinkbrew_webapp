import logging
import time

from django.shortcuts import get_object_or_404
from django.views.generic import View

from api.helpers.Core import prepare_brewpi_dic
from api.helpers.Responses import ApiResponse
from api.models import BrewPi, Device
from api.services.BrewPiSerializer import BrewPiSerializer
from api.services.BrewPiConnector import BrewPiConnector
from api.tasks import StatusMessage

logger = logging.getLogger(__name__)


class BrewPiDetail(View):

    def get(self, request, *args, **kwargs):
        logger.info("Get BrewPi detail information for {}".format(kwargs['device_id']))

        pretty = request.GET.get("pretty", "True")
        brewpi = get_object_or_404(BrewPi, device_id=kwargs['device_id'])

        return ApiResponse.json(prepare_brewpi_dic(brewpi), pretty, False)

    def put(self, request, *args, **kwargs):
        command = kwargs['command']

        logger.info("Received PUT request for BrewPi {} with command {}".format(kwargs['device_id'], command))

        brewpi = BrewPiSerializer.from_json(request.body)

        if command == "status":
            self.statusUpdate(brewpi, request)
        elif command == "update":
            self.update(brewpi, request)
        elif command == "reset":
            self.reset(brewpi)

        return ApiResponse.ok()

    def delete(self, request, *args, **kwargs):
        logger.info("Delete BrewPi {}".format(kwargs['device_id']))

        brewpi = get_object_or_404(BrewPi, device_id=kwargs['device_id'])

        tries = 0
        success = False
        while tries < 5:
            success, response = BrewPiConnector.send_reset(brewpi)
            if success:
                break
            time.sleep(0.2)
            tries += 1

        if not success:
            logger.error("BrewPi {} could not be reset: [{}]".format(brewpi.device_id, response))

            return ApiResponse.bad_request("BrewPi {} could not be reset".format(brewpi.device_id))
        else:
            Device.objects.filter(brewpi=brewpi).exclude(device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP).delete()
            Device.objects.filter(brewpi=brewpi, device_type=Device.DEVICE_TYPE_ONEWIRE_TEMP).update(brewpi=None)
            brewpi.delete()

            return ApiResponse.ok()

    def update(self, brewpi, request):
        logger.info("Received BrewPi update request for {}".format(brewpi.device_id))

        brewpi.save()

        return ApiResponse.ok()

    def statusUpdate(self, brewpi, request):
        logger.info("Received BrewPi status request for {}".format(brewpi.device_id))

        brewpi.save()

        StatusMessage.check_if_status_update_required.delay(brewpi.device_id, request.META['SERVER_PORT'])

        return ApiResponse.ok()

    def reset(self, brewpi):
        logger.info("Received BrewPi reset request for {}".format(brewpi.pk))

        tries = 0
        success = False
        while tries < 5:
            success, response = BrewPiConnector.send_reset(brewpi)
            if success:
                break
            time.sleep(0.2)
            tries += 1

        if success:
            brewpi.send_reset()
            brewpi.save()
            return ApiResponse.ok()
        else:
            logger.error("BrewPi {} reset failed: [{}]".format(brewpi.device_id, response))
            return ApiResponse.bad_request("BrewPi {} reset failed: [{}]".format(brewpi.device_id, response))
