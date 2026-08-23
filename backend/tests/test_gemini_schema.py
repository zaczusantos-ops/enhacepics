"""
Unit tests for Gemini Colorimetry structured schema & 3-stage DSLR analysis.
"""

from backend.app.schemas.colorimetry import ColorimetryParameters
from backend.app.services.gemini_analyzer import GeminiColorimetryAnalyzer
from backend.tests.test_engine import create_synthetic_church_image


def test_schema_defaults_and_validation():
    params = ColorimetryParameters()
    assert params.exposure_compensation == 0.0
    assert params.temperature_kelvin == 5500
    assert params.tint == 0.0
    assert params.contrast == 1.08
    assert params.skin_tone_protection_strength == 0.88
    assert params.chromatic_aberration_fix == 0.45
    assert params.led_clipping_restoration == 0.60
    assert params.focal_point_x == 0.50
    assert params.focal_point_y == 0.40
    assert params.f_stop_simulation == 2.8


def test_heuristic_analyzer_3stages():
    image_bytes = create_synthetic_church_image(400, 300)
    analyzer = GeminiColorimetryAnalyzer(api_key="")
    params = analyzer.analyze_image(image_bytes)

    assert isinstance(params, ColorimetryParameters)
    assert -2.0 <= params.exposure_compensation <= 2.0
    assert 2500 <= params.temperature_kelvin <= 9000
    assert 0.0 <= params.skin_tone_protection_strength <= 1.0
    assert 0.0 <= params.chromatic_aberration_fix <= 1.0
    assert 0.0 <= params.led_clipping_restoration <= 1.0
    assert 0.0 <= params.focal_point_x <= 1.0
    assert 0.0 <= params.focal_point_y <= 1.0
    assert 1.4 <= params.f_stop_simulation <= 8.0
    assert len(params.alternative_presets) == 3
    assert len(params.scene_moment) > 0
    print("3-stage schema and heuristic analyzer tests passed successfully!")


if __name__ == "__main__":
    test_schema_defaults_and_validation()
    test_heuristic_analyzer_3stages()
    print("All Gemini schema tests passed!")
