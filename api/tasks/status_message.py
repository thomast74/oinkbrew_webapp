from __future__ import absolute_import
from netifaces import interfaces, ifaddresses, AF_INET
import logging
import socket

from celery import shared_task

from api.models.brew_pi_spark import BrewPiSpark
from api.services.spark_connector import Connector


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def check_if_status_update_required(device_id):
    logger.debug("Received status message check task for {}".format(device_id))

    spark = BrewPiSpark.objects.get(device_id=device_id)
    local_ip = get_local_ip()
    if spark.web_address != local_ip:
        Connector().send_spark_info(spark, local_ip)

    return "Ok"


def get_local_ip():
    for interface in interfaces():
        if interface.startswith("eth") or interface.startswith("wlan"):
            try:
                for link in ifaddresses(interface)[AF_INET]:
                    logger.debug("local_ip: {} -> {}".format(interface, link['addr']))
                    return link['addr']
            except:
                logger.debug("Interface {} has no ip address".format(interface))

    return socket.gethostbyname(socket.gethostname())