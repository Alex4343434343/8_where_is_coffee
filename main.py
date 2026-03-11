import json
import requests
import folium
import os
from dotenv import load_dotenv
from geopy import distance

NUMBER_OF_CAFE = 5


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember'
    ]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_the_distance(spacing):
    return spacing['distance']


def main():

    load_dotenv()
    api_key = os.getenv('APIKEY')

    with open('files/coffee.json', 'r', encoding='CP1251') as my_file:
        file_contents_str = my_file.read()

    file_contents = json.loads(file_contents_str)

    your_place = input('Где Вы находитесь? ')
    your_coordinates = fetch_coordinates(api_key, your_place)
    your_coordinates = (float(your_coordinates[1]), float(your_coordinates[0]))

    new_file_contents = []

    for cafe in file_contents:

        title = cafe['Name']
        latitude = cafe['geoData']['coordinates'][1]
        longitude = cafe['geoData']['coordinates'][0]
        cafe_coordinates = (latitude, longitude)
        dist = distance.distance(your_coordinates, cafe_coordinates).m

        new_file_contents.append({
            'title': title,
            'distance': dist,
            'latitude': latitude,
            'longitude': longitude
        })

    nearest_cafe = sorted(
        new_file_contents,
        key=get_the_distance
    )[:NUMBER_OF_CAFE]

    m = folium.Map(your_coordinates, zoom_start=24)

    folium.Marker(
        location=your_coordinates,
        tooltip='Вы',
        popup='Вы',
        icon=folium.CustomIcon(
            'man.png',
            icon_size=(40, 60)
        ),
    ).add_to(m)

    for i in range(NUMBER_OF_CAFE):

        folium.Marker(
            location=[
                nearest_cafe[i]['latitude'],
                nearest_cafe[i]['longitude']
            ],
            tooltip='{coordinates} метров'.format(
                coordinates=round(nearest_cafe[i]['distance'])
            ),
            popup=nearest_cafe[i]['title'],
            icon=folium.CustomIcon(
                'coffee_cup.png',
                icon_size=(60, 60)
            ),
        ).add_to(m)

    trail_coordinates = []

    for i in range(NUMBER_OF_CAFE):

        trail_coordinates.append([
            your_coordinates,
            [nearest_cafe[i]['latitude'], nearest_cafe[i]['longitude']]
        ])

    for i, coords in enumerate(trail_coordinates):

        folium.PolyLine(
            coords,
            tooltip='{name} {distance} метров'.format(
                name=nearest_cafe[i]['title'],
                distance=round(nearest_cafe[i]['distance'])
            )
        ).add_to(m)

    m.save('index.html')


if __name__ == '__main__':
    main()
