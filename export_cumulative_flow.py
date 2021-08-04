import json
import sys
import csv
from datetime import datetime
from calendar import timegm
import time
import os

USAGE = sys.argv[0] + " <CUMULATIVE_FLOW_JSON_FILE> <from:YYYY-mm-dd> <to:YYYY-mm-dd>"

if len(sys.argv) < 4:
    raise Exception("USAGE: " + USAGE)

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = os.path.splitext(INPUT_FILE)[0] + ".csv"
FROM_STR = sys.argv[2]
TO_STR = sys.argv[3]

print("Cumulative flow written to: " + OUTPUT_FILE)

def get_day_from_timestamp(timestamp_seconds):
    return datetime.utcfromtimestamp(timestamp_seconds).strftime('%Y-%m-%d')

def get_timestamp_from_day(date_day):
    return int(timegm(datetime.strptime(date_day, "%Y-%m-%d").utctimetuple()))

def timestamp_millis_to_epoch_day(timestamp_millis):
    return int(timestamp_millis/1000 - (timestamp_millis/1000)%86400)

def get_status_changes_by_date(column_changes):
    status_change_by_date = {}

    for timestamp_millis in column_changes:
        d = timestamp_millis_to_epoch_day(int(timestamp_millis))
        if d not in status_change_by_date:
            status_change_by_date[d] = {}

        for change in column_changes[timestamp_millis]:
            if "columnTo" in change:
                column_to = change["columnTo"]
                if column_to not in status_change_by_date[d]:
                    status_change_by_date[d][column_to] = 0
                status_change_by_date[d][column_to] += 1

            if "columnFrom" in change:
                column_from = change["columnFrom"]
                if column_from not in status_change_by_date[d]:
                    status_change_by_date[d][column_from] = 0
                status_change_by_date[d][column_from] -= 1
    return status_change_by_date

def get_cumulative_flow_from_column_changes(cumulative_flow_input):
    column_changes = cumulative_flow_input['columnChanges']
    first_change_time = cumulative_flow_input['firstChangeTime']
    current_time = cumulative_flow_input['now']
    column_count = len(cumulative_flow_input['columns'])

    status_change_by_date = get_status_changes_by_date(column_changes)
                
    min_date = timestamp_millis_to_epoch_day(first_change_time)
    max_date = timestamp_millis_to_epoch_day(current_time)

    cumulative_flow = [0 for x in range(column_count)]
    cumulative_flow_by_date = {}
    
    curr_date = min_date
    while curr_date < max_date:
        for curr_column in range(column_count):
            if curr_date in status_change_by_date and curr_column in status_change_by_date[curr_date]:
                cumulative_flow[curr_column] += status_change_by_date[curr_date][curr_column]

        cumulative_flow_by_date[curr_date] = [x for x in cumulative_flow]
        curr_date += 86400

    return cumulative_flow_by_date

def get_cumulative_flow_csv(cumulative_flow_input, date_from, date_to):
    column_names = [x['name'].encode('ascii', 'ignore').decode('utf-8') for x in cumulative_flow_input['columns']]
    column_names.reverse()
    column_names = column_names + ["All"]
    cumulative_flow_dict = get_cumulative_flow_from_column_changes(cumulative_flow_input)

    csv_lines = []
    csv_lines.append(['date']+column_names)

    for d in sorted(cumulative_flow_dict):
        if d <= date_to and d >= date_from:
            date_str = get_day_from_timestamp(d)
            curr_values = cumulative_flow_dict[d]
            curr_values.reverse()
            line_sum = sum(curr_values)
            curr_values = curr_values + [line_sum]
            curr_line = [date_str] + curr_values

            csv_lines.append(curr_line)

    return csv_lines

def print_csv_file(csv_lines, output_file_name):
    with open(output_file_name, 'w') as output_file:
        wr = csv.writer(output_file, quoting=csv.QUOTE_ALL)
        for line in csv_lines:
            wr.writerow(line)

with open(INPUT_FILE) as json_file:
    cumulative_flow_input = json.load(json_file)
    date_from = get_timestamp_from_day(FROM_STR)
    date_to = get_timestamp_from_day(TO_STR)
    csv_lines = get_cumulative_flow_csv(cumulative_flow_input, date_from, date_to)
    print_csv_file(csv_lines, OUTPUT_FILE)