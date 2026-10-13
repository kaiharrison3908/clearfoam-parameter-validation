import unittest
from pathlib import Path

from parameter_validation import (
    REQUIRED_PARAMETERS,
    parse_parameter_text,
    validate_parameters,
)


def valid_parameters():
    """Return a complete set of valid numeric test inputs."""
    return {name: "1.25" for name in REQUIRED_PARAMETERS}


class ParameterValidationTests(unittest.TestCase):

    def test_accepts_complete_numeric_parameters(self):
        self.assertEqual(validate_parameters(valid_parameters()), [])

    def test_accepts_scientific_notation(self):
        parameters = valid_parameters()
        parameters["d1"] = "1.6e-09"
        self.assertEqual(validate_parameters(parameters), [])

    def test_rejects_missing_required_parameter(self):
        parameters = valid_parameters()
        del parameters["d1"]

        errors = validate_parameters(parameters)

        self.assertTrue(
            any("Missing required parameter: d1" in error for error in errors)
        )

    def test_rejects_empty_value(self):
        parameters = valid_parameters()
        parameters["mum"] = "   "

        errors = validate_parameters(parameters)

        self.assertTrue(
            any("mum" in error and "empty" in error for error in errors)
        )

    def test_rejects_non_numeric_value(self):
        parameters = valid_parameters()
        parameters["Ks"] = "not-a-number"

        errors = validate_parameters(parameters)

        self.assertTrue(
            any("Ks" in error and "valid number" in error for error in errors)
        )

    def test_rejects_nan_and_infinity(self):
        for value in ("NaN", "inf", "-inf", "1e999"):
            with self.subTest(value=value):
                parameters = valid_parameters()
                parameters["E_crit"] = value

                errors = validate_parameters(parameters)

                self.assertTrue(
                    any("E_crit" in error and "finite" in error for error in errors)
                )

    def test_reports_multiple_errors(self):
        parameters = valid_parameters()
        parameters["mum"] = ""
        parameters["Ks"] = "abc"
        del parameters["d1"]

        errors = validate_parameters(parameters)

        self.assertGreaterEqual(len(errors), 3)

    def test_does_not_modify_input(self):
        parameters = valid_parameters()
        original = parameters.copy()

        validate_parameters(parameters)

        self.assertEqual(parameters, original)

    def test_parser_excludes_openfoam_header_metadata(self):
        text = """FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    location "constant";
    object transportProperties;
}
// * * * * * * * * * * * * * * * * //

d1 1.6e-09;
mmax 40;

// ************************************************************************* //
"""
        self.assertEqual(
            parse_parameter_text(text),
            {"d1": "1.6e-09", "mmax": "40"},
        )

    def test_actual_transport_properties_configuration(self):
        config = (
            Path(__file__).resolve().parents[1]
            / "dev/clearFoam/base/constant/transportProperties"
        )
        self.assertTrue(config.is_file(), f"Config not found: {config}")

        parameters = parse_parameter_text(config.read_text())

        self.assertEqual(set(parameters), set(REQUIRED_PARAMETERS))
        self.assertEqual(validate_parameters(parameters), [])


if __name__ == "__main__":
    unittest.main()
