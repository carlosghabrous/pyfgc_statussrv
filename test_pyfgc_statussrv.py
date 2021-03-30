import pytest

import pyfgc
import pyfgc_statussrv

TEST_DEVICE = "RPZES.866.15.ETH1"

@pytest.fixture
def get_test_data():
    sta = pyfgc_statussrv.get_status_device(TEST_DEVICE)
    data = list()

    with pyfgc.fgcs(TEST_DEVICE, "sync"):
        data.append((int(pyfgc.get("FIELDBUS.ID")), sta["devices"][TEST_DEVICE]["CHANNEL"]))
        data.append((int(pyfgc.get("DEVICE.CLASS_ID")), sta["devices"][TEST_DEVICE]["CLASS_ID"]))
        data.append((pyfgc.get("DEVICE.NAME"), sta["devices"][TEST_DEVICE]["NAME"]))
        data.append((pyfgc.get("STATUS.ST_LATCHED"), sta["devices"][TEST_DEVICE]["ST_LATCHED"]))
        data.append((pyfgc.get("STATUS.ST_UNLATCHED"), sta["devices"][TEST_DEVICE]["ST_UNLATCHED"]))
        data.append((float(pyfgc.get("MEAS.I")), sta["devices"][TEST_DEVICE]["I_MEAS"]))
        data.append((float(pyfgc.get("MEAS.V")), sta["devices"][TEST_DEVICE]["V_MEAS"]))

    return data


test_data = get_test_data()

@pytest.mark.parametrize("expected, test_value", test_data)  
def test_statussrv_device(expected, test_value):
    """Summary
    """
    assert expected == test_value

@pytest.mark.parametrize("expected, test_value", test_data)
def test_statussrv_all(expected, test_value):
    """Summary
    """
    status_data = pyfgc_statussrv.get_status_all()
    sta_cfc_866_reth1 = status_data["cfc-866-reth1"]

    assert sta_cfc_866_reth1 != None or dict()
    assert expected == test_value
