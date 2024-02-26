from typing import Union
from fastapi import APIRouter, FastAPI, Request
from fastapi.templating import Jinja2Templates

from simple_dwd_weatherforecast import dwdforecast
from datetime import datetime, timedelta, timezone

import dvb

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
def home(request: Request):
    print("Oh no!")
    return templates.TemplateResponse("index.html", {"request": request})


def start_application():
    app = FastAPI(title="DVB Abfahrt", version="0.1")
    app.include_router(router)
    return app


def kelvin2celsius(temp):
    return temp - 273.15


def get_weather():
    dwd_weather = dwdforecast.Weather("10487")
    time_now = datetime.now(timezone.utc)
    temperature = "{:.2f}".format(
        kelvin2celsius(
            dwd_weather.get_forecast_data(
                dwdforecast.WeatherDataType.TEMPERATURE, time_now
            )
        )
    )
    cloudcoverage = dwd_weather.get_forecast_data(
        dwdforecast.WeatherDataType.CLOUD_COVERAGE, time_now
    )
    windspeed = dwd_weather.get_forecast_data(
        dwdforecast.WeatherDataType.WIND_SPEED, time_now
    )
    sun_duration = "{:.0f}".format(
        dwd_weather.get_forecast_data(
            dwdforecast.WeatherDataType.SUN_DURATION, time_now
        )
        / 60
    )
    fog_probability = dwd_weather.get_forecast_data(
        dwdforecast.WeatherDataType.FOG_PROBABILITY, time_now
    )
    return [
        ["Temperatur", f"{temperature} ºC"],
        ["Bewölkung", f"{cloudcoverage} %"],
        ["Wind", f"{windspeed} m/s"],
        ["Sonnendauer", f"{sun_duration} min"],
        ["Nebelwahrscheinlichkeit", f"{fog_probability} %"],
    ]


def get_schedules(station="Bahnhof Neustadt"):
    """Return the DVB schedule"""
    time_offset = 0
    num_results = 5
    city = "Dresden"
    return dvb.monitor(station, time_offset, num_results, city)


@router.get("/abfahrt")
def render_standard_template(request: Request):
    """Return the Weather and DVB schedule for Mosenstrasse"""
    return render_station_template(request, "Mosenstrasse")


@router.get("/abfahrt/{station}")
def render_station_template(request: Request, station: str):
    """Return the rendered HTML"""
    schedules = get_schedules(station=station)
    weather = get_weather()
    return templates.TemplateResponse(
        "abfahrt.html",
        {"request": request, "title": station, "schedules": schedules, "weather": weather},
    )


app = start_application()
