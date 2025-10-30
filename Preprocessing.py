import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

""" Initializing nltk downloads """
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')


""" --- BASIC TEXT PIPELINE ---"""
def basic_text_pipeline(user_input):
    """
    Implements the five steps of the basic text preprocessing pipeline:
    Tokenization, Normalization, Stop Word Removal, and Lemmatization.
    """

    # 1. Input Acquisition (The input is passed as 'user_input')
    print(f"Original Input: '{user_input}'")

    # 2. Tokenization: Split the string into individual words/tokens
    # Punctuation (like the comma) is separated as its own token here.
    tokens = word_tokenize(user_input)
    print(f"Tokens: {tokens}")

    # Initialize Lemmatizer and Stop Words Set for efficiency
    #lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # List to hold tokens after normalization and filtering
    cleaned_tokens = []

    for token in tokens:
        # 3. Normalization: Convert all tokens to lowercase
        normalized_token = token.lower()

        # We only process tokens that are alphanumeric (removes most punctuation)
        if normalized_token.isalnum():

            # 4. Stop Word Removal: Filter out common, non-essential words
            if normalized_token not in stop_words:
                # 5. Lemmatization: Reduce word to its base or root form
                # Lemmatize after stop word removal to save time
                #lemma = lemmatizer.lemmatize(normalized_token)
                lemma = WordNetLemmatizer().lemmatize(normalized_token)

                cleaned_tokens.append(lemma)

    # print(f"Processed Tokens (Cleaned): {cleaned_tokens}")
    return cleaned_tokens



example_command = "Move the robot forward by ten centimeters, and turn slowly."

# Run the pipeline
processed_result = basic_text_pipeline(example_command)

print("\n--- Final Output ---")
print(f"Final Tokens for Command Parsing: {processed_result}")
print("\n The output is a list of root words ready for command interpretation")


""" --- DEFINING ROBOT COMMAND STRUCTURE --- """
# Define Standardized Robot Actions and their valid Directional modifiers
# Key is the standard, executable command (e.g., 'move')
# Values are the valid modifiers (Directions) for that command
STANDARD_ROBOT_ACTIONS = {

    'move': {
        'valid_directions': ['forward', 'backward', 'left', 'right'],
        'description': 'Translates the robot in a linear direction.'
    },
    'rotate': {
        'valid_directions': ['left', 'right', 'clockwise', 'counter_clockwise'],
        'description': 'Rotates the robot by a specified angle.'
    },
    'stop': {
        'valid_directions': [],  # Stop usually requires no direction
        'description': 'Immediately halts all robot movement.'
    },
    # Add other core actions like 'grab', 'release' if needed
}

# Define Standardized Parameter Types and Units.
# This structure helps identify the numeric values and their corresponding units
# Key is the type of parameter required
STANDARD_ROBOT_PARAMETERS = {
    'distance': {
        'required': True,
        'valid_units': ['cm', 'meter', 'm', 'millimeter', 'mm'],
        'data_type': 'float'
    },
    'angle': {
        'required': True,
        'valid_units': ['degrees', 'radians'],
        'data_type': 'float'
    },
    'speed': {
        'required': False,
        'valid_units': ['percent', 'low', 'medium', 'high'],
        'data_type': 'mixed'
    },
}

# Combine the structures into a single configuration dictionary (Optional but useful)
ROBOT_COMMAND_GROUND_TRUTH = {
    'actions': STANDARD_ROBOT_ACTIONS,
    'parameters': STANDARD_ROBOT_PARAMETERS
}


""" CREATION OF FUNCTION TO INSPECT THE USAGE OF ROBOT ACTIONS AND PARAMETERS """
def inspect_command_structure():
    """Prints the defined command structure for verification."""
    print("--- Robot Command Ground Truth Structure ---")

    # 1: Accessing an Action's valid directions
    move_directions = ROBOT_COMMAND_GROUND_TRUTH['actions']['move']['valid_directions']
    print(f"\nStandard Action 'move' accepts directions: {move_directions}")
    # Similar cases can be checked for rotation etc.

    # 2: Accessing Parameter Units
    distance_units = ROBOT_COMMAND_GROUND_TRUTH['parameters']['distance']['valid_units']
    print(f"Distance parameters accepts units: {distance_units}")
    # Similar cases can be checked for angle etc.

# Execute the inspection function
inspect_command_structure()