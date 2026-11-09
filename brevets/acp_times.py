"""Opening and closing times for ACP brevets, using RUSA's calculator rules."""

import math

import arrow


FINISH_LIMITS = {200: 810, 300: 1200, 400: 1620, 600: 2400, 1000: 4500}
OPENING_SPEEDS = ((200, 34), (400, 32), (600, 30), (1000, 28))


def _control_distance(control_dist_km, brevet_dist_km):
    try:
        distance = float(control_dist_km)
        brevet = float(brevet_dist_km)
    except (TypeError, ValueError):
        raise ValueError("Distances must be numbers.") from None
    if brevet not in FINISH_LIMITS:
        raise ValueError("Brevet distance must be 200, 300, 400, 600, or 1000 km.")
    if not math.isfinite(distance) or distance < 0:
        raise ValueError("Control distance must be a finite, nonnegative number.")
    return min(distance, brevet)


def _time_after(brevet_start_time, minutes):
    if not isinstance(brevet_start_time, str) or not brevet_start_time:
        raise ValueError("Start time must be an ISO 8601 date and time.")
    start = arrow.get(brevet_start_time)
    return start.shift(minutes=math.floor(minutes + 0.5)).isoformat()


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """Return an opening time, preserving the start's time zone.

    Distances are kilometers; the nominal brevet is 200, 300, 400, 600,
    or 1000 km. Sum time in each speed band before rounding to a minute.
    Controls beyond the nominal finish use the nominal distance.
    """
    distance = _control_distance(control_dist_km, brevet_dist_km)
    hours = 0
    previous = 0
    for boundary, speed in OPENING_SPEEDS:
        segment = min(distance, boundary) - previous
        hours += segment / speed
        if distance <= boundary:
            break
        previous = boundary
    return _time_after(brevet_start_time, hours * 60)


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """Return a closing time, preserving the start's time zone.

    Use 20 km/h plus one hour below 60 km, 15 km/h through 600 km,
    then 11.428 km/h. The finish uses the official overall time limit.
    """
    distance = _control_distance(control_dist_km, brevet_dist_km)
    if distance == float(brevet_dist_km):
        minutes = FINISH_LIMITS[float(brevet_dist_km)]
    elif distance < 60:
        minutes = 60 + distance * 3
    else:
        hours = min(distance, 600) / 15
        hours += max(distance - 600, 0) / 11.428
        minutes = hours * 60
    return _time_after(brevet_start_time, minutes)
