"""Summary

Attributes:
    FGC_MAX_DEV_LEN (int): Maximum FGC device name length in chars
    FGC_STATSRV_FGCD_SIZE (TYPE): Size of the whole status data
    FGC_STATSRV_HEADER_SIZE (TYPE): Status server header size
    FGC_STATUS_SIZE (int): Size of status block for a device
    FGCD_MAX_DEVS (int): Maximum number of FGC devices per gateway
    HOST_NAME_MAX (int): Maximum size of a hostname in chars (including null and padding)
    STATUS_SERVER_FGC (str): Name of the FGC device in the status server
"""

# Imports
import importlib
import os
import re
import struct 

import pyfgc
import pyfgc_decoders
from pyfgc_const import FGC_MAX_DEV_LEN, FGCD_MAX_DEVS, FGC_STATUS_SIZE

# Constants
HOST_NAME_MAX                  = 68
DATA_RECEPTION_TIMESTAMP_BYTES = 8
FGC_UDP_HEADER_BYTES           = 16
TIME_SEC_BYTES                 = 4
TIME_USEC_BYTES                = 4

FGC_STATSRV_HEADER_SIZE = ((FGC_MAX_DEV_LEN + 1)
                        * FGCD_MAX_DEVS           
                        + HOST_NAME_MAX
                        + DATA_RECEPTION_TIMESTAMP_BYTES
                        + FGC_UDP_HEADER_BYTES
                        + TIME_SEC_BYTES
                        + TIME_USEC_BYTES)
FGC_STATSRV_FGCD_SIZE = FGC_STATSRV_HEADER_SIZE + FGCD_MAX_DEVS * FGC_STATUS_SIZE                                                                
STATUS_SERVER_FGC = "FGC_STATUS"


# API

def get_status_device(device_name: str, decode_only_common: bool = False, fgc_session: pyfgc.FgcSession = None) -> dict:
    """Summary
    
    Args:
        device_name (str): Description
        decode_only_common (bool, optional): Description
    
    Returns:
        dict: Description
    """
    try:
        fgc_res = fgc_session.get(device_name)
    
    except AttributeError:
        fgc_res = pyfgc.get(STATUS_SERVER_FGC, device_name)

    all_devices_in_gw = _decode_status(fgc_res, 0, decode_only_common)
    header_keys       = ["hostname", "recv_time_sec", "recv_time_usec", "id", "sequence", "send_time_sec", "send_time_usec", "time_sec", "time_usec"]
    fgc_status        = dict()
    for k in header_keys:
        fgc_status.update({k:all_devices_in_gw[k]})
    
    fgc_status.update({device_name:all_devices_in_gw["devices"][device_name]})
    return fgc_status


def get_status_all(decode_only_common: bool = False, fgc_session: pyfgc.FgcSession = None) -> dict:
    """Summary
    
    Args:
        decode_only_common (bool, optional): Description
    """
    try:
        fgc_res = fgc_session.get("ALL")

    except AttributeError:
        fgc_res = pyfgc.get(STATUS_SERVER_FGC, "ALL")
    
    fgcds = dict()
    offset = 0

    for _ in range(len(fgc_res.value)//FGC_STATSRV_FGCD_SIZE):
        status = _decode_status(fgc_res, offset, decode_only_common)

        try:
            fgcds[status["hostname"]] = status

        except KeyError:
            pass

        offset += FGC_STATSRV_FGCD_SIZE

    return fgcds

def _decode_header(status_dict, names_list, data):

    names_list = [name[0].split(b"\x00", 1)[0] for name in 
        struct.iter_unpack(f"{FGC_MAX_DEV_LEN + 1}s", 
                            data[0 : FGCD_MAX_DEVS * (FGC_MAX_DEV_LEN + 1)])]

    offset = FGCD_MAX_DEVS * (FGC_MAX_DEV_LEN + 1)

    (status_dict["hostname"], 
        status_dict["recv_time_sec"],
        status_dict["recv_time_usec"], 
        status_dict["id"],
        status_dict["sequence"],
        status_dict["send_time_sec"],
        status_dict["send_time_usec"],
        status_dict["time_sec"],
        status_dict["time_usec"]) = struct.unpack(f"!{HOST_NAME_MAX}sllllllll", 
                                                    data[offset:])

    status_dict["hostname"] = status_dict["hostname"].split(b"\x00", 1)[0].decode()

    if not status_dict["hostname"]:
        status_dict.clear()
        return None

    return status_dict, names_list

def _decode_device_data(status_dict, names_list, data, decode_only_common):
    status_dict["channels"] = dict()
    status_dict["devices"] = dict()

    offset_udp_header_bytes = 0

    for dev_number in range(FGCD_MAX_DEVS):
        offset = dev_number * FGC_STATUS_SIZE + offset_udp_header_bytes
        dev_data = data[offset : offset+FGC_STATUS_SIZE]

        class_id = dev_data[1]

        try:
            device_info = (decode_only_common
                        and pyfgc_decoders.decoders["common"](dev_data)
                        or  pyfgc_decoders.decoders[class_id](dev_data))

        except KeyError:
            device_info = pyfgc_decoders.decoders["common"](dev_data)

        device_info["CHANNEL"] = dev_number
        device_name = names_list[dev_number] and names_list[dev_number].decode() or None

        if device_name is not None:
            device_info["NAME"] = device_name
            status_dict["channels"][dev_number] = device_info
            status_dict["devices"][device_name] = device_info

    return status_dict

def _decode_status(fgc_res, offset, decode_only_common):
    status = dict()
    names = list()

    # There are four bytes at the beginning that are not taken into account in the PERL version
    # What do they account for? Ignore them for the time being
    offset += 4
    status, names = _decode_header(
      status,
      names,
      fgc_res.value[offset : offset+FGC_STATSRV_HEADER_SIZE]
    )

    offset += FGC_STATSRV_HEADER_SIZE

    status = _decode_device_data(status, names, fgc_res.value[offset:], decode_only_common)

    return status

