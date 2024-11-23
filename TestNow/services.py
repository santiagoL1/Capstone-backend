import requests
from django.conf import settings
import google.generativeai as genai

class ExternalAPIService:
    """Service class for interacting with external APIs, including Google Gemini."""

    @staticmethod
    def configure_genai():
        """Configures Google Generative AI client."""
        genai.configure(api_key=settings.EXTERNAL_API['API_KEY'])

    @staticmethod
    def generate_gemini_response(prompt: str, model_name="gemini-1.5-flash"):
        """Generates a response from the Google Gemini API."""
        try:
            ExternalAPIService.configure_genai()
            model = genai.GenerativeModel(model_name)
            response = model.generate(prompt=prompt)
            return response
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    @classmethod
    def fetch_data(cls, endpoint, params=None):
        """Generic function to fetch data from an external REST API."""
        url = f"{settings.EXTERNAL_API['BASE_URL']}{endpoint}"
        headers = {
            'Authorization': f"Bearer {settings.EXTERNAL_API['API_KEY']}",
            'Content-Type': 'application/json',
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"REST API request failed: {e}")
            return None
