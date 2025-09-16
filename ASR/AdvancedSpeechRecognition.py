#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file AdvancedSpeechRecognition.py
@brief Реализация расширенной системы распознавания речи.
@details Этот файл содержит производный класс AdvancedSpeechRecognition, расширяющий функциональность базового класса.
@see AutomaticSpeechRecognitionYandex.py
"""

from AutomaticSpeechRecognitionYandex import AutomaticSpeechRecognitionYandex

class AdvancedSpeechRecognition(AutomaticSpeechRecognitionYandex):
    """
    @class AdvancedSpeechRecognition
    @brief Производный класс для расширенного распознавания речи.
    @details Наследуется от AutomaticSpeechRecognitionYandex, добавляя возможность логирования распознанного текста.
    """
    def __init__(self, folder_id: str, log_file: str, iam_token: str = None, service_secret_key: str = None):
        """
        @brief Инициализация объекта AdvancedSpeechRecognition.
        @param folder_id Идентификатор папки в Yandex Cloud.
        @param log_file Путь к файлу для логирования распознанного текста.
        @param iam_token Токен IAM для аутентификации (опционально).
        @param service_secret_key Секретный ключ сервиса (опционально).
        """
        super().__init__(folder_id, iam_token, service_secret_key)
        self.log_file = log_file  #: Путь к файлу логов.

    def log_recognized_text(self, text: str):
        """
        @brief Логирование распознанного текста в файл.
        @param text Текст для записи в лог.
        """
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"Recognized: {text}\n")

    def recognize_speech_audio_data(self, audio_data: any, lang: str = 'ru-RU', topic: str = 'general', print_result: bool = True):
        """
        @brief Распознавание речи с логированием результата.
        @param audio_data Аудиоданные для распознавания.
        @param lang Язык распознавания (по умолчанию 'ru-RU').
        @param topic Тема распознавания (по умолчанию 'general').
        @param print_result Флаг для вывода результата в консоль.
        @return Строка с распознанным текстом или сообщение об ошибке.
        """
        result = super().recognize_speech_audio_data(audio_data, lang, topic, print_result)
        if "Ошибка" not in result:
            self.log_recognized_text(result)
        return result