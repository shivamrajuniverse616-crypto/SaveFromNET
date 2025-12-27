import requests  # Import the requests library to send HTTP requests
import json      # Import the json library to handle JSON data

# Define the local URL for the Flask application's get_info endpoint
url = "http://127.0.0.1:5000/get_info"

# Define the payload with the YouTube URL to be processed
# loops forever video used for testing
payload = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}

# Set the headers to indicate that we are sending JSON data
headers = {"Content-Type": "application/json"}

try:
    # Send a POST request to the API with the payload and headers
    response = requests.post(url, json=payload, headers=headers)
    
    # Print the HTTP status code returned by the server
    print("Status Code:", response.status_code)
    
    # Parse the response JSON and print it in a formatted (indented) string
    print("Response JSON:", json.dumps(response.json(), indent=2))
except Exception as e:
    # Catch and print any exceptions that occur during the request
    print("Error:", e)
