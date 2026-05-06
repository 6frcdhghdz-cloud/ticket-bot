print("🚀 BOT STARTED SUCCESSFULLY")

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

# ---------------- TELEGRAM ----------------
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

# ---------------- FETCH EVENTS ----------------
def get_events():
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    params = {
        "apikey": API_KEY,
        "countryCode": "GB",
        "size": 20
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        events = []

        for e in data.get("_embedded", {}).get("events", []):
            try:
                events.append({
                    "name": e.get("name", "Unknown"),
                    "venue": e.get("_embedded", {}).get("venues", [{}])[0].get("name", "Unknown"),
                    "date": e.get("dates", {}).get("start", {}).get("localDate", "Unknown"),
                    "time": e.get("dates", {}).get("start", {}).get("localTime", "Unknown"),
                    "price_min": e.get("priceRanges", [{}])[0].get("min") if "priceRanges" in e else None,
                    "price_max": e.get("priceRanges", [{}])[0].get("max") if "priceRanges" in e else None,
                })
            except:
                continue

        return events

    except:
        return []

# ---------------- DEMAND INTELLIGENCE ----------------
def demand_score(event):
    score = 0
    name = event["name"].lower()
    venue = event["venue"].lower()

    # Tier 1 global demand
    tier1 = ["final", "championship", "ufc", "boxing", "drake", "taylor swift", "coldplay"]
    for w in tier1:
        if w in name:
            score += 5

    # Tier 2 strong demand
    tier2 = ["concert", "tour", "festival", "arsenal", "chelsea", "manchester", "liverpool"]
    for w in tier2:
        if w in name:
            score += 3

    # Scarcity signal (smaller venues = higher resale pressure)
    if "arena" not in venue and "stadium" not in venue:
        score += 2

    # Ultra scarcity (no price data often = early release)
    if not event["price_max"]:
        score += 2

    return score

# ---------------- MARKET-STYLE RESALE MODEL ----------------
def estimate_resale(event):
    base = event["price_max"] if event["price_max"] else 80
    score = demand_score(event)

    # volatility adjustment (simulates market spikes)
    volatility = 1.0

    if "final" in event["name"].lower():
        volatility = 1.4
    if "ufc" in event["name"].lower():
        volatility = 1.5
    if "concert" in event["name"].lower():
        volatility = 1.2

    # pricing tiers
    if score >= 10:
        multiplier = 4.0
    elif score >= 8:
        multiplier = 3.0
    elif score >= 6:
        multiplier = 2.3
    elif score >= 4:
        multiplier = 1.8
    else:
        multiplier = 1.3

    return base * multiplier * volatility

# ---------------- FILTER LOGIC ----------------
def is_profitable(event):
    score = demand_score(event)
    return score >= 2  # only strong opportunities

# ---------------- FORMAT ALERT ----------------
def format_message(event, resale):
    return f"""
🔥 HIGH VALUE ALERT

Event: {event['name']}
Venue: {event['venue']}
Date: {event['date']} {event['time']}

🎟 Retail: £{event['price_min']} - £{event['price_max']}
💸 Est Resale: £{round(resale,2)}

📊 Demand Score: {demand_score(event)}

🎯 Recommendation:
Buy early — focus on lower / central seating zones

Platform: Ticketmaster
"""

# ---------------- MAIN LOOP ----------------
seen = set()

send_message("✅ Pro Ticket Bot Online")

while True:
    print("🔄 scanning...")
events = get_events()
print(f"Found {len(events)} events")

seen = set()

send_message("Pro Ticket Bot Online")

while True:
    print("🔄 scanning...")

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
