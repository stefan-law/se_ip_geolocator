from fastapi import FastAPI, Request, HTTPException, status
from IP2Location import IP2Location
from timezonefinder import timezone_at

import os

DB_FILE = "IP2LOCATION-LITE-DB11.IPV6.BIN"

app = FastAPI()

# Ensure there is enough RAM to run locally, otherwise delete shared memory mode
database = IP2Location(os.path.join("data", DB_FILE), "SHARED_MEMORY")


@app.get("/location/")
async def locate(request: Request):
    # Get client IP
    client_host = request.client.host

    # Query databse for geolocation by IP
    rec = database.get_all(client_host)

    # Ensure that location is located in the US
    if rec.country_short != "US":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geolocation currently only compatible with US locations IP: {client_host}",
        )

    # Translate and update UTC offset to a more useful timezone
    tz = timezone_at(lng=rec.longitude, lat=rec.latitude)
    rec.timezone = tz

    # Make state field more user-friendly
    rec = rec.__dict__
    rec["state"] = rec["region"]

    return rec
