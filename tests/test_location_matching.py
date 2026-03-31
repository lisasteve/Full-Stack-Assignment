from helper import find_matching_listings   # update import if needed


def test_same_coordinates_are_grouped_as_match():
    # This test checks that two listings with the same latitude and longitude are grouped as a match
    parking_data = [
        {
            "name": "Lot A",
            "address": "123 Main St",
            "latitude": 33.640700,
            "longitude": -84.427700,
            "ParkWhiz_provider_id": 101,
            "SpotHero_provider_id": None,
            "CAP_provider_id": None,
        },
        {
            "name": "Lot B",
            "address": "123 Main St",
            "latitude": 33.640700,
            "longitude": -84.427700,
            "ParkWhiz_provider_id": None,
            "SpotHero_provider_id": 202,
            "CAP_provider_id": None,
        },
    ]

    result = find_matching_listings(parking_data)

    assert len(result) == 1
    assert len(result[0]["provider_ids"]) == 2


def test_different_latitudes_are_not_grouped_as_match():
    # This test checks that two listings with different latitudes are not grouped as a match
    parking_data = [
        {
            "name": "Lot A",
            "address": "123 Main St",
            "latitude": 33.6407,
            "longitude": -84.4277,
            "ParkWhiz_provider_id": 101,
            "SpotHero_provider_id": None,
            "CAP_provider_id": None,
        },
        {
            "name": "Lot B",
            "address": "123 Main St",
            "latitude": 33.6507,
            "longitude": -84.4277,
            "ParkWhiz_provider_id": None,
            "SpotHero_provider_id": 202,
            "CAP_provider_id": None,
        },
    ]

    result = find_matching_listings(parking_data)

    assert len(result) == 2


def test_different_longitudes_are_not_grouped_as_match():
    # This test checks that two listings with different longitudes are not grouped as a match
    parking_data = [
        {
            "name": "Lot A",
            "address": "123 Main St",
            "latitude": 33.6407,
            "longitude": -84.4277,
            "ParkWhiz_provider_id": 101,
            "SpotHero_provider_id": None,
            "CAP_provider_id": None,
        },
        {
            "name": "Lot B",
            "address": "123 Main St",
            "latitude": 33.6407,
            "longitude": -84.4377,  # different longitude
            "ParkWhiz_provider_id": None,
            "SpotHero_provider_id": 202,
            "CAP_provider_id": None,
        },
    ]

    result = find_matching_listings(parking_data)

    assert len(result) == 2
    