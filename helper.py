from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import psycopg2
from collections import defaultdict

# Make a global variable to hold the database connection so we can reuse it across functions without having to reconnect each time
db_connection = None

def connect_db():
    # This function connects to our PostgreSQL database
    global db_connection
    try:
        # Check if we already have a connection and if it's still active
        if db_connection is not None and db_connection.closed == 0:
            print("Using existing database connection.")
            return db_connection
        # Connect to the PostgreSQL database using psycopg2
        connection = psycopg2.connect(
            user="testuser",
            password="mysecretpassword",
            host="localhost",
            port="5432",
            database="mydb"
        )

        if connection.status == psycopg2.extensions.STATUS_READY:
            db_connection = connection
            print("Connection is active and ready!")
            return db_connection
        else:
            print(f"Connection is not ready. Status: {connection.status}")
            return None
    except Exception as e:
        raise Exception(f"Error connecting to database: {e}")

def initialize_parking_table():
    # This function initializes the parking_listings table that holds all the parking information prior to matching
    global db_connection
    if db_connection is None:
        raise Exception("Could not get database connection")

    try:
        # Create the parking table if it does not exist
        print("Initializing parking_listings table in the database...")

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS parking_listings (
            id SERIAL PRIMARY KEY,
            parkwhiz_id TEXT,
            spothero_id TEXT,
            cap_id TEXT,
            name TEXT,
            address TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            total_price DOUBLE PRECISION,
            available BOOLEAN
        );
        """

        with db_connection.cursor() as cur:
            cur.execute(create_table_sql)
        db_connection.commit()
        print("parking_listings table is ready")
    except Exception as e:
        raise Exception(f"Error initializing parking table: {e}")

def initialize_parking_matches_table():
    # This function initializes the parking_matches table that holds the merged parking matches across providers
    global db_connection
    if db_connection is None:
        raise Exception("Could not get database connection")

    try:
        # Create the parking_matches table if it does not exist
        print("Initializing parking_matches table in the database...")

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS parking_matches (
            id SERIAL PRIMARY KEY,
            provider_ids JSONB,
            names JSONB,
            addresses JSONB,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION
        );
        """

        with db_connection.cursor() as cur:
            cur.execute(create_table_sql)
        db_connection.commit()
        print("parking_matches table is ready")
    except Exception as e:
        raise Exception(f"Error initializing parking matches table: {e}")
    
def add_record_to_parking_listings(parking_listing):
    # This function adds recrods to the parking listings table
    try:
        global db_connection
        if db_connection is None:
            raise Exception("No database connection available")
        
        # Get the data to insert
        parkwhiz_id = parking_listing.get("ParkWhiz_provider_id") if parking_listing.get("ParkWhiz_provider_id") is not None else None
        spothero_id = parking_listing.get("SpotHero_provider_id") if parking_listing.get("SpotHero_provider_id") is not None else None
        cap_id = parking_listing.get("CAP_provider_id") if parking_listing.get("CAP_provider_id") is not None else None

        address = parking_listing.get("address") if parking_listing.get("address") is not None else None

        latitude = parking_listing.get("latitude") if parking_listing.get("latitude") is not None else None

        longitude = parking_listing.get("longitude") if parking_listing.get("longitude") is not None else None

        name = parking_listing.get("name") if parking_listing.get("name") is not None else None

        total_price = parking_listing.get("total_price") if parking_listing.get("total_price") is not None else None

        available = parking_listing.get("available")

        insert_sql = """
            INSERT INTO parking_listings (
            parkwhiz_id,
            spothero_id,
            cap_id,
            name,
            address,
            latitude,
            longitude,
            total_price,
            available
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """

        # Insert the data
        with db_connection.cursor() as cur:
            cur.execute(insert_sql, (parkwhiz_id, spothero_id, cap_id, name, address, latitude, longitude, total_price, available))
            inserted_id = cur.fetchone()[0]
        db_connection.commit()

        print(f"Inserted listing '{name}' with ID {inserted_id} into the database.")
    except Exception as e:
        print(f"Error inserting listing {name} into database: {e}")
    
def add_record_to_parking_matches(parking_matches):
    # This function adds records to the parking matches table after we find matches across providers
    try: 
        global db_connection
        if db_connection is None:
            raise Exception("No database connection available")
        with db_connection.cursor() as cur:
            for listing in parking_matches:
                cur.execute("""
                INSERT INTO parking_matches
                (provider_ids, names, addresses, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                json.dumps(listing["provider_ids"]),
                json.dumps(listing["names"]),
                json.dumps(listing["addresses"]),
                listing["latitude"],
                listing["longitude"],
            ))
        db_connection.commit()
    except Exception as e:
        raise Exception("Error in database connection when trying to add record to parking matches")
    
def parkWhiz(airport_name, start_time, end_time):
    # This function handles the API calls to ParkWhiz
    # First, retrieve the venue id given the airport name
    url = "https://api.parkwhiz.com/v4/venues"
    params = {
        "q": f"name:{airport_name}"
    }

    response = requests.get(url, params=params) 

    # Check if the request was successful and if we got any venues back
    if response.status_code == 200:
        if len(response.json()) > 0:
            venue_id = response.json()[0].get("id")
            print(f"Retrieved ParkWhiz venue ID for {airport_name}: {venue_id}. Now fetching parking information...")

            # Next, retrieve parking information using the venue id
            url = f"https://api.parkwhiz.com/v4/quotes"
            params = {
                "q": f"venue_id:{venue_id}",
                "start_time": start_time,
                "end_time": end_time
            }
            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()

                # If we successfully retrieved parking information, extract relevant details and return them in a structured format
                if len(result) > 0:
                    print(f"Successfully retrieved parking information for {airport_name} from ParkWhiz.")

                    # Extract relevant parking information from the JSON response
                    parking_data = []
                    for listing in result:
                        data = listing.get("_embedded", {}).get("pw:location", {})
                        # Concatenate the address into a single string to store
                        address = f"{data.get('address1')}, {data.get('city')}, {data.get('state')} {data.get('postal_code')}"
                        total_price = float(listing.get("purchase_options", [{}])[0].get("price", {}).get("USD", 0))

                        # Check availability of parking lot
                        availability_status = listing.get("purchase_options", [{}])[0].get("space_availability", {}).get("status")
                        available = availability_status == "available" or availability_status == "limited"

                        parking_data.append({
                            "ParkWhiz_provider_id": int(data.get("id")),
                            "name": data.get("name"),
                            "address": address,
                            "latitude": data.get("entrances")[0].get("coordinates")[0],
                            "longitude": data.get("entrances")[0].get("coordinates")[1],
                            "total_price": total_price,
                            "available": available
                        })

                        # Insert the listing into the database
                        add_record_to_parking_listings(parking_data[-1])
                    print(f"Extracted parking data for {airport_name} from ParkWhiz.")
                    return parking_data
                else:
                    print(f"No parking information found for {airport_name} in ParkWhiz.")
                    return None
        else:
            print(f"No venues found for {airport_name} in ParkWhiz.")
            return None
    else:
        print(f"Error fetching data from ParkWhiz: {response.status_code}")
        return None
    

def spotHero(airport_iata, start_time, end_time):
    # This function handles the API call to SpotHero
    url = "https://api.spothero.com/v2/search/airport"
    params = {
        "iata": airport_iata,
        "starts": start_time,
        "ends": end_time
    }
    print(f"Requesting SpotHero data for {airport_iata}")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Extract relevant parking information from the JSON response
        parking_data = []

        for listing in response.json().get("results", []):
            data = listing.get("facility", {}).get("common", {})

            for address_data in data.get("addresses", []):
                if "physical" in address_data.get("types", ""):
                    address = f"{address_data.get('street_address')}, {address_data.get('city')}, {address_data.get('state')} {address_data.get('postal_code')}"
                    latitude = address_data.get("latitude")
                    longitude = address_data.get("longitude")
                    break
            
            # Extract the total price from the rates array, if it exists, to use as part of the listing data. 
            total_price = (
                listing.get("rates", [{}])[0]
                .get("quote", {})
                .get("total_price", {})
                .get("value")
            )

            parking_data.append({
                "SpotHero_provider_id": int(data.get("id")),
                "name": data.get("title"),
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "total_price": total_price / 100 if total_price is not None else None,
                "available": listing.get("availability", {}).get("available")
            })

            # Insert the listing into the database
            add_record_to_parking_listings(parking_data[-1])
        print(f"Extracted parking data for {airport_iata} from SpotHero.")
        return parking_data
    else:
        print(f"Error fetching data from SpotHero: {response.status_code}")
        return None
    

def cheapAirportParking(airport_iata, start_time, end_time):
    # This function handles the API call to Cheap Airport Parking
    url = f"https://www.cheapairportparking.org/parking/find.php"

    # Format time parameters for the request
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)

    params = {
        "airport": airport_iata,
        "FromDateNice": start_dt.strftime("%b %-d"),
        "FromDate": start_dt.strftime("%m/%d/%Y"),
        "from_time": start_dt.strftime("%H"),
        "ToDateNice": end_dt.strftime("%b %-d"),
        "ToDate": end_dt.strftime("%m/%d/%Y"),
        "to_time": end_dt.strftime("%H"),
        "promo": "",
        "id_lot": ""
    }

    headers = {
        "Cookie": f"_from={start_dt.strftime('%m-%d-%Y_%H')}; "
              f"_to={end_dt.strftime('%m-%d-%Y_%H')}; "
              f"airport={airport_iata}; find=4; id_visit=1184626; n_pages=6"
    }

    print(f"Requesting Cheap Airport Parking data for {airport_iata}")
    response = requests.get(url, params=params, headers=headers)

    # This returns HTML, so we need to parse it with BeautifulSoup
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract relevant parking information from the HTML
        parking_data = []

        # Loop through all the divs that contain parking listings
        for listing in soup.select("div.my_but[onclick*='gotoMap']"):
            # Extract the parking lot name, coordinates, and provider id from the onclick attribute
            data = listing["onclick"]
            args = [x.strip().strip("'") for x in data[data.find("(")+1:data.rfind(")")].split(",")]

            # Extract the id to help find the daily rate
            CAP_provider_id = int(args[1])

            # Calculate the total price
            reservation_form = soup.select_one(f"form#parking{CAP_provider_id}")

            # Extract the total price from the form if it exists, otherwise set it to None
            price_block = reservation_form.select_one(".dayrate")

            if price_block:
                # Extract the dollars and cents from the price block and combine them to get the total price as a float
                dollars = price_block.select_one("span").text.replace("$", "")
                cents = price_block.select("span")[1].text.split()[0]
                total_price = float(dollars + cents)
            else:
                total_price = None

            # Add extracted parking listing data to the parking_data array of JSON
            parking_data.append({
                "CAP_provider_id": CAP_provider_id,
                "name": args[4],
                "address": None,  # Address is not provided in the onclick data, so we set it to None as a placeholder
                "latitude": float(args[2]),
                "longitude": float(args[3]),
                "total_price": total_price,
                "available": True if total_price is not None else False # If no total price is shown, that means it is sold out
            })
            # Insert the listing into the database
            add_record_to_parking_listings(parking_data[-1])
        print(f"Extracted parking data for {airport_iata} from Cheap Airport Parking.")
        return parking_data
    else:
        print(f"Error fetching data from Cheap Airport Parking: {response.status_code}")
        return None
    
def find_matching_listings(parking_data):
    # This function finds the matching listings after receiving the payload of all listings across all providers
    print("Finding matching listings across providers...")

    # Create a defaultdict to group listings by their rounded latitude and longitude coordinates.
    # A defaultdict allows for a key to be a tuple, in this case latitude and longitude rounded to 4 decimal places, which helps to account for minor discrepancies in coordinates across providers. Each key will map to a list of listings that share those rounded coordinates.
    matches = defaultdict(list)
    for item in parking_data:
        # Round latitude and longitude to 4 decimal places to allow for some minor discrepancies in coordinates across providers
        key = (round(item.get("latitude"), 4), round(item.get("longitude"), 4))
        matches[key].append(item)
    
    print(f"Found {len(matches)} unique locations across all providers.")
    
    print("Merging listings that have the same rounded coordinates...")
    merged_listings = []
    for listings in matches.values():
        merged_listings.append({
            "provider_ids": [
                # Extract the provider name and id for each listing that has a provider id
                {"provider": key.replace("_provider_id", ""), "id": item[key]}
                for item in listings
                for key in ["ParkWhiz_provider_id", "SpotHero_provider_id", "CAP_provider_id"]
                if item.get(key) is not None
            ],
            "names": list({item["name"] for item in listings if item.get("name")}),
            "addresses": list({item["address"] for item in listings if item.get("address")}),
            "latitude": listings[0]["latitude"],
            "longitude": listings[0]["longitude"],

        })
    print(f"Matches merged across providers: {merged_listings}")
    return merged_listings

