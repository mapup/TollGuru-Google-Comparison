# TollGuru-Google-comparison
This is a Python script that calculates toll rates for a given route using the Google Maps API and TollGuru API. The script takes input data from a CSV file containing origin and destination coordinates, vehicle type, and toll pass information. It then uses the Google Maps API to get the route information and TollGuru API to get the toll rates for the route.

The output is a CSV file containing the input data and the toll rates for the route.

## Getting Started
To use this script, you will need to have a Google Maps API key and a TollGuru API key. You can get a Google Maps API key by following the instructions [here](https://developers.google.com/maps/documentation/directions/get-api-key). You can get a TollGuru API key by signing up [here](https://tollguru.com/).

Once you have your API keys, you will need to create a config.py file in the same directory as the script with the following content:
> TOLLGURU_API_KEY = "Your TollGuru API key"

> GOOGLE_API_KEY = "Your Google route API key"



### Usage
To use the script, you will need to create a CSV file containing the input data. The CSV file should have the following columns:

- **id**: Unique identifier for the route
- **origin_latitude**: Latitude of the origin
- **origin_longitude**: Longitude of the origin
- **destination_latitude**: Latitude of the destination
- **destination_longitude**: Longitude of the destination
- **tollguru_vehicle**: Vehicle type for TollGuru API (e.g. "2AxlesAuto")
- **google_toll_pass**: Toll pass information (e.g. "IN_FASTAG")


Once you have created the CSV file, you can run the script by running the following command:
> python **TollGuru_Google_Comparison.py**

The script will read the input data from the CSV file, calculate the toll rates using the Google Maps API and TollGuru API, and write the output to a CSV file.
