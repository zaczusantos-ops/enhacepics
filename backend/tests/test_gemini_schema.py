"""
Unit tests for Gemini Colorimetry structured schema.
"""

from backend.app.schemas.colorimetry import ColorimetryParameters
from backend.app.services.gemini_analyzer import GeminiColorimetryAnalyzer
from backend.tests.test_engine import create_synthetic_church_image


def test_schema_defaults_and_validation():
    params = ColorimetryParameters()
    assert params.exposure_compensation == 0.0
    assert params.temperature_kelvin == 5500
    assert params.tint == 0.0
    assert params.contrast == 1.0
    assert params.skin_tone_protection_strength == 0.8


def test_heuristic_analyzer():
    image_bytes = create_synthetic_church_image(300, 200)
    analyzer = GeminiColorimetryAnalyzer(api_key="")
    params = analyzer.analyze_image(image_bytes)

    assert isinstance(params, ColorimetryParameters)
    assert -2.0 <= params.exposure_compensation <= 2.0
    assert 2500 <= params.temperature_kelvin <= 9000
    assert 0.0 <= params.skin_tone_protection_strength <= 1.0
    assert len(params.detected_lighting_condition) > 0
    print("Schema and heuristic analyzer tests passed successfully!")


if __name__ == "__main__":
    test_schema_defaults_and_validation()
    test_heuristic_analyzer()
    print("All Gemini schema tests passed!")
