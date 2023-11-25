from constants import *
from datetime import datetime, timedelta


def parse_sheet_values(sheet_values:list) -> dict:
    res = {}
    header = sheet_values[0]
    for i in range(1,len(sheet_values)):
        if (sheet_values[i][TEAM_NR_POS]) in res:
            continue
        team_info = {}
        for j in range(1,len(sheet_values[i])):
            team_info[header[j]] = sheet_values[i][j]
        res[sheet_values[i][TEAM_NR_POS]] = team_info
    return res


def add_cell_format(stringValue, data_row, last_team_values) -> dict:
    cell_with_formatting = {"userEnteredValue": {"stringValue": stringValue}}
    if data_row[TEAM_NR_POS] == MY_TEAM:
        # Apply bold formatting to the cell
        if "userEnteredFormat" in list(cell_with_formatting.keys()):        
            cell_with_formatting["userEnteredFormat"]["textFormat"] = {"bold":True}
        else:
            cell_with_formatting["userEnteredFormat"] = {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.0}
            }
    if last_team_values != {} and data_row[DRIVER_POS] != last_team_values[COLUMNS_TO_USE[DRIVER_POS]]:
        # Apply bold formatting to the cell
        if "userEnteredFormat" in list(cell_with_formatting.keys()):        
            cell_with_formatting["userEnteredFormat"]["backgroundColor"] = {"red": 0.0, "green": 1.0, "blue": 0.0}
        else:
            cell_with_formatting["userEnteredFormat"] = {
                "backgroundColor": {"red": 0.0, "green": 1.0, "blue": 0.0}
            }
    return cell_with_formatting


def write_header(sheet):
    requests = []
    row_values=[]
    for col in COLUMNS_TO_USE:
        cell_with_formatting = {
            "userEnteredValue": {"stringValue": col},
            "userEnteredFormat": {"textFormat": {"bold": True}}
        }
        row_values.append(cell_with_formatting)

    requests.append({
        "updateCells": {
            "rows": [
                {
                    "values": row_values
                }
            ],
            "start": {"sheetId": 0, "rowIndex":0, "columnIndex": 0},
            "fields": "userEnteredValue,userEnteredFormat.textFormat.bold"
        }
    })

    # Execute the batch update request
    result = sheet.batchUpdate(
        spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()


def append_to_general_sheet(sheet, data_to_add, last_values):
    requests = []

    # Calculate the number of new rows to insert based on the size of data_to_add
    num_new_rows = len(data_to_add)

    # Insert empty rows at the top (before the header)
    requests.append({
        "insertDimension": {
            "range": {
                "sheetId": 0,
                "dimension": "ROWS",
                "startIndex": 1,  # Insert after the header (1st row)
                "endIndex": num_new_rows + 1  # Number of rows to insert (header + new rows)
            }
        }
    })

    # Iterate through data_to_add and update the newly inserted rows
    for i in range(num_new_rows):
        data_row = data_to_add[i]
        last_team_values = {}
        if data_row[TEAM_NR_POS] in list(last_values.keys()):
            last_team_values = last_values[data_row[TEAM_NR_POS]]
        row_values = []

        for j in range(len(data_row)):
            cell = data_row[j]
            cell_with_formatting = add_cell_format(cell, data_row, last_team_values)

            row_values.append(cell_with_formatting)
            requests.append({
                "updateCells": {
                    "rows": [
                        {
                            "values": row_values
                        }
                    ],
                    "start": {"sheetId": 0, "rowIndex": 1+i, "columnIndex": 0},  # Start from the 2nd row
                    "fields": "userEnteredValue,userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
                }
        })

    # Execute the batch update request
    result = sheet.batchUpdate(
        spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()


def append_to_teams_sheet(sheet, data_to_add):
    requests = []

    current_sheet_values_request = sheet.values().get(spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
                                range=FRONTEIRA_TEAMS_SHEET).execute()
    current_sheet_values = current_sheet_values_request.get('values', [])

    if not current_sheet_values:
        print('No data found. TEAMS INFO is empty.')
        print_teams_info_header(sheet)
    
    data_per_team = {}
    
    if len(current_sheet_values) > 13:
        for i in range(len(OBSERVING_TEAMS)):
            team_laps = {}
            for j in range(13, len(current_sheet_values)):
                if i*len(INFO_TEAM_TABLE_HEADER) in range(len(current_sheet_values[j])):
                    start_index = i*len(INFO_TEAM_TABLE_HEADER)
                    if current_sheet_values[j][start_index] != '':
                        lap_info = current_sheet_values[j][start_index : start_index + len(INFO_TEAM_TABLE_HEADER)]
                        team_laps[lap_info[0]] = lap_info
            if team_laps != {}:
                data_per_team[OBSERVING_TEAMS[i]] = team_laps

    for team_data_line in data_to_add:
        lap_info = {}
        lap_info['LAP'] = team_data_line[5]
        lap_info['DAY TIME'] = team_data_line[0]
        lap_info['POS'] = team_data_line[1]
        lap_info['LAP TIME'] = team_data_line[7]
        lap_info['TOTAL TIME'] = team_data_line[6]
        lap_info['DRIVER'] = team_data_line[3]
        lap_info['team_nr'] = team_data_line[2]
        lap_info['team_best_lap'] = team_data_line[8]
        if lap_info["team_nr"] not in data_per_team.keys():
            data_per_team[lap_info['team_nr']] = {lap_info['LAP']:list(lap_info.values())}
        else:
            data_per_team[lap_info['team_nr']][lap_info['LAP']] = list(lap_info.values())
            
    for i in range(len(OBSERVING_TEAMS)):
        if OBSERVING_TEAMS[i] in data_per_team.keys():
            team_data_to_add = data_per_team[OBSERVING_TEAMS[i]]
            sorted_laps_list = sorted(team_data_to_add.keys(), key=lambda lap_nr: int(lap_nr), reverse=True)
            
            last_lap_info = team_data_to_add[sorted_laps_list[0]]

            # write header
            requests.append(simple_data_cell(OBSERVING_TEAMS[i], FRONTEIRA_TEAMS_INFO_SHEET_ID, 0, 1+i*len(INFO_TEAM_TABLE_HEADER)))
            requests.append(simple_data_cell(last_lap_info[TEAM_INFO_LAP_INDEX], FRONTEIRA_TEAMS_INFO_SHEET_ID, 3, 1+i*len(INFO_TEAM_TABLE_HEADER)))
            requests.append(simple_data_cell(mean_time_per_lap(last_lap_info[TEAM_INFO_TOTAL_TIME_INDEX], int(last_lap_info[TEAM_INFO_LAP_INDEX])), FRONTEIRA_TEAMS_INFO_SHEET_ID, 4, 1+i*len(INFO_TEAM_TABLE_HEADER)))
            fastest_lap = team_fastest_lap(team_data_to_add)
            requests.append(simple_data_cell(fastest_lap[TEAM_INFO_LAP_TIME_INDEX], FRONTEIRA_TEAMS_INFO_SHEET_ID, 5, 1+i*len(INFO_TEAM_TABLE_HEADER)))
            requests.append(simple_data_cell(fastest_lap[TEAM_INFO_DRIVER_INDEX], FRONTEIRA_TEAMS_INFO_SHEET_ID, 5, 2+i*len(INFO_TEAM_TABLE_HEADER)))

            for j in range(len(sorted_laps_list)):
                lap_info = team_data_to_add[sorted_laps_list[j]]
                for k in range(len(INFO_TEAM_TABLE_HEADER)):
                    requests.append(simple_data_cell(lap_info[k], FRONTEIRA_TEAMS_INFO_SHEET_ID, 13+j, k+i*len(INFO_TEAM_TABLE_HEADER)))
    if len(requests) > 0:
        # Execute the batch update request
        result = sheet.batchUpdate(
            spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
            body={'requests': requests}
        ).execute()
        

def data_dict_to_list(new_values:dict, old_values:dict):
    res_list = []
    date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in list(new_values.keys()):
        # if key not in list (old_values.keys()) or new_values[key] != old_values[key]:
            res_list.append([date_and_time]+list({col:new_values[key][col] for col in new_values[key]}.values()))
    return res_list
    

def print_teams_info_header(sheet):
    empty_line = [''] * len(INFO_TEAM_TABLE_HEADER) * len(OBSERVING_TEAMS)
    requests = [empty_line[:] for _ in range(len(INFO_TEAM_TEMPLATE_HEADER))]
    
    for i in range(len(OBSERVING_TEAMS)):
        for j in range(len(INFO_TEAM_TEMPLATE_HEADER)):
            for k in range(len(INFO_TEAM_TEMPLATE_HEADER[j])):
                requests[j][k + i * len(INFO_TEAM_TABLE_HEADER)] = INFO_TEAM_TEMPLATE_HEADER[j][k]
    requests.append(empty_line)
    requests.append(INFO_TEAM_TABLE_HEADER * len(OBSERVING_TEAMS))

    # Execute the batch update request
    sheet.values().append(
        spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
        range=FRONTEIRA_TEAMS_SHEET,
        body={'values': requests},
        valueInputOption='RAW'
    ).execute()
    
    
def simple_data_cell(value, sheet_id, row_index, col_index) -> dict:
    return {
        "updateCells": {
            "rows": [
                {
                    "values": {"userEnteredValue": {"stringValue": value}}
                }
            ],
            "start": {"sheetId": sheet_id, "rowIndex": row_index, "columnIndex": col_index},
            "fields": "userEnteredValue,userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
        }
    }


def mean_time_per_lap(total_time_str, num_laps) -> str:
    total_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(total_time_str.split('.')[0].split(':'))))
    mean_total_seconds, mean_secs = divmod(total_seconds / num_laps, 60)
    mean_hours, mean_mins = divmod(mean_total_seconds, 60)
    return f"{int(mean_hours):02d}:{int(mean_mins):02d}:{int(mean_secs):02d}"

def team_fastest_lap(team_laps) -> list:
    laps = list(team_laps.values())
    sorted_laps_per_time = sorted(laps, key=lambda lap: lap[TEAM_INFO_LAP_TIME_INDEX])
    return sorted_laps_per_time[0]
    