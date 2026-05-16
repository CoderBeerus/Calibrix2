# max31865_driver_mock.py — CALIBRIX v2
# First-order thermal lag + Gaussian noise simulation
# Mock fault injection support for testing
import random
import math
import time

RTD_NOMINAL = 100.0
A =  3.90830e-3
B = -5.77500e-7
C = -4.18300e-12


def temp_to_resistance(temp: float) -> float:
    t = float(temp)
    if t >= 0:
        return RTD_NOMINAL * (1 + A * t + B * t**2)
    else:
        return RTD_NOMINAL * (1 + A * t + B * t**2 + C * (t - 100) * t**3)


def resistance_to_temp_converter(resistance: float) -> float:
    r_ratio = float(resistance) / RTD_NOMINAL
    if r_ratio >= 1.0:
        delta = A**2 - 4 * B * (1 - r_ratio)
        if delta < 0:
            return float("nan")
        return (-A + math.sqrt(delta)) / (2 * B)
    else:
        r    = resistance
        temp = (-242.02 + 2.2228 * r + 2.5859e-3 * r**2
                - 4.8260e-6 * r**3 - 2.8183e-8 * r**4 + 1.5243e-10 * r**5)
        if temp > 0:
            temp = (-A + math.sqrt(A**2 - 4 * B * (1 - r_ratio))) / (2 * B)
        return temp


# Fault severity constants (mirrors real driver)
FAULT_NONE    = 0
FAULT_WARNING = 1
FAULT_CRITICAL = 2


class MAX31865:
    """
    Mock MAX31865 driver with first-order thermal lag model.
    τ = 3.0 s, Gaussian noise σ = 0.02°C.
    Supports mock fault injection for UI testing.
    """
    TAU     = 3.0    # thermal time constant (s) — fast convergence for cal bath model
    NOISE   = 0.02   # Gaussian noise std-dev (°C)

    def __init__(self, bus=0, device=0, wires=4, r_ref=430.0):
        print("--- Using MOCK MAX31865 (thermal-lag model active) ---")
        self.standard_temp_for_simulation = 100.0
        self._current_temp = 25.0
        self._last_tick    = time.time()
        # Fault injection: set to FAULT_WARNING or FAULT_CRITICAL to test
        self._injected_fault = FAULT_NONE
        self._fault_message  = ""

    def configure(self, _wires):
        pass

    def inject_fault(self, severity: int, message: str = "Simulated fault"):
        """Call from tests/UI to simulate a hardware fault."""
        self._injected_fault = severity
        self._fault_message  = message

    def clear_faults(self):
        self._injected_fault = FAULT_NONE
        self._fault_message  = ""

    def read_temp(self):
        """Simulate reading with thermal lag + noise. Raises on injected fault."""
        if self._injected_fault == FAULT_CRITICAL:
            raise RuntimeError(f"CRITICAL SENSOR FAULT: {self._fault_message}")
        if self._injected_fault == FAULT_WARNING:
            print(f"[MOCK WARNING] {self._fault_message}")

        now = time.time()
        dt  = max(0.001, now - self._last_tick)
        self._last_tick = now

        target = self.standard_temp_for_simulation
        self._current_temp += (target - self._current_temp) * (1 - math.exp(-dt / self.TAU))

        noisy = self._current_temp + random.gauss(0.0, self.NOISE)
        return noisy, temp_to_resistance(noisy)

    def close(self):
        pass
