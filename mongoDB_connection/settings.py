"""
Django settings for mongoDB_connection project.
"""

from pathlib import Path
from pymongo import MongoClient
import os

# SECURITY WARNING: Keep the secret key secret in production!
SECRET_KEY = 'your-secure-secret-key'

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  # Add your deployment host here if needed

# MongoDB Connection
MONGO_URI = "mongodb+srv://jnsanagustin:Secretnalang@cluster0.0rci1.mongodb.net/Lutongbahay?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
try:
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["Lutongbahay"]
    print("✅ Successfully Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Users',  # Ensure this matches the folder name exactly
    'corsheaders',  # Add for React Native compatibility
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add for CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# CORS Settings (for React Native)
CORS_ALLOW_ALL_ORIGINS = True  # For development only
# For production, use:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:19006",
#     "exp://your-ip:19000",
# ]

ROOT_URLCONF = 'mongoDB_connection.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mongoDB_connection.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Media files (Uploaded images)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Model Configuration
MODEL_PATH = os.path.join(BASE_DIR, 'ingredient_classifier_200_epochs.h5')
CLASS_LABELS = [
    'Bitter_m', 'Calamansi', 'Eggplant', 'Garlic', 'Ginger',
    'Okra', 'Onion', 'Pork', 'Potato', 'Squash', 'Tomato'
]

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
