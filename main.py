print("🚀 BOT STARTED SUCCESSFULLY")

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

def get_events():
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": API_KEY,
        "countryCode": "GB",
        "size": 10
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        events = []
        for e in data.get("_embedded", {}).get("events", []):
            events.append({
                "name": e.get("name", "Unknown"),
                "venue": e.get("_embedded", {}).get("venues", [{}])[0].get("name", "Unknown"),
                "date": e.get("dates", {}).get("start", {}).get("localDate", "Unknown"),
                "price_min": e.get("priceRanges", [{}])[0].get("min") if "priceRanges" in e else None,
                "price_max": e.get("priceRanges", [{}])[0].get("max") if "priceRanges" in e else None,
            })

        return events
    except:
        return []

def demand_score(event):
    score = 0
    name = event["name"].lower()

    if any(x in name for x in ["final", "ufc", "boxing"]):
        score += 5
    if any(x in name for x in ["concert", "tour"]):
        score += 3

    return score

def estimate_resale(event):
    base = event["price_max"] if event["price_max"] else 80
    score = demand_score(event)

    if score >= 5:
        return base * 3
    elif score >= 3:
        return base * 2
    else:
        return base * 1.5

def is_profitable(event):
    return True

def format_message(event, resale):
    return f"""
🔥 EVENT ALERT

Event: {event['name']}
Venue: {event['venue']}
Date: {event['date']}

💸 Est Resale: £{round(resale,2)}
"""

seen = set()

send_message("Pro Ticket Bot Online")

while True:
    events = get_events()
    print(f"Found {len(events)} events")

    for e in events:
        key = e["name"] + e["date"]

        if key in seen:
            continue

        if is_profitable(e):
            resale = estimate_resale(e)
            send_message(format_message(e, resale))
            seen.add(key)

    time.sleep(10)

