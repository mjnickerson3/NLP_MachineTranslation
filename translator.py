"""
translator.py

Student starter template for the Machine Translation Comparison project.

Instructions:
- Complete the sections
- At minimum, implement ONE real translation API
- You may add more translator classes if you want
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

import requests


class TranslationError(Exception):
    """Custom exception for translation-related failures."""


@dataclass
class TranslationResult:
    service_name: str
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    raw_response: Optional[Dict[str, Any]] = None


class BaseTranslator(ABC):
    """Abstract base class for translation services."""

    @property
    @abstractmethod
    def service_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> TranslationResult:
        raise NotImplementedError


class MockTranslator(BaseTranslator):
    """
    Mock translator for testing program structure.
    This does not perform a real translation.
    """

    @property
    def service_name(self) -> str:
        return "MockTranslator"

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> TranslationResult:
        fake_translation = f"[MOCK {source_language}->{target_language}] {text}"

        return TranslationResult(
            service_name=self.service_name,
            source_text=text,
            translated_text=fake_translation,
            source_language=source_language,
            target_language=target_language,
            raw_response={"mock": True},
        )


class DeepLTranslator(BaseTranslator):
    """
    Example real translator using DeepL.
    Students should complete the sections.
    """

    BASE_URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: Optional[str] = None) -> None:
        # Load the API key from the argument or environment variable
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")

        if not self.api_key:
            raise TranslationError(
                "DEEPL_API_KEY not found. Add it to your environment or .env file."
            )

    @property
    def service_name(self) -> str:
        return "DeepL"

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> TranslationResult:

        # Build the payload dictionary
        payload = {
            "text": text,
            "source_lang": source_language.upper(),
            "target_lang": target_language.upper(),
        }

        # Build the headers dictionary
        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}"
        }

        # Send the POST request
        response = requests.post(
            self.BASE_URL,
            data=payload,
            headers=headers,
            timeout=30,
        )

        # Handle non-200 responses
        if response.status_code != 200:
            raise TranslationError(
                f"DeepL request failed with status {response.status_code}: {response.text}"
            )

        # Convert response to JSON
        data = response.json()

        # Extract translated text from the JSON structure
        try:
            translated_text = data["translations"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise TranslationError("Unexpected DeepL response format.") from exc

        return TranslationResult(
            service_name=self.service_name,
            source_text=text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            raw_response=data,
        )


class GoogleCloudTranslator(BaseTranslator):
    """
    Example real translator using Google Cloud Translation API.
    Students should complete the sections.
    """

    BASE_URL = "https://translation.googleapis.com/language/translate/v2"

    def __init__(self, api_key: Optional[str] = None) -> None:
        # Load the API key from the argument or environment variable
        self.api_key = api_key or os.getenv("GOOGLE_TRANSLATE_API_KEY")

        if not self.api_key:
            raise TranslationError(
                "GOOGLE_TRANSLATE_API_KEY not found. Add it to your environment or .env file."
            )

    @property
    def service_name(self) -> str:
        return "GoogleCloudTranslate"

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> TranslationResult:

        # Build the payload dictionary
        payload = {
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text",
            "key": self.api_key,
        }

        # Send the POST request
        response = requests.post(
            self.BASE_URL,
            data=payload,
            timeout=30,
        )

        # Handle non-200 responses
        if response.status_code != 200:
            raise TranslationError(
                f"Google request failed with status {response.status_code}: {response.text}"
            )

        # Convert response to JSON
        data = response.json()

        # Extract translated text from the JSON structure
        try:
            translated_text = (
                data["data"]["translations"][0]["translatedText"]
            )
        except (KeyError, IndexError) as exc:
            raise TranslationError("Unexpected Google response format.") from exc

        return TranslationResult(
            service_name=self.service_name,
            source_text=text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            raw_response=data,
        )