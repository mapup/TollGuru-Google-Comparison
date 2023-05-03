import json
import time
import warnings
from datetime import datetime
import pandas as pd
import requests
import config
from os.path import join
from geojson import LineString, Feature, FeatureCollection, dump

# from shapely.geometry import LineString
import polyline

warnings.filterwarnings("ignore")

# Function to create a GeoJSON feature from a polyline and data
def get_geojson(poly, data):

    shape = LineString(polyline.decode(poly))

    return Feature(geometry=shape, properties=data)

# Function to get the toll rates from TollGuru API
def get_tg_api_response(polyline, vehicle_type, departure_time):
    url = "https://apis.tollguru.com/toll/v2/complete-polyline-from-mapping-service"

    payload = json.dumps(
        {
            "vehicleType": vehicle_type,
            "source": "google",
            "departure_time": departure_time,
            "polyline": polyline,
        }
    )
    headers = {"Content-Type": "application/json", "x-api-key": f"{config.TG_API_KEY}"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=10
    ).json()

    tag_and_cash = response["route"]["costs"].get("tagAndCash", "NA")
    tag = response["route"]["costs"].get("tag", "NA")
    cash = response["route"]["costs"].get("cash", "NA")
    _license = response["route"]["costs"].get("licensePlate", "NA")
    prepaid = response["route"]["costs"].get("prepaidCard", "NA")
    # toll_id_list = []
    # for id in response["route"]["tolls"]:
    #     toll_id_list.append(id["id"])

    return tag, cash, tag_and_cash, _license, prepaid


# Function to get the route information from Google Maps API
def get_google_api_response(o_lat, o_long, d_lat, d_long, departure_time, toll_pass):
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
            "routingPreference": "TRAFFIC_AWARE",
            "polylineQuality": "HIGH_QUALITY",
            "departureTime": departure_time,
            "computeAlternativeRoutes": False,
            "extraComputations": ["TOLLS"],
            "routeModifiers": {
                "vehicleInfo": {"emissionType": "GASOLINE"},
                "tollPasses": [toll_pass],
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
    json_features = []

    # df = df.iloc[:1, :]
    output_df = pd.DataFrame()

    for idx, row in df.iterrows():
        print(f"Working on case: {idx+1} of {len(df)}")

        # Get route information from Google Maps API
        google_poly1, google_currency, google_cash_cost = get_google_api_response(
            o_lat=row.from_lat,
            o_long=row.from_long,
            d_lat=row.to_lat,
            d_long=row.to_long,
            departure_time=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            toll_pass=-1,
        )
        google_poly2, google_currency, google_tag_cost = get_google_api_response(
            o_lat=row.from_lat,
            o_long=row.from_long,
            d_lat=row.to_lat,
            d_long=row.to_long,
            departure_time=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            toll_pass=row.toll_pass,
        )

        if google_poly1 != "NA":
            (
                tg_tag,
                tg_cash,
                tg_tagAndCash,
                tg_license,
                tg_prepaid,
            ) = get_tg_api_response(
                polyline=google_poly1,
                vehicle_type=row.vehicle_tollguru,
                departure_time=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )
        elif google_poly2 != "NA":
            (
                tg_tag,
                tg_cash,
                tg_tagAndCash,
                tg_license,
                tg_prepaid,
            ) = get_tg_api_response(
                polyline=google_poly2,
                vehicle_type=row.vehicle_tollguru,
                departure_time=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )
        else:
            print(f"Skipping ID: {row.id}")
            continue

        _dict = {
            "id": row.id,
            "from_lat": row.from_lat,
            "from_long": row.from_long,
            "to_lat": row.to_lat,
            "to_long": row.to_long,
            "vehicle_tollguru": row.vehicle_tollguru,
            "toll_pass": row.toll_pass,
            "google_currency": google_currency,
            "google_tag_cost": google_tag_cost,
            "google_cash_cost": google_cash_cost,
            "tg_tag": tg_tag,
            "tg_cash": tg_cash,
            "tg_tagAndCash": tg_tagAndCash,
            "tg_license": tg_license,
            "tg_prepaid": tg_prepaid,
        }
        json_features.append(get_geojson(google_poly1, _dict))

        output_df = output_df.append(pd.DataFrame([_dict]), ignore_index=True)
        time.sleep(1)

    #with open(OUTPUT.split(".")[0] + ".geojson", "w") as f:
    #    dump(json_features, f)

    output_df.to_csv(OUTPUT, encoding="utf-8-sig", index=False)


if __name__ == "__main__":
    FILE = "india_test_cases_Chandigarh.csv"
    INPUT = join("input_test_cases", FILE)
    OUTPUT = join("output_test_cases", FILE)
    main()
