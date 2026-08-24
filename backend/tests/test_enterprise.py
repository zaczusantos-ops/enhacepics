"""
Test Enterprise Features: Users, Teams, Shared Presets, Culling & Smart Crop.
"""

import unittest
from backend.app.schemas.enterprise import (
    UserRegisterRequest, UserLoginRequest,
    TeamCreateRequest, TeamAddMemberRequest,
    TeamPresetCreateRequest, TeamPresetParams,
    PhotoCandidate
)
from backend.app.services.db_service import db_service
from backend.app.services.culling_service import culling_service


class TestEnterprise(unittest.TestCase):

    def test_user_registration_and_login(self):
        reg = UserRegisterRequest(
            username="fotografo_teste",
            email="fotografo@igreja.org",
            password="securepassword123",
            name="Fotógrafo Teste",
            church_name="Igreja Batista Central"
        )
        res = db_service.register_user(reg)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.token)
        self.assertEqual(res.user.username, "fotografo_teste")

        # Login
        login_req = UserLoginRequest(
            email_or_username="fotografo_teste",
            password="securepassword123"
        )
        login_res = db_service.login_user(login_req)
        self.assertTrue(login_res.success)
        self.assertEqual(login_res.user.email, "fotografo@igreja.org")

    def test_team_and_presets(self):
        user_id = "usr_fotografo_teste"
        team = db_service.create_team(user_id, TeamCreateRequest(
            name="Mídia Jovens",
            description="Cobertura de cultos de jovens",
            church_name="Igreja Batista Central"
        ))
        self.assertIsNotNone(team.id)
        self.assertEqual(team.name, "Mídia Jovens")

        # Add member
        team_updated = db_service.add_member_to_team(team.id, "lucas_video", "member")
        self.assertTrue(any(m.username == "lucas_video" for m in team_updated.members))

        # Create preset
        preset = db_service.create_team_preset(team.id, "Fotógrafo Teste", TeamPresetCreateRequest(
            name="Moody Jovens Pro",
            description="Preset quente com alto contraste",
            category="Louvor",
            params=TeamPresetParams(
                exposure_compensation=0.15,
                temperature_kelvin=5800,
                contrast=1.18,
                f_stop_simulation=2.0
            )
        ))
        self.assertEqual(preset.name, "Moody Jovens Pro")

        presets = db_service.get_team_presets(team.id)
        self.assertTrue(any(p.name == "Moody Jovens Pro" for p in presets))

    def test_culling_funnel(self):
        # 10 sample photos from burst
        photos = [
            PhotoCandidate(photo_id=f"p_{i}", file_name=f"Culto_Louvor_{i:02d}.jpg")
            for i in range(1, 11)
        ]

        # Phase 1: Deduplication
        dedup = culling_service.deduplicate_and_group(photos)
        self.assertTrue(dedup.success)
        self.assertEqual(dedup.total_photos_analyzed, 10)
        self.assertGreater(dedup.total_groups_formed, 0)
        self.assertGreater(dedup.champions_count, 0)

        # Phase 2: Top 20 Ranking
        ranking = culling_service.rank_top_photos(photos)
        self.assertTrue(ranking.success)
        self.assertEqual(ranking.total_evaluated, 10)
        self.assertEqual(ranking.top_20_count, 10)
        self.assertGreaterEqual(ranking.ranked_photos[0].ai_score, 8.0)

        # Phase 3: Smart Crop
        crop = culling_service.calculate_smart_crop("p_1", width=1920, height=1080)
        self.assertTrue(crop.success)
        self.assertEqual(crop.suggested_crop.aspect_ratio, "4:5")
        self.assertAlmostEqual(crop.suggested_crop.height, 1.0)


if __name__ == "__main__":
    unittest.main()
