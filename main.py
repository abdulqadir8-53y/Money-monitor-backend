# Initialize Firebase
firebase_config_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
db = None
try:
    if not firebase_admin._apps:
        if os.path.isfile(firebase_config_path):
            cred = credentials.Certificate(firebase_config_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✓ Firebase initialized successfully")
        else:
            print("⚠ Firebase credentials file not found - running in demo mode")
except Exception as e:
    print(f"⚠ Firebase initialization warning: {e}")
    print("Running in demo mode without Firestore")
