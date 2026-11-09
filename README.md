# ACP Brevet Time Calculator
By Chris Warner - cbwar@uoregon.edu

A Flask and Ajax worksheet for calculating control opening and closing times
for 200, 300, 400, 600, and 1000 km ACP brevets.

## Run locally

Use Python 3.10 or newer. From the repository root:

```sh
cd brevets
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate` on Windows or
`source .venv/bin/activate` on macOS/Linux, then run:

```sh
python -m pip install -r requirements.txt
python flask_brevets.py
```

Open [the calculator](http://localhost:5000). The port can be changed with
`python flask_brevets.py --port 5001`.

## Run with Docker

From the repository root:

```sh
docker build -t brevets ./brevets
docker run --rm -p 127.0.0.1:5000:5000 brevets
```

Open [the calculator](http://localhost:5000). Stop the container with Ctrl+C.

## Use the worksheet

Select the nominal brevet distance, start date, and start time. Enter each
control's distance from the start in kilometers or miles; its other distance
field and opening/closing times update automatically. Zero is a valid control
distance. Location names are optional.

Changing the brevet distance or start date/time recalculates populated rows.
Clearing a distance clears that row's converted distance and times. Invalid
entries and failed requests produce a message in the row's Notes column.

The start date defaults to today, and the start time defaults to midnight.
The browser supplies its local UTC offset for the selected start date/time.
Results show the full date and 24-hour time, using that same offset throughout
the brevet, including across daylight-saving transitions.