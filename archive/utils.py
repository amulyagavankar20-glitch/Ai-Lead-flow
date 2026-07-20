import requests
from config import WEBHOOK_URL
import time

def process_lead(lead_data):
    """
    Sends the lead data to the n8n webhook and returns the interpreted response. 
    """
    try:
        response = requests.post(WEBHOOK_URL, json=lead_data, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                # Expecting a JSON response as outlined
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return {
                    "error": "Failed to parse webhook response. Ensure it returns valid JSON."
                }
        else:
            return {
                "error": f"Webhook returned error code {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "error": "The request timed out. The AI processing might be taking longer than 30 seconds."
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Failed to connect to the webhook. Make sure your n8n instance is running and the webhook URL is correct."
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}"
        }
