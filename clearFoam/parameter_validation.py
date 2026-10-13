"""Validation helpers for ClearFOAM transportProperties parameters."""

import math
import re
from collections.abc import Mapping


REQUIRED_PARAMETERS = (
    "d1", "mmax", "c0", "mum", "Yxs", "ms", "Ks", "eps",
    "a", "b", "mu", "Y", "mu_e", "Y_e", "k_1", "k_4",
    "M_inf", "E_inf", "alpha", "beta", "n", "tau", "eta1",
    "eta2", "k5", "E_threshold", "E_crit", "delta_death",
    "eta_disp", "D_enzyme", "alpha_lux", "beta_lux", "K_lux",
    "gamma_I", "K_1", "R2_TOT", "K_I", "gamma_Ie",
    "epsilon", "gamma_disp", "gamma_EPS_prod", "k_deg", "M_b",
)


def parse_parameter_text(text: str) -> dict[str, str]:
    """Parse model parameters after the OpenFOAM header separator."""
    parameters = {}
    in_parameters = False

    for line in text.splitlines():
        if re.match(r"^\s*//\s*\*\s*\*+", line):
            if not in_parameters:
                in_parameters = True
                continue
            break

        if not in_parameters:
            continue

        line = line.split("//", 1)[0].strip()
        match = re.match(r"^(\w+)\s+([^;]+);", line)
        if match:
            parameters[match.group(1)] = match.group(2).strip()

    return parameters


def validate_parameters(parameters: Mapping[str, object]) -> list[str]:
    """Return validation errors without modifying the supplied parameters."""
    errors = []

    missing = sorted(set(REQUIRED_PARAMETERS) - set(parameters))
    for name in missing:
        errors.append(f"Missing required parameter: {name}.")

    for name, raw_value in parameters.items():
        value = str(raw_value).strip()

        if not value:
            errors.append(f"{name}: value cannot be empty.")
            continue

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            errors.append(f"{name}: {value!r} is not a valid number.")
            continue

        if not math.isfinite(number):
            errors.append(f"{name}: value must be finite, not {value!r}.")

    return errors
