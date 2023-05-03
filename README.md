# TollGuru-Google-comparison
This is a Python script that calculates toll rates for a given route using the Google Maps API and TollGuru API. The script takes input data from a CSV file containing origin and destination coordinates, vehicle type, and toll pass information. It then uses the Google Maps API to get the route information and TollGuru API to get the toll rates for the route.

The output is a CSV file containing the input data and the toll rates for the route. Additionally, a GeoJSON file is created containing the route polyline and toll information.

## Getting Started
To use this script, you will need to have a Google Maps API key and a TollGuru API key. You can get a Google Maps API key by following the instructions [here](https://developers.google.com/maps/documentation/directions/get-api-key). You can get a TollGuru API key by signing up [here](https://tollguru.com/).

Once you have your API keys, you will need to create a config.py file in the same directory as the script with the following content:
> GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

> TG_API_KEY = "YOUR_TOLLGURU_API_KEY"

### Requirements

> requests==2.26.0

> pandas==1.3.3

> geojson==2.5.0

> polyline==1.4.0



### Usage
To use the script, you will need to create a CSV file containing the input data. The CSV file should have the following columns:

- **id**: Unique identifier for the route
- **from_lat**: Latitude of the origin
- **from_long**: Longitude of the origin
- **to_lat**: Latitude of the destination
- **to_long**: Longitude of the destination
- **vehicle_tollguru**: Vehicle type for TollGuru API (e.g. "2AxlesAuto")
- **toll_pass**: Toll pass information (e.g. "NHAI Monthly Pass")


Once you have created the CSV file, you can run the script by running the following command:
> python **google_tg_comparison.py**

The script will read the input data from the CSV file, calculate the toll rates using the Google Maps API and TollGuru API, and write the output to a CSV file and a GeoJSON file.
