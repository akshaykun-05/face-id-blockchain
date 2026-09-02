import re
import unittest

import numpy as np

from src.face_encoder import FaceEncoder


class FaceEncoderTests(unittest.TestCase):
    def test_normalization_produces_unit_length_embedding(self) -> None:
        embedding = np.array([3.0, 4.0], dtype=np.float64)

        normalized = FaceEncoder.normalize_embedding(embedding)

        self.assertTrue(np.isclose(np.linalg.norm(normalized), 1.0))
        self.assertEqual(normalized.dtype, np.float32)

    def test_commitment_is_deterministic_and_sha256_shaped(self) -> None:
        embedding = FaceEncoder.normalize_embedding(np.array([1.0, 2.0, 3.0]))

        first = FaceEncoder.commitment(embedding)
        second = FaceEncoder.commitment(embedding.copy())

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        self.assertRegex(first, re.compile(r"^[0-9a-f]{64}$"))

    def test_empty_or_zero_embedding_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FaceEncoder.normalize_embedding(np.array([]))
        with self.assertRaises(ValueError):
            FaceEncoder.normalize_embedding(np.zeros(3))


if __name__ == "__main__":
    unittest.main()
