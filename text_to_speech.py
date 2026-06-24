import os

from google.cloud import texttospeech

key_path = os.getenv("GCLOUD_SERVICE_ACCOUNT_KEY")
client = texttospeech.TextToSpeechClient.from_service_account_file(key_path)

voice = texttospeech.VoiceSelectionParams(
    language_code="ja-JP",
    name="ja-JP-Chirp3-HD-Erinome",
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.75,
)


def text_to_speech(japanese_text, mp3_outfile):
    synthesis_input = texttospeech.SynthesisInput(text=japanese_text)
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )
    with open(mp3_outfile, "wb") as f:
        f.write(response.audio_content)
        print(f"Japanese audio written to {mp3_outfile}")

    return mp3_outfile
