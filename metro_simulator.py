def parse_time(time_str):
    """
    Converts a time string like '09:30' into minutes from midnight.
    Example: '01:00' -> 60 minutes.
    """
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    except:
        return None
def format_time(total_minutes):
    """
    Converts minutes from midnight back to a time string like '09:30'.
    """
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    # The :02d means "format as a 2-digit number, adding a 0 in front if needed"
    
    return f"{hours:02d}:{minutes:02d}"
    def match_name(text, options):
    for option in options:
        if option.lower() == text.lower():
            return option
    return text
class MetroSimulator:
    def __init__(self):
        # We will store our data in these dictionaries (like digital address books)
        self.stations = {}      # Stores station info
        self.lines = {}         # Stores the list of stations for each line
        self.travel_times = {}  # Stores time to travel between two stations
        
        # Service hours (in minutes from midnight)
        self.start_time = 6 * 60   # 06:00 AM
        self.end_time = 23 * 60    # 11:00 PM

    def load_data(self, filename="metro_data.txt"):
        """Reads the station data from the text file."""
        try:
            file = open(filename, 'r')
            lines = file.readlines()
            file.close()
        except:
            print(f"Error: Could not find file {filename}")
            return False

        # Loop through each line in the file
        # We skip the first line because it is just the header
        for i in range(1, len(lines)):
            line = lines[i].strip() # Remove extra spaces
            parts = line.split(',') # Split by comma
            
            if len(parts) < 5:
                continue
            
            # Get the data from the line
            line_name = parts[0].strip()
            station1 = parts[1].strip()
            station2 = parts[2].strip()
            time_taken = int(parts[3].strip())
            
            # Add the line to our records if it's new
            if line_name not in self.lines:
                self.lines[line_name] = []
            
            # Add stations to the line list if they aren't there yet
            # We are building the list of stations in order
            current_line_stations = self.lines[line_name]
            
            if len(current_line_stations) == 0:
                current_line_stations.append(station1)
            
            # If the last station we added is the same as station1, then station2 is next
            if current_line_stations[-1] == station1:
                current_line_stations.append(station2)
            
            # Store the travel time between these two stations
            # We store it both ways: A->B and B->A
            self.travel_times[(station1, station2)] = time_taken
            self.travel_times[(station2, station1)] = time_taken

        return True

    def get_frequency(self, current_time_minutes):
        """Returns how often trains come (in minutes) based on the time of day."""
        # Peak Hours: 8:00 AM - 10:00 AM (480 - 600 minutes)
        # Peak Hours: 5:00 PM - 7:00 PM (1020 - 1140 minutes)
        
        is_morning_peak = (current_time_minutes >= 480 and current_time_minutes < 600)
        is_evening_peak = (current_time_minutes >= 1020 and current_time_minutes < 1140)
        
        if is_morning_peak or is_evening_peak:
            return 4 # Every 4 minutes
        else:
            return 8 # Every 8 minutes

    def get_next_trains(self, line_name, station_name, current_time):
        """Finds the next train arrival time for a station."""
        
        # Check if the station exists on this line
        if line_name not in self.lines:
            return []
        
        stations_on_line = self.lines[line_name]
        if station_name not in stations_on_line:
            return []

        # We need to find trains going in both directions
        results = []

        # Direction 1: Towards the last station (Down)
        last_station = stations_on_line[-1]
        if station_name != last_station:
            # Calculate when the first train (6:00 AM) reaches here
            time_from_start = 0
            
            # Add up travel time from the first station to our station
            station_index = stations_on_line.index(station_name)
            for i in range(station_index):
                s1 = stations_on_line[i]
                s2 = stations_on_line[i+1]
                time_from_start += self.travel_times[(s1, s2)]
            
            first_train_arrival = self.start_time + time_from_start
            
            # Find the next train after current_time
            next_arrival = self.find_next_arrival_time(first_train_arrival, current_time)
            
            if next_arrival:
                results.append({
                    "direction": last_station,
                    "time": next_arrival
                })
        # Direction 2: Towards the first station (Up)
        first_station = stations_on_line[0]
        if station_name != first_station:
            # Calculate when the first train (6:00 AM) from the other end reaches here
            time_from_end = 0
            
            # Add up travel time from the last station backwards to our station
            station_index = stations_on_line.index(station_name)
            for i in range(len(stations_on_line) - 1, station_index, -1):
                s1 = stations_on_line[i]
                s2 = stations_on_line[i-1]
                time_from_end += self.travel_times[(s1, s2)]
                
            first_train_arrival = self.start_time + time_from_end
            next_arrival = self.find_next_arrival_time(first_train_arrival, current_time)
            if next_arrival:
                results.append({
                    "direction": first_station,
                    "time": next_arrival
                })
                
        return results
    def find_next_arrival_time(self, first_train_time, current_time):
        """
        Calculates the next train arrival.
        It simulates trains starting from the first train until one arrives after current_time.
        """
        # The 'offset' is how long it takes to get to our station from the start of the line
        travel_duration = first_train_time - self.start_time
        
        # Start simulating train departures from the origin at 6:00 AM
        departure_time = self.start_time
        
        while departure_time < self.end_time:
            # When does this train arrive at our station?
            arrival_time = departure_time + travel_duration
            
            # If this train arrives after (or at) the current time, it's the one we want!
            if arrival_time >= current_time:
                return arrival_time
            
            # Otherwise, check the next train
            frequency = self.get_frequency(departure_time)
            departure_time += frequency
            
        return None

    def plan_journey(self, start_station, end_station, time_str):
        """Finds the best route between two stations."""
        current_time = parse_time(time_str)
        if current_time is None:
            return "Invalid time format."
            
        if current_time < self.start_time or current_time >= self.end_time:
            return "No service available (06:00 AM - 11:00 PM)."

        # We use a list to keep track of paths we are exploring
        # Each item is: (arrival_time, current_station, path_history, current_line)
        paths_to_explore = []
        
        # Start at the source station
        paths_to_explore.append((current_time, start_station, [], None))
        
        # Keep track of the fastest time we've reached each station to avoid loops
        visited_stations = {} 
        
        best_journey = None
        
        while len(paths_to_explore) > 0:
            # 1. Find the path that has the earliest arrival time so far
            best_index = 0
            for i in range(1, len(paths_to_explore)):
                if paths_to_explore[i][0] < paths_to_explore[best_index][0]:
                    best_index = i
            
            # Remove it from the list to process it
            current_arrival_time, current_station, history, current_line = paths_to_explore.pop(best_index)
            
            # If we reached the destination, we found the best path!
            if current_station == end_station:
                best_journey = (current_arrival_time, history)
                break
            
            # If we've been here before faster, skip this path
            state = (current_station, current_line)
            if state in visited_stations and visited_stations[state] <= current_arrival_time:
                continue
            visited_stations[state] = current_arrival_time        

            # 2. Explore where we can go from here
            
            # Find all lines connected to this station
            connected_lines = []
            for line_name in self.lines:
                if current_station in self.lines[line_name]:
                    connected_lines.append(line_name)
            
            for line in connected_lines:
                # Calculate delay if we are changing lines
                delay = 0
                if current_line is not None and line != current_line:
                    delay = 5 # 5 minutes to change lines
                
                # When are we ready to leave?
                ready_to_depart_time = current_arrival_time + delay
                
                # Find neighbors (stations next to this one on this line)
                stations_list = self.lines[line]
                index = stations_list.index(current_station)
                neighbors = []
                if index > 0: 
                    neighbors.append(stations_list[index-1]) # Previous station
                if index < len(stations_list) - 1: 
                    neighbors.append(stations_list[index+1]) # Next station
                
                for neighbor in neighbors:
                    travel_time = self.travel_times[(current_station, neighbor)]
                    
                    # Find the direction of the train
                    if stations_list.index(neighbor) > index:
                        direction = stations_list[-1] # Going down
                    else:
                        direction = stations_list[0]  # Going up
                    
                    # Find the next train time
                    next_train_time = self.get_specific_train_time(line, current_station, direction, ready_to_depart_time)
                    
                    if next_train_time:
                        arrival_at_neighbor = next_train_time + travel_time
                        
                        # Record this step
                        new_step = {
                            "station": current_station,
                            "line": line,
                            "departure": next_train_time,
                            "next_station": neighbor
                        }
                        new_history = history + [new_step]
                        
                        paths_to_explore.append((arrival_at_neighbor, neighbor, new_history, line))

        if best_journey:
            return self.print_journey(best_journey, start_station, end_station)
        else:
            return "No route found."
    def get_specific_train_time(self, line, station, direction_end, time_after):
        """Helper to find the next train time for a specific direction."""
        stations = self.lines[line]
        idx = stations.index(station)
        
        if direction_end == stations[-1]: 
            # Going towards end
            time_from_start = 0
            for i in range(idx):
                time_from_start += self.travel_times[(stations[i], stations[i+1])]
            first_arrival = self.start_time + time_from_start
        else: 
            # Going towards start
            time_from_end = 0
            for i in range(len(stations) - 1, idx, -1):
                time_from_end += self.travel_times[(stations[i], stations[i-1])]
            first_arrival = self.start_time + time_from_end
            
        return self.find_next_arrival_time(first_arrival, time_after)

    def print_journey(self, journey_data, source, dest):
        final_time, steps = journey_data
        output = ["Journey Plan:"]
        
        # The first step tells us where we started
        first_step = steps[0]
        current_line = first_step['line']
        
        output.append(f"Start at {source} ({current_line} Line)")
        output.append(f"Next metro at {format_time(first_step['departure'])}")
        
        # Loop through the steps to find interchanges
        for i in range(len(steps)):
            step = steps[i]
            
            # If the line changes, it means we transferred
            if step['line'] != current_line:
                # The previous step brought us here
                prev_step = steps[i-1]
                arrival_time = prev_step['departure'] + self.travel_times[(prev_step['station'], prev_step['next_station'])]
                
                output.append(f"Arrive at {step['station']} at {format_time(arrival_time)}")
                output.append(f"Transfer to {step['line']} Line")
                output.append(f"Next {step['line']} metro departs at {format_time(step['departure'])}")
                
                current_line = step['line']
        
        output.append(f"Arrive at {dest} at {format_time(final_time)}")
        
        # Calculate total time
        # Start time is when the first train departed (roughly)
        # Or better, the user's input time? We don't have it here easily.
        # Let's use the first train departure as the start of the "trip"
        start_time = steps[0]['departure']
        total_minutes = final_time - start_time
        # Note: This doesn't include the initial wait at the first station, but it's close.
        
        output.append(f"Total travel time: {total_minutes} minutes")
        
        return "\n".join(output) 
# Main Program
def main():
    sim = MetroSimulator()
    if not sim.load_data():
        return

    print("Delhi Metro Simulator")
    print("---------------------")
    print("1. Check Metro Timings")
    print("2. Plan a Journey")
    print("3. Exit")
    all_stations = [s for stations in sim.lines.values() for s in stations]
    
    while True:
        choice = input("\nEnter your choice (1/2/3): ")
        
        if choice == '1':
            line = input("Enter Line (Blue/Magenta): ").strip()
            station = input("Enter Station Name: ").strip()
            time_str = input("Enter Current Time (HH:MM): ").strip()
            src = match_name(src, all_stations)
            dst = match_name(dst, all_stations)
            
            current_min = parse_time(time_str)
            if current_min is None:
                print("Invalid time. Please use HH:MM format.")
                continue
                
            trains = sim.get_next_trains(line, station, current_min)
            if not trains:
                print("No trains found. Check station name or line.")
            else:
                for t in trains:
                    print(f"Towards {t['direction']}: Next metro at {format_time(t['time'])}")
                    
                    # Show subsequent trains
                    freq = sim.get_frequency(t['time'])
                    t2 = t['time'] + freq
                    t3 = t2 + sim.get_frequency(t2)
                    print(f"  Next trains at {format_time(t2)}, {format_time(t3)}")

        elif choice == '2':
            src = input("Source Station: ").strip()
            dst = input("Destination Station: ").strip()
            time_str = input("Time of Travel (HH:MM): ").strip()
            
            plan = sim.plan_journey(src, dst, time_str)
            print(plan)
            
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
                
