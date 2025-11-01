import spacy

# Load the small English model for SpaCy
# This model handles POS tagging, NER, and Dependency Parsing.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run:")
    print("python -m spacy download en_core_web_sm")
    exit()

# --- Placeholder for Phase 2/4 Dictionaries ---
# In a real setup, these would be imported from fuzzy_matching.py and robot_controller.py
STANDARD_ACTIONS = {'move', 'rotate', 'stop', 'grab', 'release'}
STANDARD_DIRECTIONS = {'forward', 'backward', 'left', 'right'}
STANDARD_UNITS = {'cm', 'meters', 'degrees'}


# --- 1. POS Tagging and Named Entity Recognition (NER) ---
# SpaCy handles these automatically when processing the text.

def process_with_spacy(text: str):
    """
    Runs text through the SpaCy pipeline to get linguistic features.
    """
    # SpaCy automatically tokenizes, tags POS, and finds dependencies
    doc = nlp(text)

    # Simple NER extraction for demonstration (SpaCy uses "CARDINAL" for numbers)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    return doc, entities


# --- 2. Dependency Parsing and 3. Intent and Slot Filling ---

def extract_command_slots(doc, fuzzy_tokens: list) -> dict:
    """
    Uses Dependency Parsing to link Actions (Verbs) to Parameters (Objects).
    It extracts the Action, Direction, Value, and Unit (Slots).

    Args:
        doc (spacy.tokens.Doc): The SpaCy processed document.
        fuzzy_tokens (list): The list of tokens corrected by fuzzy matching (Phase 2).

    Returns:
        dict: The final extracted command slots.
    """
    command_slots = {
        'command': 'UNKNOWN',
        'direction': None,
        'value': None,
        'unit': None
    }

    # Recreate the fuzzy-corrected sentence for parsing consistency
    # (SpaCy performs its own tokenization, so we map results back to fuzzy_tokens)

    # 1. Look for the main Action (Verb)
    for token in doc:
        # We look for a verb that is also a recognized standardized action
        if token.pos_ == "VERB" and token.lemma_ in STANDARD_ACTIONS:
            command_slots['command'] = token.lemma_.upper()

            # --- Dependency Parsing Logic ---
            # 2. Look for Direction and Parameters (Objects/Modifiers)
            for child in token.children:
                child_text = child.text.lower()

                # Check for Direction Slot
                if child_text in STANDARD_DIRECTIONS:
                    command_slots['direction'] = child_text.upper()

                # Check for Value/Unit Slot (Numeric or Quantity)
                # SpaCy uses 'nummod' (numeric modifier) or 'dobj' (direct object)
                if child.dep_ in ('nummod', 'dobj', 'pobj') or child.ent_type_ == 'CARDINAL':

                    # Try to find the numeric value and unit around the token
                    # Simplistic extraction: look for a number near a unit

                    # Check the token itself against fuzzy-corrected numbers
                    if child_text.isdigit() or child.ent_type_ == 'CARDINAL':
                        command_slots['value'] = float(child_text.replace('a', '1').replace('an', '1'))

                        # Look for a unit right next to the value
                        if child.head.text.lower() in STANDARD_UNITS:
                            command_slots['unit'] = child.head.text.lower()
                        elif (child.i + 1) < len(doc) and doc[child.i + 1].text.lower() in STANDARD_UNITS:
                            command_slots['unit'] = doc[child.i + 1].text.lower()

                    # Handle units when parsing
                    elif child_text in STANDARD_UNITS:
                        command_slots['unit'] = child_text

                        # Look for the numeric value (CARDINAL/NUM) attached to the unit
                        for grandchild in child.children:
                            if grandchild.ent_type_ == 'CARDINAL':
                                command_slots['value'] = float(grandchild.text)

    return command_slots


# --- 4. Final Command Object Generation (The wrapper function) ---

def generate_command_object(user_input: str, fuzzy_tokens: list) -> dict:
    """
    Main function for Phase 3: runs SpaCy and extracts the final command object.

    NOTE: In a fully integrated system, the user_input should be cleaned
    (punctuation removed) before passing to SpaCy for better NER/Parsing.
    """
    # Step 1 & 2: POS Tagging, NER, and Dependency Parsing
    doc, entities = process_with_spacy(user_input)

    # Step 3: Intent and Slot Filling
    command_object = extract_command_slots(doc, fuzzy_tokens)

    # Final cleanup/validation
    if command_object['command'] == 'UNKNOWN':
        # Simple rule: if the first *fuzzy* token is an action, assume that's the command
        if fuzzy_tokens and fuzzy_tokens[0] in STANDARD_ACTIONS:
            command_object['command'] = fuzzy_tokens[0].upper()

    return command_object


# --- Example Usage (Integration with Phase 1/2 Output) ---

# Example 1: Clear Command with Units (Assume fuzzy corrected 'ninety degerees' -> 'ninety degrees')
user_command_1 = "Turn the robot right by ninety degrees."
fuzzy_tokens_1 = ['rotate', 'right', 'by', '90', 'degrees']
final_object_1 = generate_command_object(user_command_1, fuzzy_tokens_1)

print("\n--- Example 1 Command Interpretation ---")
print(f"Input: {user_command_1}")
print(f"Fuzzy Tokens: {fuzzy_tokens_1}")
print(f"Command Object: {final_object_1}")
# Expected Output: {'command': 'ROTATE', 'direction': 'RIGHT', 'value': 90.0, 'unit': 'degrees'}


# Example 2: Movement Command with misspellings (Assume fuzzy correction works)
user_command_2 = "Move forwerd five centimeters."
fuzzy_tokens_2 = ['move', 'forward', '5', 'cm']
final_object_2 = generate_command_object(user_command_2, fuzzy_tokens_2)

print("\n--- Example 2 Command Interpretation ---")
print(f"Input: {user_command_2}")
print(f"Fuzzy Tokens: {fuzzy_tokens_2}")
print(f"Command Object: {final_object_2}")
# Expected Output: {'command': 'MOVE', 'direction': 'FORWARD', 'value': 5.0, 'unit': 'cm'}