"""Multilingual voice capture, transcription and translation for Rescue Link.

Cloud processing is enabled when Google Cloud credentials and APIs are configured.
Original audio and both transcript versions are stored in the local SQLite database.
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
import uuid
import wave

from backend.db import get_connection

SUPPORTED_LANGUAGES = {
    "Hindi": "hi-IN",
    "Gujarati": "gu-IN",
    "Marathi": "mr-IN",
    "English": "en-IN",
}


def transcribe_and_translate(audio_bytes: bytes, language_name: str) -> dict:
    """Transcribe a WAV recording in its source language and translate it to English."""
    if language_name not in SUPPORTED_LANGUAGES:
        raise ValueError("Choose Hindi, Gujarati, Marathi or English.")

    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            pcm_data = wav_file.readframes(wav_file.getnframes())
    except (wave.Error, EOFError) as exc:
        raise ValueError("The recording is not a valid WAV file. Please record again.") from exc

    if sample_width != 2:
        raise ValueError("Audio must be 16-bit PCM WAV. Please record again using the browser microphone.")

    try:
        from google.cloud import speech
        from google.cloud import translate_v2
    except ImportError as exc:
        raise RuntimeError(
            "Voice dependencies are missing. Install the project's requirements.txt again."
        ) from exc

    try:
        speech_client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            audio_channel_count=channels,
            language_code=SUPPORTED_LANGUAGES[language_name],
            enable_automatic_punctuation=True,
        )
        response = speech_client.recognize(
            config=config,
            audio=speech.RecognitionAudio(content=pcm_data),
            timeout=60,
        )
        transcript = " ".join(
            result.alternatives[0].transcript.strip()
            for result in response.results
            if result.alternatives
        ).strip()
        if not transcript:
            raise ValueError("No speech was detected. Try recording closer to the microphone.")

        if language_name == "English":
            translated = transcript
        else:
            translator = translate_v2.Client()
            translated_result = translator.translate(
                transcript,
                target_language="en",
                source_language=SUPPORTED_LANGUAGES[language_name][:2],
                format_="text",
            )
            translated = translated_result["translatedText"]

        return {
            "language": language_name,
            "language_code": SUPPORTED_LANGUAGES[language_name],
            "transcript": transcript,
            "translated_text": translated,
        }
    except ValueError:
        raise
    except Exception as exc:
        message = str(exc)
        if "DefaultCredentialsError" in type(exc).__name__ or "credentials" in message.lower():
            raise RuntimeError(
                "Google Cloud credentials are not configured. Set GOOGLE_APPLICATION_CREDENTIALS "
                "to a service-account JSON file and enable Speech-to-Text and Cloud Translation."
            ) from exc
        raise RuntimeError(f"Voice processing failed: {message}") from exc


def save_voice_note(audio_bytes: bytes, result: dict, mime_type: str = "audio/wav") -> str:
    """Persist original audio and its source/English transcripts."""
    note_id = f"VOICE-{uuid.uuid4().hex[:12].upper()}"
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO voice_notes
                (id, request_id, created_at, language, language_code,
                 original_transcript, translated_text, mime_type, audio_data)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note_id,
                datetime.utcnow().isoformat(),
                result["language"],
                result["language_code"],
                result["transcript"],
                result["translated_text"],
                mime_type,
                sqlite3.Binary(audio_bytes),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return note_id


def attach_voice_note(note_id: str, request_id: str) -> None:
    """Associate a previously saved recording with its submitted SOS request."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE voice_notes SET request_id=? WHERE id=?",
            (request_id, note_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_voice_note_for_request(request_id: str):
    """Return one request's transcript and audio for the operations team."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, created_at, language, language_code,
                   original_transcript, translated_text, mime_type, audio_data
            FROM voice_notes
            WHERE request_id=?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (request_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
