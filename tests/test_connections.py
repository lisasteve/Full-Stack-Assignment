import psycopg2
import requests
import datetime

def test_database_connection():
    # This test checks if we can connect to the PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="testuser",
        password="mysecretpassword"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()

    assert db_version is not None

def test_spothero_connection():
    # This test checks if we can retrieve data from the SpotHero API

    url = "https://api.spothero.com/v2/search/airport"
    params = {
        "iata": "ATL",
        "starts": "2026-04-01T00:00:00",
        "ends": "2026-04-07T00:00:00"
    }
    response = requests.get(url, params=params)

    assert response.status_code == 200

def test_parkwhiz_venues_connection():
    # This test checks if we can retrieve data from the ParkWhiz venue API
    url = "https://api.parkwhiz.com/v4/venues"
    params = {
        "q": "name:Hartsfield-Jackson Atlanta International Airport"
    }
    response = requests.get(url, params=params)

    assert response.status_code == 200

def test_parkwhiz_quotes_connection():
    # This test checks if we can retrieve quotes from the ParkWhiz API for a given venue id
    url = f"https://api.parkwhiz.com/v4/quotes"
    params = {
        "q": "venue_id:11",
        "start_time": "2026-04-01T00:00:00",
        "end_time": "2026-04-07T00:00:00"
    }
    response = requests.get(url, params=params)

    assert response.status_code == 200

def test_cheap_airport_parking_connection():
    # This test checks if we can retrieve data from the Cheap Airport Parking API
        # This function handles the API call to Cheap Airport Parking
    url = f"https://www.cheapairportparking.org/parking/find.php"

    # Format time parameters for the request
    start_dt = datetime.datetime.fromisoformat("2026-04-01T00:00:00")
    end_dt = datetime.datetime.fromisoformat("2026-04-07T00:00:00")

    params = {
        "airport": "ATL",
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
              f"airport=ATL; find=4; id_visit=1184626; n_pages=6"
    }

    print(f"Requesting Cheap Airport Parking data for ATL")
    response = requests.get(url, params=params, headers=headers)

    assert response.status_code == 200
    