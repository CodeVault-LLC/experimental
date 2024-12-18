import requests
from datetime import datetime

def fetch_crime_data():
    # Define the API URL for Norwegian Police or Open Data Portal
    url = "https://data.politiet.no/api/crime-events"  # Hypothetical URL for demonstration

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }

    # Make the HTTP request
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch crime data. Status code:", response.status_code)
        return []

    # Parse the JSON response
    try:
        crime_data = response.json()
        crimes = []

        for event in crime_data.get("events", []):
            crime = {
                "title": event.get("title", "No title"),
                "location": event.get("location", {}).get("address", "Unknown location"),
                "date": event.get("date", "Unknown date"),
                "details": event.get("description", "No details available")
            }
            crimes.append(crime)

        return crimes
    except Exception as e:
        print(f"Error parsing crime data: {e}")
        return []

if __name__ == "__main__":
    print("Fetching latest crime data from Norway...")
    crime_data = fetch_crime_data()

    if crime_data:
        print("Latest crimes in Norway:")
        for crime in crime_data:
            print(f"- {crime['title']} at {crime['location']} on {crime['date']}")
            print(f"  Details: {crime['details']}")
    else:
        print("No crime data available.")
