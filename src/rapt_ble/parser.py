import logging
from binascii import hexlify
from collections import namedtuple
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import DeviceClass, SensorLibrary, Units

_LOGGER = logging.getLogger(__name__)


RAPTPillMetrics = namedtuple(
    "RAPTPillMetrics", "version, mac, temperature, gravity, x, y, z, battery"
)


class RAPTPillBluetoothDeviceData(BluetoothData):
    """Data update for RAPT Bluetooth devices"""

    def _process_metrics(self, data: bytes) -> None:
        """
        Process advertisement with metrics.

        This is what the advertisement data payload looks like in C,
        endianness is big endian:

        typedef struct __attribute__((packed)) {
            char prefix[4];        // RAPT
            uint8_t version;       // always 0x01
            uint8_t mac[6];
            uint16_t temperature;  // x / 128 - 273.15
            float gravity;         // / 1000
            int16_t x;             // x / 16
            int16_t y;             // x / 16
            int16_t z;             // x / 16
            int16_t battery;       // x / 256
        } RAPTPillMetrics;
        """
        if len(data) != 23:
            raise ValueError("Metrics data must have length 23")

        # get "raw" data, drop second part of the prefix ("PT"), start with the version
        metrics_raw = RAPTPillMetrics._make(unpack(">B6sHfhhhh", data[2:]))

        # convert to actual metrics
        metrics = RAPTPillMetrics(
            version=metrics_raw.version,
            mac=hexlify(metrics_raw.mac).decode("ascii"),
            temperature=round(metrics_raw.temperature / 128 - 273.15, 2),
            gravity=round(metrics_raw.gravity / 1000, 4),
            x=metrics_raw.x / 16,
            y=metrics_raw.y / 16,
            z=metrics_raw.z / 16,
            battery=round(metrics_raw.battery / 256),
        )

        if metrics.version != 1:
            _LOGGER.warning(
                "Unexpected RAPT payload version %d, measurements may be incorrect!",
                metrics.version,
            )

        _LOGGER.debug("Parsed RAPT Pill data: %s", metrics)

        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE, metrics.battery
        )
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS, metrics.temperature
        )
        self.update_sensor(
            key=DeviceClass.SPECIFIC_GRAVITY,
            device_class=DeviceClass.SPECIFIC_GRAVITY,
            native_unit_of_measurement=Units.SPECIFIC_GRAVITY,
            native_value=metrics.gravity,
        )

    def _process_version(self, data: bytes) -> None:
        """Process advertisement with SW version."""
        # version payload is e.g. "KEG20220612_050156_81c6d1"
        # first two bytes are manufacturer ID, we just need to strip initial "G"
        if data[0] != 71:  # "G"
            _LOGGER.warning(
                "'%r' doesn't seem to be version advertisement payload, ignoring" % data
            )
            return
        version = data[1:].decode("ascii")
        self.set_device_sw_version(version)

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        manufacturer_data = service_info.manufacturer_data

        if not manufacturer_data:
            return

        # 16722 = 0x52 0x41 prefix in little endian - start of "RAPT"
        # 17739 = 0x4b 0x45 prefix in little endian - start of "KEG"
        if 16722 not in manufacturer_data and 17739 not in manufacturer_data:
            _LOGGER.debug("RAPT Pill manufacturer ID not found in data")
            return

        _LOGGER.debug("Got RAPT Pill data payload: %s", manufacturer_data)

        self.set_device_manufacturer("RAPT")
        self.set_device_type("RAPT Pill hydrometer")
        mac_suffix = short_address(service_info.address)
        self.set_device_name(f"RAPT Pill {mac_suffix}")
        self.set_title(f"RAPT Pill {mac_suffix}")

        if 17739 in manufacturer_data:
            if data := manufacturer_data[17739]:
                self._process_version(data)

        if 16722 not in manufacturer_data:
            return

        data = manufacturer_data[16722]

        if manufacturer_data[16722] == b"PTdPillG1":
            # likely a HW revision advertisement - can be ignored
            _LOGGER.debug("Ignoring 'RAPTdPillG1' payload")
            return

        if len(data) != 23:
            _LOGGER.error("Unknown RAPT payload: %s", data)
            return

        self._process_metrics(data)
