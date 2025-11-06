from location.location import get_current_location
STORE_LOCATION = get_current_location()

# MODEL WEIGHTS
AGE_DETECTOR_WEIGHTS = "./src/analysis/models/resnet50_regression.pth"
GENDER_DETECTOR = "rizvandwiki/gender-classification"
EMBEDDING_MODEL = "./src/analysis/models/resnet50_regression.pth"

# DETAILED CONFIGURABLE ITEMS
DEFAULT_CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.8
MIN_FACE_RATIO = 0.1
EMBEDDING_THRESHOLD = 0.2

# TRACKING_DURATION_SEC should be more than PROCESS_INTERVAL_SEC always
PROCESS_INTERVAL_SEC = 2
TRACKING_DURATION_SEC = 3
MAX_EMBEDDING_TO_MATCH = 500

# SCREEN LOCATION ID
LOCATION_ID = "..."

# API CONFIGURATION
# BASE_URL = 'http://localhost:5001'
# API_KEY = 'test_api_key_123'
BASE_URL = "https://pfrm.fcust.com"  # Change this line
API_KEY = "AGGJ4FpR0lJHv9Vjedc49K7A2Nrqv9OVXnVt6TWYoNUWRdquPY2pHfg39BxoObP5utcfL4mvNqGkwAt7X7ochdGitpB001TixxfRGHp181jxiFOnu4ufwUCMrUlZ2ce9"        # Change this line
# API PAYLOAD CONFIGURATION
DEFAULT_DEVICE_TYPE = ""
DEFAULT_EVENTS = ["white","black"]
DEFAULT_COMPANY_NAME = "UST"

# Configurable parameters (can be modified as needed)
PURCHASE_INTENT = "electronics"  # Purchase intent from config
VISITOR_SEGMENTS = ["female"]  # Visitor segments from config

# Display targeting options (choose one approach)
DISPLAY_IDS = [752]  # Display IDs from config - for single/multiple display targeting
STORE_UUID = "UST-001"    # For all store displays targeting
STORE_UUID_TYPE = "STORE_CODE"

#KAFKA DETAILS (DEPRECATED - keeping for reference)
TOPICS = ["..."]
BOOTSTRAP_SERVERS="..."