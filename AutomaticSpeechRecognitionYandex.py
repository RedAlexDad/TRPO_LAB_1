import os
import io
import json
import pyaudio
import tempfile
import requests
import subprocess
import numpy as np
import urllib.request
import soundfile as sf
from pydub import AudioSegment

class AutomaticSpeechRecognitionYandex:
    def __init__(self, folder_id:str, iam_token:str=None, service_secret_key:str=None):
        self.folder_id = folder_id
           
        # Проверяем взаимоисключающие условия для iam_token и oauth_token
        if (iam_token and service_secret_key) or (iam_token==None and service_secret_key==None):
            raise ValueError("Only one of 'iam_token' or 'service_secret_key' must be provided, not both.")
        if (not iam_token and not service_secret_key) and (not iam_token==None and not service_secret_key==None):
            raise ValueError("Either 'iam_token' or 'oauth_token' must be provided.")
        
        # Проверяем, передан ли iam_token. Если нет, вызываем функцию для его получения.
        self.iam_token = iam_token if iam_token else None
        self.service_secret_key = service_secret_key if not iam_token else None
            
    def detect_audio_format_by_name(self, audio_data):
        """
        Определение формата аудиофайла по имени файла.
        :param audio_data: Объект с атрибутом name или строка с именем файла.
        :return: Строка с форматом файла (например, "wav", "mp3", "ogg").
        """
        if hasattr(audio_data, 'name'):
            file_name = audio_data.name
        elif isinstance(audio_data, str):
            file_name = audio_data
        else:
            raise ValueError("Unable to determine file name")

        # Получаем расширение файла
        _, file_extension = os.path.splitext(file_name)
        file_extension = file_extension.lower().lstrip('.')  # Убираем точку и приводим к нижнему регистру

        # Проверяем поддерживаемые форматы
        if file_extension in {"wav", "mp3", "ogg", "webm"}:
            return file_extension
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def detect_audio_format(self, file_content):
        """
        Определение формата аудиофайла по заголовкам.
        :param file_content: Байты файла.
        :return: Строка с форматом файла (например, "wav", "mp3", "ogg", "webm").
        """
        # Словарь с шаблонами заголовков
        format_signatures = {
            b'RIFF': "wav",          # WAV файлы начинаются с "RIFF"
            b'ID3': "mp3",           # MP3 файлы часто начинаются с "ID3"
            b'\xFF\xFB': "mp3",      # MP3 файлы также могут начинаться с "\xFF\xFB"
            b'OggS': "ogg",          # Ogg файлы начинаются с "OggS"
        }

        # Проверяем первые байты файла на соответствие шаблонам
        for signature, format_name in format_signatures.items():
            if file_content.startswith(signature):
                return format_name

        # Если формат не определен
        raise ValueError("Unsupported audio format")

    def convert_audio_to_bytes(self, audio_data):
        # Если передан объект InMemoryUploadedFile, читаем его
        if hasattr(audio_data, 'seek'):
            audio_data.seek(0)  # Перемещаем указатель в начало файла
                    
        file_content = audio_data.read() if hasattr(audio_data, 'read') else audio_data
        
        # Проверка, что данные не пустые
        if not file_content:
            raise ValueError("Audio data is empty")
                
        # Определение формата файла
        try:
            audio_format = self.detect_audio_format_by_name(audio_data)
            # audio_format = self.detect_audio_format(file_content) # Неверно распознает формат из за словаря
            # print(f"Detected audio format: {audio_format}")
        except Exception as e:
            raise RuntimeError(f"Failed to detect audio format: {str(e)}")

        # Создаем объект AudioSegment
        try:
            audio = AudioSegment.from_file(file=io.BytesIO(file_content), format=audio_format)
        except Exception as e:
            raise RuntimeError(f"Failed to load audio data with pydub: {str(e)}")

        # Конвертируем в OggOpus
        output_buffer = io.BytesIO()
        try:
            audio.export(output_buffer, format="ogg", codec="libopus")
        except Exception as e:
            raise RuntimeError(f"Failed to export audio data to OggOpus: {str(e)}")

        return output_buffer.getvalue()
      
    def recognize_speech_audio_data(self, audio_data:any, lang:str='ru-RU', topic:str='general', print_result:bool=True):
        params = "&".join([
            "topic=%s" % topic,
            "folderId=%s" % self.folder_id,
            "lang=%s" % lang
        ])

        # Проверка формата аудиоданных
        if not audio_data or len(audio_data) == 0:
            print("Ошибка: Аудиоданные пустые или некорректные.")
            return "Ошибка: Аудиоданные пустые."

        audio_data = self.convert_audio_to_bytes(audio_data)
        # Попытка преобразовать аудио в OggOpus
        # try:
        #     audio_data = self.convert_audio_to_bytes(audio_data)
        #     content_type = "audio/ogg"
        # except Exception as e:
        #     print(f"Ошибка преобразования аудио: {str(e)}. Отправка исходных данных.")
        #     content_type = "audio/mp3"  # Предполагаем, что исходный формат — MP3


        url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=audio_data)
        url.add_header("Authorization", f"Bearer {self.iam_token}" if self.iam_token else f"Api-Key {self.service_secret_key}")
        url.add_header("Content-Type", "audio/ogg")
                
        print(f"Отправка аудиоданных длиной: {len(audio_data)} байт с параметрами: {params}")  # Отладочная информация

        try:
            responseData = urllib.request.urlopen(url).read().decode('UTF-8')
            decodedData = json.loads(responseData)

            if decodedData.get("error_code") is None:
                if print_result: print('[SPEECH KIT] Распознанный текст:', decodedData.get('result'))
                return decodedData.get("result")
            else:
                # print(f"Ошибка Yandex: {decodedData.get('error_code')} - {decodedData.get('error_message')}")
                return f"Ошибка: {decodedData.get('error_code')} - {decodedData.get('error_message')}"
        except urllib.error.HTTPError as error:
            return f"HTTP Error: {error.code} - {error.reason}"
        except Exception as error:
            return f"Ошибка: {str(error)}"

    def recognize_speech_audio_path(self, audio_file_path:str, lang:str='ru-RU', topic:str='general'):
        with open(audio_file_path, "rb") as f:
            data = f.read()

        params = "&".join([
            "topic=%s" % topic,
            "folderId=%s" % self.folder_id,
            "lang=%s" % lang
        ])

        url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=data)
        url.add_header("Authorization", "Bearer %s" % self.iam_token)

        try:
            responseData = urllib.request.urlopen(url).read().decode('UTF-8')
            decodedData = json.loads(responseData)

            if decodedData.get("error_code") is None:
                return decodedData.get("result")
            else:
                return f"Ошибка: {decodedData.get('error_code')} - {decodedData.get('error_message')}"
        except urllib.error.HTTPError as e:
            return f"HTTP Error: {e.code} - {e.reason}"
        except Exception as e:
            return f"Ошибка: {str(e)}"
