#!/usr/local/bin/python3

import sys
from datetime import datetime, timedelta


# Global variables
g_records = [] # 2D list with flight records
g_records_len = 0 # Number of records in g_records
g_exit_code = 0


# /**
# * Prints help message(-h, --help arguments)
# */
def print_help():
    sys.stdout.write("Program searches for connections between flights with time for transfer(1-4hours).\nIt accepts flight records in format:\nsource airport,destination airport,departure,arrival,flight number\nDeparture and Arrival datetimes are in ISO 8601 format %Y-%m-%dT%H:%M:%S\nExample of flight record:\nUSM,HKT,2016-10-11T10:10:00,2016-10-11T11:10:00,PV511\n\nInput is taken from stdin.\nProgram outputs itineraries of 2 or more connecting flights on stdout.\nEach itinerary is on newline, individual flights in itinerary are separated by ';'.")
    exit(0)

# /**
# * Checks input from stdin for errors and stores valid flight records 
# * in global 2D list g_records
# */
def get_check_input():
    for line in sys.stdin:
        # Skips line if it is column names
        if(line == "source,destination,departure,arrival,flight_number\n"):
            continue

        details = line.split(',') # Split flight record into list
        if(len(details) != 5): # not enough/too much information
            error_handling(2) # Write wrong number of params error
            continue # And ignore this line

        # Check datetime format and convert it
        try:
            dep_format = datetime.strptime(details[2], '%Y-%m-%dT%H:%M:%S')
            arr_format = datetime.strptime(details[3], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            error_handling(3) # Write wrong datetime error
            continue # Ignore this line


        # Strip newlines from flight number
        flight_num = details[4].replace('\n','')
 
        # Make list - record of one flight, add to g_records with all records
        flight = [details[0], details[1], dep_format, arr_format, flight_num]
        g_records.append(flight)
    return 0

# /**
# * Writes error message on stderr and changes exit code of script
# * @param err_num error number to identify specific error
# */
def error_handling(err_num):
    global g_exit_code # use global variable

    if(err_num == 1):
        sys.stderr.write ("Error: Wrong script arguments. -h or --help are only ones accepted.\n")
        g_exit_code = 1            
    elif (err_num == 2):
        sys.stderr.write ("Error: Not enough or too many columns on a line. Line ignored.\n")
        g_exit_code = 2
    elif(err_num == 3):
        sys.stderr.write ("Error: DateTime format of arrival or departure is wrong. Line ignored.\n")
        g_exit_code = 3
    return 0

        
# /**
# * Recursive function which searches for connections between flights
# * @param flight_history history of previously visited places and times of arrivals
# * @param record_id list of indexes in g_records of previous flights
# * @return record_id list of indexes in g_records of used connections
# */
def find_combinations(flight_history, record_id):
    # Goes through all records, keeps track of index of record
    for next_index,next_destination in enumerate(g_records):
        # Create time limits for transfer between flights
        time_min = flight_history[-2] + timedelta(hours=1)
        time_max = flight_history[-2] + timedelta(hours=4)        

        # Finding flights that start where last flight ended
        # skips those where destination was already visited
        # and skips those which are not in time limit for transfer
        if(next_destination[0] == flight_history[-1] and
           next_destination[1] not in flight_history and
           next_destination[2] > time_min and
           next_destination[2]< time_max):

            # Store index of next flight connection
            record_id.append(next_index) 
            # Add information about next flight to history
            flight_history.append(next_destination[3]) # Time of next arrival
            flight_history.append(next_destination[1]) # Next destination
            # Find next connection recursively
            find_combinations(flight_history, record_id)
        # If all records had been gone through, return itinerary
        elif(next_index == (g_records_len - 1)):
            return(record_id)
        # Continue to next flight record
        else:
            continue
    

# Main
if __name__ == "__main__":

    # Check for script arguments
    if(len(sys.argv) > 1):
        # Only -h, --help are allowed
        if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
            print_help()
        else:
            error_handling(1)
    # Check input for errors and store it into global list g_records
    get_check_input()
    # Get number of flight records in g_records
    g_records_len = len(g_records) 


    # For each record tries to find connetions 
    for start_index,start in enumerate(g_records):
        # Initializes flight history with source, time of arrival 
        # to destination and destination
        flight_history = [start[0], start[3] ,start[1]]
        # Remeber index of a starting flight
        record_id = [start_index]
        # Start searching for connections
        itinerary_id = find_combinations(flight_history, record_id)
        # If there is at least one connection to original flight
        # print the itinerary. Itineraries are writen in original format
        # of flight record, separated by ';', each itinerary on new line
        if(len(itinerary_id) > 1):
            for index in itinerary_id:
                sys.stdout.write("%s,%s,%s,%s,%s;" % (g_records[index][0],
                                                      g_records[index][1],
                                                      g_records[index][2].strftime('%Y-%m-%dT%H:%M:%S'),
                                                      g_records[index][3].strftime('%Y-%m-%dT%H:%M:%S'),
                                                      g_records[index][4]))
            sys.stdout.write("\n") # Write newline

    # Exit with either 0 or error code of last found error in input
    exit(g_exit_code)
