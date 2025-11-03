import spacy

# Load the small English model for SpaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run:")
    print("python -m spacy download en_core_web_sm")
    exit()

# Dictionaries (Ground Truth)
STANDARD_ACTIONS = {'move', 'rotate', 'turn', 'stop', 'grab', 'release'}
STANDARD_DIRECTIONS = {'forward', 'backward', 'left', 'right'}

# Unit Standardization Lookup Table
UNIT_STANDARDS = {
    'cm': 'cm',
    'centimeter': 'cm',
    'centimeters': 'cm',
    'meter': 'meter',
    'meters': 'meter',
    'degree': 'degrees',
    'degrees': 'degrees',
}
ALL_UNIT_TOKENS = set(UNIT_STANDARDS.keys()) | set(UNIT_STANDARDS.values())


def process_with_spacy(text: str):
    """Runs text through the SpaCy pipeline to get linguistic features."""
    doc = nlp(text)
    return doc, [(ent.text, ent.label_) for ent in doc.ents]


def extract_command_slots(doc, fuzzy_tokens: list) -> dict:
    """
    Two-Pass Slot Extraction: Robustly extracts command, direction, value, and unit.
    """
    command_slots = {
        'command': 'UNKNOWN',
        'direction': None,
        'value': None,
        'unit': None
    }

    # --- PASS 1: FIND ACTION (Intent) ---
    for token in doc:
        # Find the main action verb
        if token.pos_ == "VERB" and token.lemma_ in STANDARD_ACTIONS:
            command_slots['command'] = token.lemma_.upper()
            break

            # --- PASS 2: FIND DIRECTION, VALUE, AND UNIT (Iterate all tokens) ---
    for i, token in enumerate(doc):
        token_text_lower = token.text.lower()

        # Find Direction
        if command_slots['direction'] is None and token_text_lower in STANDARD_DIRECTIONS:
            command_slots['direction'] = token_text_lower.upper()

        # Find Value
        is_numeric = token.pos_ == 'NUM' or token.ent_type_ == 'CARDINAL'

        if is_numeric and command_slots['value'] is None:

            # 1. Value Extraction
            try:
                command_slots['value'] = float(token_text_lower.replace('a', '1').replace('an', '1'))
            except ValueError:
                continue

                # 2. Unit Extraction: Look at the token immediately following the number (i + 1)
            if (i + 1) < len(doc):
                next_token = doc[i + 1].text.lower()

                if next_token in ALL_UNIT_TOKENS:
                    # Perform standardization lookup: e.g., 'centimeters' -> 'cm'
                    command_slots['unit'] = UNIT_STANDARDS.get(next_token, next_token)

                    # Since we found a value/unit pair, we can stop searching for slots
                    # (This implicitly assumes only one action/parameter set per command)
                    # We break the inner for loop here, but allow the outer one to finish if necessary.

    # Final fallback for Command if not found via Verb
    if command_slots['command'] == 'UNKNOWN' and fuzzy_tokens and fuzzy_tokens[0].lower() in STANDARD_ACTIONS:
        command_slots['command'] = fuzzy_tokens[0].upper()

    return command_slots


def generate_command_object(user_input: str, fuzzy_tokens: list) -> dict:
    """Wrapper function to generate the final command object."""
    doc, _ = process_with_spacy(user_input)
    command_object = extract_command_slots(doc, fuzzy_tokens)
    return command_object