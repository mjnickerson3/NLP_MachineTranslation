"""
main.py

Student starter template for the Machine Translation Comparison and Evaluation Tool.

Instructions:
- Complete all TODO sections
- At minimum, use ONE real translation API
- Use test_cases.json for your translation inputs
- Save your results to results.json
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import List, Dict, Any

from dotenv import load_dotenv

from translator import (
    BaseTranslator,
    DeepLTranslator,
    GoogleCloudTranslator,
    MockTranslator,
    TranslationError,
)


TEST_CASES_FILE = "test_cases.json"
OUTPUT_FILE = "results.json"


def load_test_cases(filepath: str) -> List[Dict[str, Any]]:
    """
    Load translation test cases from a JSON file.
    """
    path = Path(filepath)

    #  check if the file exists
    if not path.exists():
        raise FileNotFoundError(f"Could not find {filepath}")

    #  open and load the JSON data
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    #  verify the JSON is a list
    if not isinstance(data, list):
        raise ValueError("test_cases.json must contain a JSON list of test cases.")

    return data


def build_translators() -> List[BaseTranslator]:
    """
    Build the list of translators.

    Minimum requirement:
    - one real API translator

    Fallback:
    - use MockTranslator if no real service loads
    """
    translators: List[BaseTranslator] = []

    #  try loading DeepLTranslator
    try:
        translators.append(DeepLTranslator())
    except TranslationError as exc:
        print(f"[INFO] DeepL not loaded: {exc}")

    #  optionally try loading GoogleCloudTranslator
    try:
        translators.append(GoogleCloudTranslator())
    except TranslationError as exc:
        print(f"[INFO] Google Cloud not loaded: {exc}")

    # fallback
    if not translators:
        print("[INFO] No real APIs loaded. Falling back to MockTranslator.")
        translators.append(MockTranslator())

    return translators


def get_rating(prompt_text: str) -> int:
    """
    Ask the user for a rating from 1 to 5.
    """
    while True:
        user_input = input(prompt_text).strip()

        try:
            rating = int(user_input)
            if 1 <= rating <= 5:
                return rating
        except ValueError:
            pass

        print("Please enter a whole number from 1 to 5.")


def evaluate_translation(service_name: str) -> Dict[str, int]:
    """
    Ask the user to rate adequacy and fluency.
    """
    print(f"\nRate translation from {service_name}:")
    adequacy = get_rating("  Adequacy (1-5): ")
    fluency = get_rating("  Fluency  (1-5): ")

    return {
        "adequacy": adequacy,
        "fluency": fluency,
    }


def print_test_case_header(index: int, case: Dict[str, Any]) -> None:
    """
    Print a readable header for each test case.
    """
    print("\n" + "=" * 80)
    print(f"TEST CASE {index + 1}")
    print("=" * 80)
    print(f"Category        : {case.get('category', 'Unknown')}")
    print(f"Source Language : {case['source_language']}")
    print(f"Target Language : {case['target_language']}")
    print(f"Source Text     : {case['text']}")

    if case.get("reference_translation"):
        print(f"Reference       : {case['reference_translation']}")


def run_translation_case(
    case: Dict[str, Any],
    translators: List[BaseTranslator],
) -> Dict[str, Any]:
    """
    Run one test case through all translators and collect ratings.
    """
    case_result: Dict[str, Any] = {
        "category": case.get("category"),
        "source_language": case["source_language"],
        "target_language": case["target_language"],
        "text": case["text"],
        "reference_translation": case.get("reference_translation"),
        "translations": [],
    }

    for translator in translators:
        try:
            # TODO: call the translator's translate() method
            result = translator.translate(
                text=case["text"],
                source_language=case["source_language"],
                target_language=case["target_language"],
            )

            print(f"\nService: {result.service_name}")
            print(f"Translation: {result.translated_text}")

            # TODO: collect ratings
            ratings = evaluate_translation(result.service_name)

            case_result["translations"].append(
                {
                    "service_name": result.service_name,
                    "translated_text": result.translated_text,
                    "adequacy": ratings["adequacy"],
                    "fluency": ratings["fluency"],
                }
            )

        except Exception as exc:
            print(f"\nService: {translator.service_name}")
            print(f"ERROR: {exc}")

            case_result["translations"].append(
                {
                    "service_name": translator.service_name,
                    "translated_text": None,
                    "adequacy": None,
                    "fluency": None,
                    "error": str(exc),
                }
            )

    return case_result


def save_results(results: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save the project results to JSON.
    """
    # TODO: write the results list to a JSON file
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)


def print_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print average adequacy and fluency by service.
    """
    summary: Dict[str, Dict[str, List[int]]] = {}

    for case in results:
        for translation in case["translations"]:
            service_name = translation["service_name"]
            adequacy = translation.get("adequacy")
            fluency = translation.get("fluency")

            if adequacy is None or fluency is None:
                continue

            if service_name not in summary:
                summary[service_name] = {
                    "adequacy_scores": [],
                    "fluency_scores": [],
                }

            summary[service_name]["adequacy_scores"].append(adequacy)
            summary[service_name]["fluency_scores"].append(fluency)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not summary:
        print("No completed ratings available.")
        return

    for service_name, scores in summary.items():
        avg_adequacy = mean(scores["adequacy_scores"])
        avg_fluency = mean(scores["fluency_scores"])

        print(f"\nService: {service_name}")
        print(f"  Average Adequacy: {avg_adequacy:.2f}")
        print(f"  Average Fluency : {avg_fluency:.2f}")


def main() -> None:
    # TODO: load environment variables
    load_dotenv()

    try:
        test_cases = load_test_cases(TEST_CASES_FILE)
    except Exception as exc:
        print(f"Failed to load test cases: {exc}")
        return

    translators = build_translators()

    print("Loaded translators:")
    for translator in translators:
        print(f" - {translator.service_name}")

    all_results: List[Dict[str, Any]] = []

    for index, case in enumerate(test_cases):
        print_test_case_header(index, case)
        case_result = run_translation_case(case, translators)
        all_results.append(case_result)

    save_results(all_results, OUTPUT_FILE)
    print_summary(all_results)

    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()