from AutomaticSpeechRecognitionYandex import AutomaticSpeechRecognitionYandex
from AdvancedSpeechRecognition import AdvancedSpeechRecognition

# Тест базового класса
asr = AutomaticSpeechRecognitionYandex(folder_id="your_folder_id", iam_token="your_iam_token")
result = asr.recognize_speech_audio_path("sample.wav")
print("Результат базового класса:", result)

# Тест производного класса
adv_asr = AdvancedSpeechRecognition(folder_id="your_folder_id", log_file="speech_log.txt", iam_token="your_iam_token")
result = adv_asr.recognize_speech_audio_path("sample.wav")
print("Результат производного класса:", result)