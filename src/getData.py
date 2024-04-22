import os
import requests
import json
from random import choice


def getData(city, state, country, bbox, file, debug):
    print("Fetching data...")
    api_servers = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    url = choice(api_servers)
    if city or state or country: 
        query1 = f"""
        [out:json];
        area[name="{city}"]->.city;
        area[name="{state}"]->.state;
        area[name="{country}"]->.country;
        (
            way(area.country)(area.state)(area.city)[building];
            way(area.country)(area.state)(area.city)[highway];
            way(area.country)(area.state)(area.city)[landuse];
            way(area.country)(area.state)(area.city)[natural];
            way(area.country)(area.state)(area.city)[leisure];
            way(area.country)(area.state)(area.city)[waterway]["waterway"!="fairway"];
            way(area.country)(area.state)(area.city)[amenity];
            way(area.country)(area.state)(area.city)[bridge];
            way(area.country)(area.state)(area.city)[railway];
            way(area.country)(area.state)(area.city)[barrier];
        );
        (._;>;);
        out;
        """
    elif bbox:
        bbox = bbox.split(",")
        bbox = [float(i) for i in bbox]
        print(bbox)
        
        query1 = f"""
        [out:json][bbox:{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}];
        ( 
            nwr["building"];
            nwr["highway"];
            nwr["landuse"];
            nwr["natural"];
            nwr["leisure"];
            nwr["waterway"];
            nwr["amenity"];
            nwr["bridge"];
            nwr["railway"];
            nwr["barrier"];
        );
        (._;>;);
        out;
        """
    elif file:
        print("Loading data from file")
    else:
        print("Error! No data provided")
        
    try:
        if file:
            with open("data.json") as dataset:
                data = json.load(dataset)
        else:
            print(f"Chosen server: {url}")
            data = requests.get(url, params={"data": query1}).json()

        if len(data["elements"]) == 0:
            print("Error! No data available")
            os._exit(1)
    except Exception as e:
        if "The server is probably too busy to handle your request." in str(e):
            print("Error! OSM server overloaded")
        elif "Dispatcher_Client::request_read_and_idx::rate_limited" in str(e):
            print("Error! IP rate limited")
        else:
            print(f"Error! {e}")
        os._exit(1)

    if debug:
        with open("arnis-debug-raw_data.json", "w", encoding="utf-8") as f:
            f.write(str(data))
    return data
