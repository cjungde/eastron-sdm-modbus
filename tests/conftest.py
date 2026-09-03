"""Fixtures: an SDM72D over modbus-connection's in-memory mock backend.

The mock backend and its fixtures ship with ``modbus-connection`` and are
imported explicitly so the suite does not rely on pytest entry-point autoloading.
No socket, no serial port, no meter — just an address-keyed register store.
"""

from __future__ import annotations

import struct

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.pytest_plugin import (
    mock_modbus_connection as mock_modbus_connection,
    mock_modbus_unit as mock_modbus_unit,
)

from eastron_sdm_modbus import SDM72DMeter


def f32(value: float) -> list[int]:
    """Encode a float the way the meter lays it out: two big-endian words."""
    return list(struct.unpack(">HH", struct.pack(">f", value)))


def words(mapping: dict[int, float]) -> dict[int, int]:
    """Expand ``{address: float}`` into the register words the meter would hold."""
    out: dict[int, int] = {}
    for address, value in mapping.items():
        hi, lo = f32(value)
        out[address] = hi
        out[address + 1] = lo
    return out


# One plausible snapshot of the meter under a light, unbalanced load.
MEASUREMENTS: dict[int, float] = {
    0x0000: 226.5671,  # voltage_l1
    0x0002: 226.3041,  # voltage_l2
    0x0004: 226.1867,  # voltage_l3
    0x0006: 0.296,     # current_l1
    0x0008: 0.0,       # current_l2
    0x000A: 0.2481,    # current_l3
    0x000C: 9.8422,    # power_l1
    0x000E: 0.0,       # power_l2
    0x0010: 3.5717,    # power_l3
    0x002A: 226.3119,  # avg_voltage
    0x0030: 0.5441,    # sum of line currents — a trap, see test_neutral_current
    0x0034: 14.245,    # total_power
    0x0038: 123.4009,  # total_va
    0x003C: -116.3244, # total_var
    0x003E: 0.1154,    # power_factor
    0x0046: 50.09,     # frequency
    0x0048: 17613.9707,# import_energy
    0x004A: 0.0,       # export_energy
    0x00E0: 0.2758,    # neutral_current
    0x0156: 17613.9707,# total_energy
    0x0184: 330.962,   # resettable_import
    0x0186: 0.0,       # resettable_export
    0x018C: 17613.9707,# net_energy
}


@pytest.fixture
def loaded_unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """A unit whose input registers hold the snapshot above."""
    mock_modbus_unit.load_raw({"input": words(MEASUREMENTS)})
    return mock_modbus_unit


@pytest.fixture
def meter(loaded_unit: MockModbusUnit) -> SDM72DMeter:
    """An SDM72D meter on the loaded unit."""
    return SDM72DMeter(loaded_unit)
