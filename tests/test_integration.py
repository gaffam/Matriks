def test_full_flow():
    from pathlib import Path
    import sys
    from unittest.mock import patch
    import pytest
    pytest.importorskip('yaml')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    from ui.cli_app import main

    with patch('speech.speech_client.transcribe_mic', return_value='Kod 135 nedir?'):
        with patch('speech.voice_response.speak') as speak_mock:
            main()
            speak_mock.assert_called()
