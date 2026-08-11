# Nimbus: A Weather-Aware Routing App

## Introduction

Nimbus predicts the weather along your ride by pairing forecast data with your calculated arrival time at every waypoint.

## Features

Nimbus uses on-map selection for origin and destination locations. Users can choose between travel modes: Driving, Cycling, and Walking. This adjusts the ETA of the route accordingly by estimating the average speed of the user.

Weather calculations are done according to the ETA of the user to the point of interest, essentially giving the user a peek at the possible weather conditions within the area. Nimbus uses radial limits to save time and usage on API requests. This shows waypoints that are >= 2km from each other, and only checks the weather for those select waypoints.

## Limitations

- OSM Requires highly-specific naming for addresses (I recommend using the pin system)
- API usage that may cause long loading times depending on the route distance
- Weather report accuracy may not be exactly accurate due to the nature of Open-Meteo

## Why Nimbus?

As a motorist, I found it to be a struggle to accurately check weathers for a route I take to go from one point to another, and often get caught by surprise by a localized rain shower despite seeing the weather from the origin and destination being clear. I decided to solve that problem myself by using the OpenRouteService and OpenMeteo APIs, and created the bridge between the two that ended up being Nimbus.

## Acknowledgements and AI Use

Nimbus uses [OpenRouteService](https://openrouteservice.org/) and [OpenMeteo](https://open-meteo.com/), which are two great publically available APIs.

I engineered and built the backend architecture, MVC data pipeline, spatial filtering calculations, and multi-API integrations in Python. Utilized Claude/LLMs as a productivity tool to accelerate Streamlit UI components and layout prototyping.
