"""
Custom sensor_state_data enums, based on this discussion:
https://github.com/Bluetooth-Devices/sensor-state-data/pull/51
"""
import sensor_state_data.enum


class SensorDeviceClass(sensor_state_data.BaseDeviceClass):
    # inherited fields

    BATTERY = sensor_state_data.DeviceClass.BATTERY

    SIGNAL_STRENGTH = sensor_state_data.DeviceClass.SIGNAL_STRENGTH

    SPECIFIC_GRAVITY = sensor_state_data.DeviceClass.SPECIFIC_GRAVITY

    TEMPERATURE = sensor_state_data.DeviceClass.TEMPERATURE

    # library-specific fields

    SPECIFIC_GRAVITY_TREND = "specific_gravity_trend"


class Units(sensor_state_data.enum.StrEnum):
    # inherited fields

    PERCENTAGE = sensor_state_data.Units.PERCENTAGE

    SPECIFIC_GRAVITY = sensor_state_data.Units.SPECIFIC_GRAVITY

    SIGNAL_STRENGTH_DECIBELS_MILLIWATT = (
        sensor_state_data.Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    )

    TEMP_CELSIUS = sensor_state_data.Units.TEMP_CELSIUS

    # library-specific fields

    SPECIFIC_GRAVITY_PER_DAY = "SG/d"
