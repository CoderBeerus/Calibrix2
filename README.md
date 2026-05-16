# CALIBRIX — RTD Calibration System

CALIBRIX is a Raspberry Pi–based system I built to calibrate RTD sensors (PT100/PT1000) in a structured and measurable way.

The goal was not just to read temperature, but to build something closer to how calibration is actually done in labs — with stabilization checks, multiple samples, uncertainty calculation, and proper pass/fail decisions.

---

## What this project does

At a high level, the system takes an RTD sensor and compares it against a known reference temperature.

But instead of just logging values, it follows a proper calibration process:

- Reads temperature using MAX31865 (SPI)
- Waits until the system is thermally stable (not just “wait 30 seconds”)
- Collects multiple samples at each setpoint
- Computes error metrics like MBE, RMSE, standard deviation
- Calculates uncertainty using a GUM-based approach
- Applies correction (offset) based on measured bias
- Re-evaluates the corrected values
- Decides PASS/FAIL using tolerance limits (IEC 60751)

So it’s basically trying to bridge the gap between a student project and a real calibration workflow.

---

## Why I built this

Most projects I saw just display temperature or push it to the cloud.

That’s not useful if you care about:
- how accurate the sensor actually is
- whether it meets tolerance standards
- how much uncertainty is in the measurement

I wanted something that answers:
> “Is this sensor actually reliable?”

That’s where this project came from.

---

## How the system is structured

I didn’t build this as one big file. It’s split into modules so each part does one job.

### Control + UI
- `main.py`  
  Handles the GUI (PyQt5), user input, and overall control flow. Also manages the worker thread for continuous data acquisition.

### Calibration logic
- `calibration_sequencer.py`  
  This is the core logic. It runs the calibration as a state machine:
  
  IDLE → HEATING → STABILIZING → STABLE → RECORDING → NEXT POINT → COMPLETE  

  It also handles:
  - As-Found vs As-Left comparison
  - correction calculation (offset = −MBE)
  - final PASS/FAIL decision

### Sensor interface
- `max31865_driver.py`  
  Reads RTD values and also detects faults like open circuit, short to ground, etc.

- `max31865_driver_mock.py`  
  A simulated version with noise and thermal lag. This helped a lot during development when hardware wasn’t stable.

### Data handling
- `data_logger.py`  
  Stores timestamped data safely (thread-safe), including measured temp, standard temp, resistance, and error.

---

## Analysis part (important)

### Metrics
- `metrics.py`  
  Computes:
  - Mean Bias Error (MBE)
  - RMSE
  - MAE
  - Standard deviation
  - Relative error

These are used to understand how the sensor behaves, not just a single value.

### Uncertainty
- `uncertainty_calculator.py`  

This part calculates measurement uncertainty based on GUM.

It considers:
- ADC resolution
- repeatability (from sample variation)
- reference standard uncertainty
- self-heating
- model error

Final uncertainty:
U = k × sqrt(u1² + u2² + u3² + u4² + u5²)

This is then used in the decision rule.

---

## Decision logic

Instead of just checking error, the system uses:
|MBE| + U ≤ tolerance

Where:
- MBE = mean error
- U = expanded uncertainty
- tolerance = IEC 60751 limit

This avoids falsely passing a sensor just because uncertainty was ignored.

---

## Stabilization (one of the harder parts)

I didn’t rely on fixed delay.

Stability is detected using:
- slope (temperature change rate)
- standard deviation
- closeness to setpoint
- dwell time

All conditions must hold before recording starts.

This made the system more reliable but also harder to tune.

---

## Visualization & reports

- `plotter.py`  
  Real-time graph using PyQtGraph (faster than matplotlib). Shows:
  - measured vs standard
  - error
  - tolerance band
  - calibration phases

- `report_generator.py`  
  Generates:
  - PDF calibration report
  - CSV data
  - correction table

Reports include:
- As-Found vs As-Left comparison
- uncertainty values
- final verdict

---

## Hardware used

- Raspberry Pi 4
- MAX31865 RTD interface
- PT100 sensor
- SPI communication

---

## What didn’t go smoothly

Some actual issues I faced:

- Noise and unstable readings at low temperatures  
- Timing mismatch between sampling and logging  
- Handling NaN / invalid data (especially near 0°C)  
- Getting stabilization logic right without false positives  
- Making sure uncertainty calculation doesn’t give misleading results  

Most of the effort went into fixing these, not writing new features.

## Future improvements

- Multi-sensor calibration
- Closed-loop temperature control (heater + PID)
- Modbus/industrial protocol integration
- Better fault diagnostics
- Remote monitoring

---

## Author

Bhavesh Zanke  
Instrumentation Engineering
