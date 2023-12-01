import constants
import importlib
from datetime import datetime, timedelta


def parse_sheet_values(sheet_values:list) -> dict:
    res = {}
    header = sheet_values[0]
    for i in range(1,len(sheet_values)):
        if (sheet_values[i][ constants.TEAM_NR_POS]) in res:
            continue
        team_info = {}
        for j in range(1,len(sheet_values[i])):
            team_info[header[j]] = sheet_values[i][j]
        res[sheet_values[i][constants.TEAM_NR_POS]] = team_info
    return res


def add_cell_format(stringValue, data_row, last_team_values) -> dict:
    cell_with_formatting = {"userEnteredValue": {"stringValue": stringValue}}
    if data_row[constants.TEAM_NR_POS] == constants.MY_TEAM:
        # Apply bold formatting to the cell
        if "userEnteredFormat" in list(cell_with_formatting.keys()):        
            cell_with_formatting["userEnteredFormat"]["textFormat"] = {"bold":True}
        else:
            cell_with_formatting["userEnteredFormat"] = {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.0}
            }
    if last_team_values != {} and data_row[constants.DRIVER_POS] != last_team_values[constants.COLUMNS_TO_USE[constants.DRIVER_POS]]:
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
    for col in constants.COLUMNS_TO_USE:
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
        spreadsheetId=constants.FRONTEIRA_SPREADSHEET_ID,
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
        if data_row[constants.TEAM_NR_POS] in list(last_values.keys()):
            last_team_values = last_values[data_row[constants.TEAM_NR_POS]]
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
        spreadsheetId=constants.FRONTEIRA_SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()


def append_to_teams_sheet(sheet, data_to_add):
    importlib.reload(constants)

    requests = []

    current_sheet_values_request = sheet.values().get(spreadsheetId=constants.FRONTEIRA_SPREADSHEET_ID,
                                range=constants.FRONTEIRA_TEAMS_SHEET).execute()
    current_sheet_values = current_sheet_values_request.get('values', [])

    if not current_sheet_values:
        print('No data found. TEAMS INFO is empty.')
        print_teams_info_header(sheet)
    
    data_per_team = {}
    
    if len(current_sheet_values) > 13:
        for i in range(len(constants.OBSERVING_TEAMS)):
            team_laps = {}
            for j in range(13, len(current_sheet_values)):
                if i*len(constants.INFO_TEAM_TABLE_HEADER) in range(len(current_sheet_values[j])):
                    start_index = i*len(constants.INFO_TEAM_TABLE_HEADER)
                    if current_sheet_values[j][start_index] != '':
                        lap_info = current_sheet_values[j][start_index : start_index + len(constants.INFO_TEAM_TABLE_HEADER)]
                        team_laps[lap_info[0]] = lap_info
            if team_laps != {}:
                data_per_team[constants.OBSERVING_TEAMS[i]] = team_laps

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
            data_per_team[lap_info['team_nr']] = {'0':['0']+list(lap_info.values())}
        else:
            lap_id = str(len(data_per_team[lap_info['team_nr']]))
            data_per_team[lap_info['team_nr']][lap_id] = [lap_id]+list(lap_info.values())
            
    for i in range(len(constants.OBSERVING_TEAMS)):
        if constants.OBSERVING_TEAMS[i] in data_per_team.keys():
            team_data_to_add = data_per_team[constants.OBSERVING_TEAMS[i]]
            sorted_laps_list = sorted(team_data_to_add.keys(), key=lambda lap_nr: int(lap_nr), reverse=True)
            
            last_lap_info = team_data_to_add[sorted_laps_list[0]]

            # write header
            requests.append(simple_data_cell(constants.OBSERVING_TEAMS[i], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 0, 1+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
            requests.append(simple_data_cell(last_lap_info[constants.TEAM_INFO_POS_INDEX], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 3, 1+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
            requests.append(simple_data_cell(mean_time_per_lap(last_lap_info[constants.TEAM_INFO_TOTAL_TIME_INDEX], len(team_data_to_add)), constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 4, 1+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
            fastest_lap = team_fastest_lap(list(team_data_to_add.values()))
            requests.append(simple_data_cell(fastest_lap[constants.TEAM_INFO_LAP_TIME_INDEX], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 5, 1+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
            requests.append(simple_data_cell(fastest_lap[constants.TEAM_INFO_DRIVER_INDEX], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 5, 2+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
            driver_times = mean_time_per_driver(list(team_data_to_add.values()))
            for j in range(len(driver_times)):
                requests.append(simple_data_cell(driver_times[j]['driver'], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 6+j, 1+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
                requests.append(simple_data_cell(driver_times[j]['mean time'], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 6+j, 2+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
                requests.append(simple_data_cell(driver_times[j]['fastest lap'], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 6+j, 3+i*len(constants.INFO_TEAM_TABLE_HEADER), i, 'background'))
                
                
            for j in range(len(sorted_laps_list)):
                lap_info = team_data_to_add[sorted_laps_list[j]]
                color_style = 'background'
                if j<len(sorted_laps_list)-1 and lap_info[constants.TEAM_INFO_DRIVER_INDEX] != team_data_to_add[sorted_laps_list[j+1]][constants.TEAM_INFO_DRIVER_INDEX]:
                    color_style = 'pilot_change'
                for k in range(len(constants.INFO_TEAM_TABLE_HEADER)):
                    requests.append(simple_data_cell(lap_info[k], constants.FRONTEIRA_TEAMS_INFO_SHEET_ID, 13+j, k+i*len(constants.INFO_TEAM_TABLE_HEADER), i, color_style))
                    
    if len(requests) > 0:
        # Execute the batch update request
        result = sheet.batchUpdate(
            spreadsheetId=constants.FRONTEIRA_SPREADSHEET_ID,
            body={'requests': requests}
        ).execute()
        

def data_dict_to_list(new_values:dict, old_values:dict):
    res_list = []
    date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in list(new_values.keys()):
        if (key not in list(old_values.keys())) or (new_values[key] != old_values[key]):
            res_list.append([date_and_time]+list({col:new_values[key][col] for col in new_values[key]}.values()))
    return res_list
    

def print_teams_info_header(sheet):
    empty_line = [''] * len(constants.INFO_TEAM_TABLE_HEADER) * len(constants.OBSERVING_TEAMS)
    requests = [empty_line[:] for _ in range(len(constants.INFO_TEAM_TEMPLATE_HEADER))]
    
    for i in range(len(constants.OBSERVING_TEAMS)):
        for j in range(len(constants.INFO_TEAM_TEMPLATE_HEADER)):
            for k in range(len(constants.INFO_TEAM_TEMPLATE_HEADER[j])):
                field = constants.INFO_TEAM_TEMPLATE_HEADER[j][k]
                if field == "teamNr":
                    field = constants.OBSERVING_TEAMS[i]
                requests[j][k + i * len(constants.INFO_TEAM_TABLE_HEADER)] = field
    requests.append(empty_line)
    requests.append(constants.INFO_TEAM_TABLE_HEADER * len(constants.OBSERVING_TEAMS))

    # Execute the batch update request
    sheet.values().append(
        spreadsheetId=constants.FRONTEIRA_SPREADSHEET_ID,
        range=constants.FRONTEIRA_TEAMS_SHEET,
        body={'values': requests},
        valueInputOption='RAW'
    ).execute()
    
    
def simple_data_cell(value, sheet_id, row_index, col_index, team_index, colour_style) -> dict:
    team_colour = constants.COLOURS[team_index%len(constants.COLOURS)][colour_style]
    if team_index == 0:
        team_colour = constants.MY_TEAM_COLOURS[colour_style]
    return {
        "updateCells": {
            "rows": [
                {
                    "values": {
                        "userEnteredValue": {"stringValue": value},
                        "userEnteredFormat": {"backgroundColor": team_colour}
                        }
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
    sorted_laps_per_time = sorted(team_laps, key=lambda lap: lap[constants.TEAM_INFO_LAP_TIME_INDEX])
    return sorted_laps_per_time[0]


def mean_time_per_driver(team_laps) -> list:
    res = []
    driver_times = {}
    driver_times_mean = {}
    for lap in team_laps:
        if "Pit " not in lap[constants.TEAM_INFO_LAP_TIME_INDEX]:
            if lap[constants.TEAM_INFO_DRIVER_INDEX] not in list(driver_times.keys()):
                # driver_times[lap[TEAM_INFO_DRIVER_INDEX]] = [lap[TEAM_INFO_LAP_TIME_INDEX]]
                driver_times[lap[constants.TEAM_INFO_DRIVER_INDEX]] = {lap[constants.TEAM_INFO_LAP_INDEX]:lap[constants.TEAM_INFO_LAP_TIME_INDEX]}  # ignore
            else:
                # driver_times[lap[TEAM_INFO_DRIVER_INDEX]].append(lap[TEAM_INFO_LAP_TIME_INDEX])
                driver_times[lap[constants.TEAM_INFO_DRIVER_INDEX]][lap[constants.TEAM_INFO_LAP_INDEX]] = lap[constants.TEAM_INFO_LAP_TIME_INDEX]

    for driver in list(driver_times.keys()):
        last_lap = None
        filtered_laps = []
        for lap_nr in sorted(list(driver_times[driver].keys())):
            if not (last_lap == None or int(last_lap) < int(lap_nr)-1):
                filtered_laps.append(driver_times[driver][lap_nr])
            last_lap = lap_nr
        driver_times_mean[driver] = filtered_laps

    for driver in list(driver_times.keys()):
        total_time_sec = 0
        for lap_time in driver_times_mean[driver]:
            lap_time_str = lap_time.split(".")[0].split(":")
            total_time_sec += int(lap_time_str[0])*60 + int(lap_time_str[1])
        
        mean_time = "N/A"
        fast_time = "N/A"
        if len(driver_times_mean[driver]) > 0:
            mean_time_sec = total_time_sec / len(driver_times_mean[driver])
            mean_time = f"{int(mean_time_sec//60):02d}:{int(mean_time_sec%60):02d}"
        if len(driver_times[driver]) > 0:
            fast_time = sorted(list(driver_times[driver].values()), key=lambda lap_time: lap_time)[0]
        
        res.append({
            'driver':driver,
            'mean time':mean_time,
            'fastest lap':fast_time
        })
    return res