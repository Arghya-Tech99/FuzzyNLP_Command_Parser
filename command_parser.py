import spacy

# Load the small English model for SpaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run:")
    print("python -m spacy download en_core_web_sm")
    exit()

# --- Phase 2/4 Dictionaries ---
STANDARD_ACTIONS = {'move', 'rotate', 'stop', 'grab', 'release'}
STANDARD_DIRECTIONS = {'forward', 'backward', 'left', 'right'}
STANDARD_UNITS = {'cm', 'meters', 'degrees'}

# --- Unit Standardization Lookup Table ---
UNIT_STANDARDS = {
    'centimeter': 'cm',
    'centimeters': 'cm',
    'meter': 'meter',
    'meters': 'meter',
    'degree': 'degrees',
    'degrees': 'degrees',
}


# --- 1. POS Tagging and Named Entity Recognition (NER) ---
def process_with_spacy(text: str):
    """
    Runs text through the SpaCy pipeline to get linguistic features.
    """
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return doc, entities


# --- 2. Dependency Parsing and 3. Intent and Slot Filling (SINGLE, CORRECT DEFINITION) ---
def extract_command_slots(doc, fuzzy_tokens: list) -> dict:
    """
    Uses Dependency Parsing to link Actions (Verbs) to Parameters (Objects).
    It extracts the Action, Direction, Value, and Unit (Slots).
    """
    command_slots = {
        'command': 'UNKNOWN',
        'direction': None,
        'value': None,
        'unit': None
    }

    for token in doc:
        # 1. Look for the main Action (Verb)
        if token.pos_ == "VERB" and token.lemma_ in STANDARD_ACTIONS:
            command_slots['command'] = token.lemma_.upper()

            # 2. Look for Direction and Parameters (Objects/Modifiers)
            for child in token.children:
                child_text = child.text.lower()

                # Check for Direction Slot
                if child_text in STANDARD_DIRECTIONS:
                    command_slots['direction'] = child_text.upper()

                # Check for Value/Unit Slot (Numeric or Quantity)
                # SpaCy uses 'nummod', 'dobj', 'pobj', and NER 'CARDINAL'
                if child.dep_ in ('nummod', 'dobj', 'pobj') or child.ent_type_ == 'CARDINAL':

                    # --- VALUE EXTRACTION ---
                    # Check the token itself (or its numeric entity type) for the value
                    if child_text.isdigit() or child.ent_type_ == 'CARDINAL' or (
                            child.dep_ == 'nummod' and child.pos_ == 'NUM'):
                        # Basic conversion of value to float
                        command_slots['value'] = float(child_text.replace('a', '1').replace('an', '1'))

                        potential_unit = None

                        # --- UNIT EXTRACTION AND STANDARDIZATION ---
                        # Look for a unit attached to the value (e.g., '50' -> 'centimeters')
                        if (child.i + 1) < len(doc) and doc[child.i + 1].text.lower() in UNIT_STANDARDS:
                            potential_unit = doc[child.i + 1].text.lower()

                        # Look for units attached via dependency parsing (e.g., 'of degrees')
                        elif child.head.text.lower() in UNIT_STANDARDS:
                            potential_unit = child.head.text.lower()

                        # Perform standardization lookup
                        if potential_unit:
                            command_slots['unit'] = UNIT_STANDARDS.get(potential_unit, potential_unit)

    return command_slots


# --- 4. Final Command Object Generation (The wrapper function) ---

def generate_command_object(user_input: str, fuzzy_tokens: list) -> dict:
    """
    Main function for Phase 3: runs SpaCy and extracts the final command object.
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
# ... (Keep your example usage block for testing) ...