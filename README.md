# eastron-sdm-modbus

> **Alpha — not ready for installation.**
> The register model is complete and covered by tests against an in-memory
> backend, but it has not yet been verified against a physical meter, the API
> may still change without notice, and no Home Assistant integration consumes it
> yet. Do not install this for productive use.

Device library for Eastron SDM series energy meters, built on
[`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection).

Standalone and framework-free: it models the meter's registers and decodes them.
It opens no connection of its own — you hand it a `ModbusUnit`, and whoever owns
the bus decides how that unit is obtained.

## Supported devices

| Model | Status |
|---|---|
| SDM72D-M-2 | 22 measurements, resettable energy counters |

## Usage

```python
from modbus_connection import ModbusTcpParams, connect
from eastron_sdm_modbus import SDM72DMeter

async with connect(ModbusTcpParams(host="192.168.1.50", port=502)) as connection:
    meter = SDM72DMeter(connection.for_unit(1))
    await meter.async_update()

    print(meter.measurements.total_power)      # W
    print(meter.measurements.import_energy)    # kWh
```

Clearing the resettable import, export and net counters:

```python
await meter.async_reset_energy()
```

## Reading plan

Every measurement is a 32-bit IEEE 754 float in two input registers (FC04). The
address map is sparse, so the model declares the ranges the meter answers and
lets the planner turn them into as few reads as the meter's 30-parameter request
limit allows. No block splitting by hand.

## Tests

```
python -m pytest
```

The suite runs against the in-memory mock backend that ships with
`modbus-connection`. No meter and no network are involved.
