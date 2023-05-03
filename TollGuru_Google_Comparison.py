import json
import time

import pandas as pd
import requests

import config


# Function to get the toll rates from TollGuru API
def get_tg_api_response(polyline, vehicle_type):
    url = "https://apis.tollguru.com/toll/v2/complete-polyline-from-mapping-service"

    payload = json.dumps(
        {
            "vehicleType": vehicle_type,
            "source": "google",
            "polyline": polyline,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "x-api-key": f"{config.TOLLGURU_API_KEY}",
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=10
    ).json()

    tollguru_transponder_cash = response["route"]["costs"].get("tagAndCash", "NA")
    tollguru_transponder = response["route"]["costs"].get("tag", "NA")
    tollguru_cash = response["route"]["costs"].get("cash", "NA")
    tollguru_license_plate = response["route"]["costs"].get("licensePlate", "NA")
    tollguru_prepaid = response["route"]["costs"].get("prepaidCard", "NA")

    return (
        tollguru_transponder,
        tollguru_cash,
        tollguru_transponder_cash,
        tollguru_license_plate,
        tollguru_prepaid,
    )


# Function to get the route information from Google Maps API
def get_google_api_response(o_lat, o_long, d_lat, d_long, google_toll_pass):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    payload = json.dumps(
        {
            "origin": {
                "location": {"latLng": {"latitude": o_lat, "longitude": o_long}}
            },
            "destination": {
                "location": {"latLng": {"latitude": d_lat, "longitude": d_long}}
            },
            "travelMode": "DRIVE",
            "polylineQuality": "HIGH_QUALITY",
            "computeAlternativeRoutes": False,
            "extraComputations": ["TOLLS"],
            "routeModifiers": {
                "vehicleInfo": {"emissionType": "GASOLINE"},
                "tollPasses": [google_toll_pass],
                "avoidTolls": False,
            },
        }
    )
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": f"{config.GOOGLE_API_KEY}",
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.travelAdvisory.tollInfo,routes.legs.travelAdvisory.tollInfo,routes.polyline.encodedPolyline",
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=10
    ).json()

    polyline = response["routes"][0]["polyline"]["encodedPolyline"]
    try:
        currency_code = response["routes"][0]["legs"][0]["travelAdvisory"]["tollInfo"][
            "estimatedPrice"
        ][0]["currencyCode"]
        unit = response["routes"][0]["legs"][0]["travelAdvisory"]["tollInfo"][
            "estimatedPrice"
        ][0].get("units", "0")
        nanos = response["routes"][0]["legs"][0]["travelAdvisory"]["tollInfo"][
            "estimatedPrice"
        ][0].get("nanos", "0")
        cost = float(unit) + (float(nanos) / 10**9)
        return polyline, currency_code, cost
    except Exception:
        return polyline, "NA", "NA"


def main():
    # Read input data from CSV file
    df = pd.read_csv(INPUT, encoding="utf-8-sig")
    output_df = pd.DataFrame()

    for idx, row in df.iterrows():
        print(f"Working on case: {idx+1} of {len(df)}")

        # Get route information from Google Maps API
        google_poly, google_currency, google_cash_cost = get_google_api_response(
            o_lat=row.origin_latitude,
            o_long=row.origin_longitude,
            d_lat=row.destination_latitude,
            d_long=row.destination_longitude,
            google_toll_pass=-1,
        )
        google_poly, google_currency, google_tag_cost = get_google_api_response(
            o_lat=row.origin_latitude,
            o_long=row.origin_longitude,
            d_lat=row.destination_latitude,
            d_long=row.destination_longitude,
            google_toll_pass=row.google_google_toll_pass,
        )

        (
            tollguru_transponder,
            tollguru_cash,
            tollguru_transponder_cash,
            tollguru_license_plate,
            tollguru_prepaid,
        ) = get_tg_api_response(
            polyline=google_poly,
            vehicle_type=row.tollguru_vehicle,
        )

        _dict = {
            "id": row.id,
            "origin_latitude": row.origin_latitude,
            "origin_longitude": row.origin_longitude,
            "destination_latitude": row.destination_latitude,
            "destination_longitude": row.destination_longitude,
            "tollguru_vehicle": row.tollguru_vehicle,
            "google_toll_pass": row.google_toll_pass,
            "google_currency": google_currency,
            "google_tag_cost": google_tag_cost,
            "google_cash_cost": google_cash_cost,
            "tollguru_transponder": tollguru_transponder,
            "tollguru_cash": tollguru_cash,
            "tollguru_transponder_cash": tollguru_transponder_cash,
            "tollguru_license_plate": tollguru_license_plate,
            "tollguru_prepaid": tollguru_prepaid,
        }

        output_df = output_df.append(pd.DataFrame([_dict]), ignore_index=True)
        time.sleep(1)

    output_df.to_csv(OUTPUT, encoding="utf-8-sig", index=False)


if __name__ == "__main__":
    INPUT = "sample-input.csv"
    OUTPUT = "sample-output.csv"
    main()
