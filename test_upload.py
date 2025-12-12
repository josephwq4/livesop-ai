import requests
import os

url = "http://localhost:8000/integrations/csv/upload?team_id=team123"
files = {'file': open('sample_workflow_data.csv', 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
