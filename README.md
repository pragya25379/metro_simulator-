# Delhi Metro Simulator

A command-line Python program that simulates the Delhi Metro **Blue** and **Magenta** lines.

## Features

1. **Metro Timings** – check the next train arrival times at any station, in both directions.
2. **Journey Planner** – find the fastest route between two stations, including interchanges.

## Data Sources

- Station lists and order were collected from public Delhi Metro maps and the DMRC app.
- Travel times are estimated averages (about 2 min per hop on the Blue Line, 3 min on the Magenta Line) chosen to match total travel times found online.
- Interchange points: Janakpuri West, Botanical Garden.

## Assumptions

| Item | Value |
|------|-------|
| Service start | 06:00 AM |
| Service end | 11:00 PM (23:00) |
| Peak hours | 08:00–10:00 and 17:00–19:00 |
| Peak frequency | Every 4 minutes |
| Off-peak frequency | Every 8 minutes |
| Interchange delay | Fixed 5 minutes |
| Travel time | Fixed estimate between consecutive stations |
| Blue Line route | Dwarka Sector 21 → Noida Electronic City |

## Project Structure

```
delhi-metro-simulator/
├── metro_simulator.py   # Main Python program
├── metro_data.txt       # Station and line data (CSV-style)
├── README.md            # This file
├── LICENSE              # MIT License
├── .gitignore
└── .gitattributes
```

### Data file format

`metro_data.txt` has a header row followed by one row per pair of adjacent stations:

```
Line, Station, NextStation, TravelTime(min), Interchange Point
Blue, Dwarka Sector 21, Dwarka Sector 8, 2, No
```

## How to Run

1. Make sure Python 3 is installed.
2. Clone the repository and run:

```bash
git clone https://github.com/<your-username>/delhi-metro-simulator.git
cd delhi-metro-simulator
python metro_simulator.py
```

3. Follow the on-screen prompts.

## Example Usage

**Metro Timings**
- Select option `1`
- Line: `Blue`
- Station: `Rajiv Chowk`
- Time: `09:18`

**Journey Planner**
- Select option `2`
- Source: `Dwarka`
- Destination: `Botanical Garden`
- Time: `08:22`
