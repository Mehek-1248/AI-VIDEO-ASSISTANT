import unittest

from core.transcriber import transcribe_all
from utils.audio_processor import process_input


class AudioInputContractTests(unittest.TestCase):
    def test_empty_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "required"):
            process_input("  ")

    def test_missing_local_source_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            process_input("missing-recording.mp4")


class TranscriptionContractTests(unittest.TestCase):
    def test_empty_chunks_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "audio chunks"):
            transcribe_all([])

    def test_unknown_language_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "english.*hinglish"):
            transcribe_all(["chunk.wav"], language="french")


if __name__ == "__main__":
    unittest.main()
