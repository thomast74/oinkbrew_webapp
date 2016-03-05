import logging
import sys

from django.views.generic import View
from django.shortcuts import get_object_or_404, get_list_or_404

from api.helpers.Core import prepare_configuration_dic
from api.helpers.Responses import ApiResponse
from api.models import BrewPi, Configuration
from api.services.BrewPiConnector import BrewPiConnector
from api.views.ConfigurationDetail import ConfigurationDetail

logger = logging.getLogger(__name__)


class ConfigurationList(View):

    def get(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        pretty = request.GET.get("pretty", "True")

        logger.info("Get all configurations for BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        configurations = get_list_or_404(Configuration, brewpi=brewpi)

        configs_arr = []
        for configuration in configurations:
            configs_arr.append(prepare_configuration_dic(configuration))

        return ApiResponse.json(configs_arr, pretty, False)

    def post(self, request, *args, **kwargs):
        device_id = kwargs['device_id']
        logger.info("New configuration received for BrewPi {}".format(device_id))

        brewpi = get_object_or_404(BrewPi, device_id=device_id)
        config_dic = ConfigurationDetail.convert_json_data(request.body)

        configuration = ConfigurationDetail.create_configuration(brewpi, config_dic)

        try:
            ConfigurationDetail.assign_device_function(brewpi, configuration, config_dic, False)

            configuration.heat_actuator_id = ConfigurationDetail.get_sensor_or_actuator("heat_actuator", False,
                                                                                        configuration, config_dic)
            configuration.temp_sensor_id = ConfigurationDetail.get_sensor_or_actuator("temp_sensor", False,
                                                                                      configuration, config_dic)

            if configuration.type == Configuration.CONFIG_TYPE_FERMENTATION:
                configuration.fan_actuator_id = ConfigurationDetail.get_sensor_or_actuator("fan_actuator", False,
                                                                                           configuration, config_dic)
                configuration.cool_actuator_id = ConfigurationDetail.get_sensor_or_actuator("cool_actuator", False,
                                                                                            configuration, config_dic)

            configuration.save()
            ConfigurationDetail.store_phase(configuration, config_dic.get("phase"))

            tries = 0
            success = False
            while tries < 5:
                success = BrewPiConnector.send_configuration(brewpi, configuration)
                if success:
                    break
                tries += 1

            if success:
                return ApiResponse.message('"ConfigId":"{}"'.format(configuration.pk))
            else:
                ConfigurationDetail.delete_configuration(device_id, configuration.pk)
                return ApiResponse.bad_request("BrewPi could not be updated")
        except:
            ConfigurationDetail.delete_configuration(device_id, configuration.pk)
            return ApiResponse.bad_request(sys.exc_info()[1])