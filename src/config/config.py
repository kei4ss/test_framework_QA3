import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://fakestoreapi.com")
API_BASE_USERS_URL = os.getenv("API_BASE_URL", "https://fakestoreapi.com/users")

API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))