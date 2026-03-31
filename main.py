import requests
import helper
import logging

def main():
    # Connect to the database
    helper.connect_db()

    # Create parking table that holds all parking listings across providers before matching
    helper.initialize_parking_table()

    # Create parking_matches table that holds the merged parking matches across providers
    helper.initialize_parking_matches_table()

    # mapping of airport IATA codes to their names
    airport1 = {'iata': 'ATL', 'name': 'Hartsfield-Jackson Atlanta International Airport'}
    airport2 = {'iata': 'DEN', 'name': 'Denver International Airport DIA'}

    # Start time and end time for parking search (example: 2024-07-01 to 2024-07-07)
    # Timezones for parkwhiz and spothero are localized in parking location timezone
    start_time = "2026-04-01T00:00:00"
    end_time = "2026-04-07T00:00:00"

    # Retrieve parking information from ParkWhiz
    parkwhiz_data1 = helper.parkWhiz(airport1['name'], start_time, end_time)
    parkwhiz_data2 = helper.parkWhiz(airport2['name'], start_time, end_time)

    # Retrieve parking information from SpotHero
    spothero_data1 = helper.spotHero(airport1['iata'], start_time, end_time)
    spothero_data2 = helper.spotHero(airport2['iata'], start_time, end_time)

    # Retrieve parking information from Cheap Airport Parking
    cap_data1 = helper.cheapAirportParking(airport1['iata'], start_time, end_time)
    cap_data2 = helper.cheapAirportParking(airport2['iata'], start_time, end_time)

    # Consolidate all parking data into a single list
    all_parking_data = spothero_data1 + spothero_data2 + parkwhiz_data1 + parkwhiz_data2 + cap_data1 + cap_data2
    print(f"Total parking listings collected: {len(all_parking_data)}")

    # Find matching listings across providers and print them
    merged_listings = helper.find_matching_listings(all_parking_data)
    # Add matches to the parking_matches table in the database
    helper.add_record_to_parking_matches(merged_listings)

if __name__ == "__main__":
    main()

