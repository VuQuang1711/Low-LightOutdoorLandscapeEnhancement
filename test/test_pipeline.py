"""
Test Suite: Unit Tests for Image Enhancement Comparison Pipeline
test/test_pipeline.py - Universal XAI & 3-Tier Blueprint
Tests:
1. Data loading and low-light degradation simulation.
2. 4 traditional enhancement methods execution.
3. Quality assessment metrics (PSNR, SSIM, NIQE).
4. Memory cleanup and shutdown_resources.
"""

import sys
import unittest
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DataLoader
from src.enhancement_modules import EnhancementModules
from src.metrics import ImageQualityMetrics
from src.model_logic import ImageEnhancementComparisonPipeline
from src.resource_manager import cleanup_memory, shutdown_resources


class TestEnhancementSuite(unittest.TestCase):

    def setUp(self):
        # Tạo ảnh mẫu phong cảnh nhỏ để test nhanh
        self.dummy_img = np.zeros((128, 128, 3), dtype=np.uint8)
        self.dummy_img[:64, :] = [180, 120, 80]   # Sky
        self.dummy_img[64:, :] = [40, 80, 30]     # Ground

    def test_low_light_simulation(self):
        dark = DataLoader.simulate_low_light(self.dummy_img, brightness_factor=0.35, gamma_darkening=2.2)
        self.assertEqual(dark.shape, self.dummy_img.shape)
        self.assertLess(np.mean(dark), np.mean(self.dummy_img))

    def test_noise_application(self):
        noisy = DataLoader.apply_noise(self.dummy_img, "gaussian", {"sigma": 15.0})
        self.assertEqual(noisy.shape, self.dummy_img.shape)
        self.assertFalse(np.array_equal(noisy, self.dummy_img))

    def test_four_enhancement_methods(self):
        # 1. HE
        he_res, _, _ = EnhancementModules.apply_histogram_equalization(self.dummy_img)
        self.assertEqual(he_res.shape, self.dummy_img.shape)

        # 2. CLAHE
        clahe_res, _, _ = EnhancementModules.apply_clahe(self.dummy_img, clip_limit=3.0, tile_grid_size=(8, 8))
        self.assertEqual(clahe_res.shape, self.dummy_img.shape)

        # 3. Gamma
        gamma_res, _, _, _ = EnhancementModules.apply_gamma_correction(self.dummy_img, gamma=0.5)
        self.assertEqual(gamma_res.shape, self.dummy_img.shape)

        # 4. MSR
        msr_res, _, _ = EnhancementModules.apply_multi_scale_retinex(self.dummy_img, scales=[15, 80])
        self.assertEqual(msr_res.shape, self.dummy_img.shape)

    def test_metrics_calculation(self):
        psnr = ImageQualityMetrics.calculate_psnr(self.dummy_img, self.dummy_img)
        self.assertEqual(psnr, 100.0)

        ssim = ImageQualityMetrics.calculate_ssim(self.dummy_img, self.dummy_img)
        self.assertAlmostEqual(ssim, 1.0, places=2)

        niqe = ImageQualityMetrics.calculate_niqe(self.dummy_img)
        self.assertIsInstance(niqe, float)
        self.assertGreater(niqe, 0.0)

    def test_pipeline_execution(self):
        pipeline = ImageEnhancementComparisonPipeline()
        res = pipeline.process_comparison(
            image_input=self.dummy_img,
            simulate_low_light=True,
            noise_type="gaussian",
            denoise_method="bilateral"
        )
        self.assertTrue(res["ground_truth_available"])
        self.assertIn("he", res["methods"])
        self.assertIn("clahe", res["methods"])
        self.assertIn("gamma", res["methods"])
        self.assertIn("msr", res["methods"])
        self.assertIn("overall_recommended", res["rankings"])

    def test_resource_cleanup(self):
        cleanup_memory()
        shutdown_resources()


if __name__ == "__main__":
    unittest.main()
