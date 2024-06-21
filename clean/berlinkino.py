import json
import dateparser
import re
import spacy
from datetime import datetime, timedelta
import pytz

def extract_clock_times(text):
    # Define a regular expression pattern to match clock times (hh:mm Uhr)
    pattern = r'(\d+:\d+)'
    matches = re.findall(pattern, text)
    return matches


def extract_date_times(date):
    with open('errors_datetime_format.txt','a',encoding='utf-8') as f:
        try:
            times = extract_clock_times(date)
            for time in times:
                date = date.replace(time,"")

            start_date = dateparser.parse(date).date()

            try:
                start_time = dateparser.parse(times[0]).time()
            except:
                start_time = None
            try:
                end_time = dateparser.parse(times[1]).time()
            except:
                end_time = None
            # end_date = calculate_end_date(start_date,start_time,end_time)

            return {
                "start_date":start_date,
                # "end_date":end_date,
                "start_time":start_time,
                "end_time":end_time
            }
        except:
            f.write(f"{date}\n")
            return None

def get_price(text):
    for p in ["kostenfrei","eintritt frei","free","Kostenlos"]:
        if text.lower().startswith(p):
            return 0
    
    nlp = spacy.load("en_core_web_sm")

    doc = nlp(text)

    prices = []
    
    for token in doc:
        if token.like_num:  # Check if the token looks like a number
            price = token.text.replace(",",".")
            try:
                valid_price_pattern = re.compile(r'^\d+\.\d+$')
                if bool(valid_price_pattern.match(price)):
                    prices.append(float(price))
            except:
                prices.append(price)
    if prices:
        for number in sorted(prices):
            if number > 5:
                return number
    else:
        return None

def extract_prices(text):
    if not text:
        return None
    # Regular expression pattern to find prices
    price_pattern = r'\b\d+[,\.]\d+\b'
    
    # Find all prices in the text using regex
    prices = re.findall(price_pattern, text)
    
    # Convert prices to floats and return as an array
    # return [price for price in prices]
    prices_numbers =  []
    for price_str in prices:
        prices_numbers.append(float(price_str.replace(",",".")))
    if prices_numbers:
        for number in sorted(prices_numbers):
            if number > 5:
                # print(number)
                return number
    return None

def clean_next_start(start_date,start_time):

    # Parse the start_date
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Parse the start_time
    start_time = datetime.strptime(start_time, "%H:%M:%S")

    # Combine date and time
    combined_datetime = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute, start_time.second)

    # Format the combined date and time as ISO 8601
    iso8601_datetime = combined_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    if start_time == "":
        return start_date
    return iso8601_datetime

def clean_duration(start_time,end_time):
    if end_time == "":
        return ""
    # Define the time format
    time_format = "%H:%M:%S"

    # Parse the start and end times
    start_time = datetime.strptime(start_time, time_format)
    end_time = datetime.strptime(end_time, time_format)

    # Calculate the duration in minutes
    duration_minutes = (end_time - start_time).total_seconds() / 60
    return duration_minutes

def find_duplicate_events(data):
    event_counts = {}  # Dictionary to store the count of each event

    for event in data:
        event_id = event.get("event_name")  # Replace "event_id" with the actual identifier for events
        if event_id:
            if event_id in event_counts:
                event_counts[event_id] += 1
            else:
                event_counts[event_id] = 1
    duplicate_events = [event_id for event_id, count in event_counts.items() if count > 1]
    return duplicate_events

def extract_location_infos(locationText):
    if "\n" in locationText:
        address = locationText.split("\n")
        _address = address[0]
        if len(address[1].split('   '))>1:
            zipCode = address[1].split('   ')[0]
            city = address[1].split('   ')[1]
        else:
            zipCode = None
            city = address[1]
    else:
        _address = None
        zipCode = None
        city = None
    
    return {
        "address":_address,
        "city":city,
        "zipCode":zipCode
    }

def extract_date(text):
    parts = text.split()
    date_str = parts[1]
    date_format = "%d.%m.%y"
    date_obj = datetime.strptime(date_str, date_format)
    extracted_date = date_obj.date()

    return extracted_date

def convert_to_berlin_time(source_datetime_str, source_format):
    source_datetime = datetime.strptime(source_datetime_str, source_format)
    
    # Berlin timezone
    berlin_tz = pytz.timezone('Europe/Berlin')
    
    # Localize the source datetime to Berlin timezone
    berlin_datetime = berlin_tz.localize(source_datetime)
    
    # Convert to the desired string format including the timezone offset
    berlin_datetime_str_with_tz = berlin_datetime.isoformat()

    return berlin_datetime_str_with_tz


def clean(input_file,output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    events = []
    event_counts = find_duplicate_events(data)
    for index,event in enumerate(data):
        print(f"\rLoading {index+1}/{len(data)}",end="")
        # if event["dates"] == []:
        #     continue
        # print(extract_prices(event["ticket_prices"]))
        location = extract_location_infos(event["location_adress"])
        for date in event["dates"]:
            
            try:
                date_str = extract_date(date)
                times = extract_clock_times(date)
                for time_str in times:
                    obj = {
                        "title": event["title"].split("(")[0].strip(),
                        "durationInMinutes": eval(event["duree"].replace("min","")) if event["duree"] else None,
                        "category": event["categories"].replace(", ",",") if event["categories"] else None,
                        "venue":event['location_name'],
                        "address":location["address"],
                        "city":location["city"],
                        "zipCode":location["zipCode"],
                        "geoLocation": event["geo_location"],
                        "description": event["description"],
                        "price": extract_prices(event["ticket_prices"]),
                        "source": "berlinkino",
                        "link": event["event_url"],
                        "start":convert_to_berlin_time(f"{date_str} {time_str}","%Y-%m-%d %H:%M"),
                        "isPeriodical": True if len(event["dates"])> 1 else False
                    }
                    events.append(obj)
            except Exception as e:
                print(event["title"],e)
                
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)



def clean_berlinkino():
    clean("inputs/01berlinkino.json","outputs/02berlinkino.json")

