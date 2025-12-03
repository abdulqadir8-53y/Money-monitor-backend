# Initialize Firebase
import json
firebase_config_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
try:
    if not firebase_admin._apps:
        if firebase_config_path:
            # Try loading from file path first (local development)
            if os.path.isfile(firebase_config_path):
                cred = credentials.Certificate(firebase_config_path)
            else:
                # Try loading from JSON string (production)
                cred = credentials.Certificate(json.loads(firebase_config_path))
        else:
            # Use default Application Default Credentials
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    db = firestore.client()
