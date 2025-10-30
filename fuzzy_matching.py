import Levenshtein as lev
from fuzzywuzzy import fuzz
import Preprocessing as process

# --- GROUND TRUTH (Standard Definitions) ---
# Dictionaries imported from Preprocessing.py
print(process.STANDARD_ROBOT_ACTIONS)
print(process.STANDARD_ROBOT_PARAMETERS)

# --- Create the Comprehensive Reference Lexicon ---
# This maps user synonyms/variants (keys) to the Standard Robot Term (values).
# It's built upon the Phase 1 Ground Truth for all recognized tokens.
REFERENCE_COMMAND_LEXICON = {
    # Actions Synonyms (User term: Standard term)
    'go': 'move',
    'advance': 'move',
    'shift': 'move',
    'turn': 'rotate',
    'halt': 'stop',

    # Direction Synonyms
    'forwards': 'forward',
    'front': 'forward',
    'back': 'backward',

    # Parameter Synonyms (Units and Quantifiers)
    'centimeter': 'cm',
    'meters': 'meter',
    'degree': 'degrees',

    # Specific Parameter/Quantifier Mapping (Example: for parameter extraction)
    'ten': '10',
    'half': '0.5',
    'one': '1',
    'two': '2',
    'three': '3',
    'half a meter': '0.5 meter'
}

# Extract all standard terms (values) for efficient fuzzy comparison
STANDARD_VOCABULARY = set(REFERENCE_COMMAND_LEXICON.values())
STANDARD_VOCABULARY.update(REFERENCE_COMMAND_LEXICON.keys())  # Include original keys too


# --- Fuzzy String Matching Implementation ---

def get_standard_word(token: str, vocabulary: set, threshold: int = 85) -> str:
    """
    Compares a user token against a set of standard vocabulary using fuzzy matching.

    Args:
        token (str): The user input token (e.g., 'forwerd').
        vocabulary (set): Set of standardized words (from REFERENCE_COMMAND_LEXICON).
        threshold (int): Minimum fuzz.ratio score (0-100) for a match.

    Returns:
        str: The standardized word if score >= threshold, otherwise the original token.
    """
    best_match = token
    highest_ratio = 0

    # Using fuzz.ratio (Levenshtein distance similarity) for single-word matching
    for standard_word in vocabulary:
        # Calculate the simple fuzzy ratio
        ratio = fuzz.ratio(token.lower(), standard_word.lower())

        if ratio > highest_ratio:
            highest_ratio = ratio

            # Check for the minimum similarity threshold
            if highest_ratio >= threshold:
                best_match = standard_word

    # Return the best match if it meets the threshold
    return best_match if highest_ratio >= threshold else token


def fuzzy_correct_sentence(processed_tokens: list) -> list:
    """
    Applies fuzzy correction to every token in the preprocessed list.
    """
    corrected_tokens = []

    for token in processed_tokens:
        # Correct the token using the global standard vocabulary
        corrected_token = get_standard_word(token, STANDARD_VOCABULARY)
        corrected_tokens.append(corrected_token)

    return corrected_tokens


# --- Command Template Matching (Initial) ---

# This step is primarily for demonstration; in a real system, Phase 3
# (POS tagging/Dependency Parsing) handles extraction.
# This simple template matching uses the corrected tokens to transform units/quantities.

def simple_template_matching(fuzzy_tokens: list, lexicon: dict) -> list:
    """
    Performs a simple pass to replace tokens with their final standardized form
    based on exact matches in the lexicon.

    Example Goal: Replace 'cm' with 'centimeter' (if 'centimeter' is the standard)
    or replace 'ten' with '10'.

    Note: For this example, we'll swap tokens back to their standardized value
    using the lexicon where applicable.
    """
    final_tokens = []

    for token in fuzzy_tokens:
        # Check if the corrected token itself is a key in the original lexicon
        # and has a different standardized value (e.g., 'ten' -> '10').

        # NOTE: This logic needs careful integration with fuzzy correction,
        # but for simplicity, we look up the standard definition here.
        standard_value = lexicon.get(token, token)

        # If the standard value includes a space (like '0.5 meter'),
        # we token-split it and add those parts.
        if ' ' in standard_value:
            final_tokens.extend(standard_value.split())
        else:
            final_tokens.append(standard_value)

    return final_tokens


# --- Full Pipeline Example ---

# Assume this input comes from your working Phase 1 pipeline,
# where the input "Move forwerd ten centimetars." becomes:
INPUT_TOKENS_FROM_PHASE_1 = ['move', 'forwerd', 'ten', 'centimetars']

print(f"1. Input Tokens (from Phase 1): {INPUT_TOKENS_FROM_PHASE_1}")

# A. Apply Fuzzy Correction (Step 2)
# 'forwerd' should become 'forward'
# 'centimetars' should become 'centimeter' (or 'cm' if that was the standard)
fuzzy_corrected = fuzzy_correct_sentence(INPUT_TOKENS_FROM_PHASE_1)
print(f"2. Fuzzy Corrected Tokens:     {fuzzy_corrected}")

# B. Apply Simple Template Matching (Step 3)
# 'ten' should become '10' (via lexicon lookup)
# 'forward' and 'move' remain standardized
final_standardized = simple_template_matching(fuzzy_corrected, REFERENCE_COMMAND_LEXICON)
print(f"3. Final Standardized Tokens:  {final_standardized}")

# Goal Achieved: Transform ['move', 'forwerd', 'ten', 'centimetars'] into
# ['move', 'forward', '10', 'cm'] (or similar standardized output).