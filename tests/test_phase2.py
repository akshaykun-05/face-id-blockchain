import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from src.reverse_image_search import ReverseImageSearchError, search_image


class ReverseImageSearchTests(unittest.TestCase):
    def _image_path(self) -> tuple[tempfile.TemporaryDirectory[str], str]:
        directory = tempfile.TemporaryDirectory()
        image_path = str(Path(directory.name) / "test.jpg")
        Image.new("RGB", (2, 2), "white").save(image_path)
        return directory, image_path

    @patch("src.reverse_image_search.requests.get")
    @patch("src.reverse_image_search.requests.post")
    def test_results_are_parsed(self, mock_post: Mock, mock_get: Mock) -> None:
        directory, image_path = self._image_path()
        self.addCleanup(directory.cleanup)
        upload_response = Mock()
        upload_response.json.return_value = {"image_id": "uploaded-image-id"}
        mock_post.return_value = upload_response
        response = Mock()
        response.json.return_value = {
            "visual_matches": [
                {
                    "title": "Example profile",
                    "link": "https://www.instagram.com/example",
                    "source": "instagram.com",
                    "thumbnail": "https://cdn.example/thumb.jpg",
                    "type": "profile",
                }
            ]
        }
        mock_get.return_value = response

        results = search_image(image_path, "test-key")

        self.assertEqual(results[0]["title"], "Example profile")
        self.assertEqual(results[0]["url"], "https://www.instagram.com/example")
        self.assertEqual(results[0]["domain"], "instagram.com")
        self.assertTrue(results[0]["is_social_media"])
        self.assertEqual(results[0]["type"], "profile")
        upload_files = mock_post.call_args.kwargs["files"]
        self.assertEqual(upload_files["image"][0], "test.jpg")
        self.assertNotIn("encoded_image", mock_get.call_args.kwargs["params"])
        request_params = mock_get.call_args.kwargs["params"]
        self.assertEqual(request_params["engine"], "google_lens")
        self.assertEqual(request_params["image_id"], "uploaded-image-id")

    @patch("src.reverse_image_search.requests.get")
    @patch("src.reverse_image_search.requests.post")
    def test_non_social_result_is_not_a_social_match(self, mock_post: Mock, mock_get: Mock) -> None:
        directory, image_path = self._image_path()
        self.addCleanup(directory.cleanup)
        upload_response = Mock()
        upload_response.json.return_value = {"image_id": "uploaded-image-id"}
        mock_post.return_value = upload_response
        response = Mock()
        response.json.return_value = {
            "visual_matches": [
                {"title": "News result", "link": "https://news.example/story"}
            ]
        }
        mock_get.return_value = response

        results = search_image(image_path, "test-key")

        self.assertFalse(results[0]["is_social_media"])
        self.assertNotIn("social_media_match", json.dumps(results))

    @patch("src.reverse_image_search.requests.get")
    @patch("src.reverse_image_search.requests.post")
    def test_malformed_search_response_is_rejected(
        self, mock_post: Mock, mock_get: Mock
    ) -> None:
        directory, image_path = self._image_path()
        self.addCleanup(directory.cleanup)
        upload_response = Mock()
        upload_response.json.return_value = {"image_id": "uploaded-image-id"}
        mock_post.return_value = upload_response
        response = Mock()
        response.json.return_value = {"unexpected": []}
        mock_get.return_value = response

        with self.assertRaisesRegex(ReverseImageSearchError, "visual_matches"):
            search_image(image_path, "test-key")

    @patch("src.reverse_image_search.requests.get")
    @patch("src.reverse_image_search.requests.post")
    def test_search_details_are_never_printed(
        self, mock_post: Mock, mock_get: Mock
    ) -> None:
        directory, image_path = self._image_path()
        self.addCleanup(directory.cleanup)
        upload_response = Mock()
        upload_response.json.return_value = {"image_id": "uploaded-image-id"}
        mock_post.return_value = upload_response
        response = Mock()
        response.json.return_value = {"visual_matches": []}
        mock_get.return_value = response

        with patch("builtins.print") as mock_print:
            search_image(image_path, "test-key")

        output = " ".join(str(call) for call in mock_print.call_args_list)
        self.assertNotIn("test-key", output)
        self.assertNotIn("uploaded-image-id", output)
        self.assertNotIn("encoded_image", output)

    def test_missing_api_key_is_handled(self) -> None:
        directory, image_path = self._image_path()
        self.addCleanup(directory.cleanup)

        with self.assertRaisesRegex(ReverseImageSearchError, "SERPAPI_API_KEY"):
            search_image(image_path, None)


if __name__ == "__main__":
    unittest.main()
