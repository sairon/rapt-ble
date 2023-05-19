import logging
import struct

import pytest
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import (
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
)

from rapt_ble.custom_state_data import DeviceClass, Units
from rapt_ble.parser import RAPTPillBluetoothDeviceData


@pytest.fixture(autouse=True)
def logging_config(caplog):
    caplog.set_level(logging.DEBUG)


def bytes_to_service_info(payload: bytes) -> BluetoothServiceInfo:
    manufacturer_data = {}
    (manufacturer_id,) = struct.unpack("<H", payload[:2])
    manufacturer_data[manufacturer_id] = payload[2:]

    return BluetoothServiceInfo(
        name="",
        address="00:11:22:33:44:55",
        rssi=-60,
        manufacturer_data=manufacturer_data,
        service_data={},
        service_uuids=[],
        source="local",
    )


@pytest.mark.parametrize(
    "data_bytes",
    [
        # payload v1
        b"RAPT\x01x\xe3m<\xb9\x94\x94\x8bD|\xb9\xf64E\x02b&w*\xac",
        # payload v2 - invalid gravity velocity
        b"RAPT\x02\x00\x00\x00\x00\x00\x00\x94\x8bD|\xb9\xf64E\x02b&w*\xac",
        # payload v2 - valid gravity velocity
        b"RAPT\x02\x00\x01\xc1\x6d\x26\x14\x92\x6b\x44\x7f\x52\xc9\x31\xc9\x02\x2d\x29\x97\x3f\x46",
        b"RAPTdPillG1",
        b"KEG20220612_050156_81c6d1",
    ],
)
def test_device_supported(data_bytes):
    device = RAPTPillBluetoothDeviceData()

    data = bytes_to_service_info(data_bytes)

    assert device.supported(data)


def test_parse_version():
    device = RAPTPillBluetoothDeviceData()
    data = bytes_to_service_info(b"KEG20220612_050156_81c6d1")
    device.update(data)
    assert device._get_device_info(None).sw_version == "20220612_050156_81c6d1"


def test_parse_metrics_v1():
    device = RAPTPillBluetoothDeviceData()
    data = bytes_to_service_info(
        b"RAPT\x01x\xe3m<\xb9\x94\x94\x8bD|\xb9\xf64E\x02b&w*\xac"
    )
    result = device.update(data)
    assert result == SensorUpdate(
        title="RAPT Pill 4455",
        devices={
            None: SensorDeviceInfo(
                name="RAPT Pill 4455",
                manufacturer="RAPT",
                model="RAPT Pill hydrometer",
                hw_version=None,
                sw_version=None,
            ),
        },
        entity_descriptions={
            DeviceKey(key="specific_gravity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="specific_gravity", device_id=None),
                device_class=DeviceClass.SPECIFIC_GRAVITY,
                native_unit_of_measurement=Units.SPECIFIC_GRAVITY,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=DeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="specific_gravity", device_id=None): SensorValue(
                device_key=DeviceKey("specific_gravity", device_id=None),
                name="Specific Gravity",
                native_value=1.0109,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=23.94,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=43,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
        },
    )


def test_parse_metrics_v2():
    device = RAPTPillBluetoothDeviceData()
    data = bytes_to_service_info(
        b"RAPT\x02\x00\x01\xc1\x6d\x26\x14\x92\x6b\x44\x7f\x52\xc9\x31\xc9\x02\x2d\x29\x97\x3f\x46",
    )
    result = device.update(data)
    assert result == SensorUpdate(
        title="RAPT Pill 4455",
        devices={
            None: SensorDeviceInfo(
                name="RAPT Pill 4455",
                manufacturer="RAPT",
                model="RAPT Pill hydrometer",
                hw_version=None,
                sw_version=None,
            ),
        },
        entity_descriptions={
            DeviceKey(key="specific_gravity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="specific_gravity", device_id=None),
                device_class=DeviceClass.SPECIFIC_GRAVITY,
                native_unit_of_measurement=Units.SPECIFIC_GRAVITY,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=DeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="specific_gravity_velocity", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="specific_gravity_velocity", device_id=None),
                device_class=DeviceClass.SPECIFIC_GRAVITY_VELOCITY,
                native_unit_of_measurement=Units.SPECIFIC_GRAVITY_POINTS_PER_DAY,
            ),
        },
        entity_values={
            DeviceKey(key="specific_gravity", device_id=None): SensorValue(
                device_key=DeviceKey("specific_gravity", device_id=None),
                name="Specific Gravity",
                native_value=1.0213,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=19.69,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=63,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="specific_gravity_velocity", device_id=None): SensorValue(
                device_key=DeviceKey("specific_gravity_velocity", device_id=None),
                name="Specific Gravity Velocity",
                native_value=-14.821796417236328,
            ),
        },
    )


def test_parse_metrics_v2_no_velocity():
    device = RAPTPillBluetoothDeviceData()
    data = bytes_to_service_info(
        b"RAPT\x02\x00\x00\x00\x00\x00\x00\x94\x8bD|\xb9\xf64E\x02b&w*\xac",
    )
    result = device.update(data)
    assert result == SensorUpdate(
        title="RAPT Pill 4455",
        devices={
            None: SensorDeviceInfo(
                name="RAPT Pill 4455",
                manufacturer="RAPT",
                model="RAPT Pill hydrometer",
                hw_version=None,
                sw_version=None,
            ),
        },
        entity_descriptions={
            DeviceKey(key="specific_gravity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="specific_gravity", device_id=None),
                device_class=DeviceClass.SPECIFIC_GRAVITY,
                native_unit_of_measurement=Units.SPECIFIC_GRAVITY,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=DeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(
                key="specific_gravity_velocity", device_id=None
            ): SensorDescription(
                device_key=DeviceKey(key="specific_gravity_velocity", device_id=None),
                device_class=DeviceClass.SPECIFIC_GRAVITY_VELOCITY,
                native_unit_of_measurement=Units.SPECIFIC_GRAVITY_POINTS_PER_DAY,
            ),
        },
        entity_values={
            DeviceKey(key="specific_gravity", device_id=None): SensorValue(
                device_key=DeviceKey("specific_gravity", device_id=None),
                name="Specific Gravity",
                native_value=1.0109,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=23.94,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=43,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="specific_gravity_velocity", device_id=None): SensorValue(
                device_key=DeviceKey("specific_gravity_velocity", device_id=None),
                name="Specific Gravity Velocity",
                native_value=None,
            ),
        },
    )
