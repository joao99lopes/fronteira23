from constants import *
from datetime import datetime


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
            for j in range(13, len(parse_sheet_values)):
                
                break
            # SACAR DADOS COLUNA EQUIPA
            # PUXAR ESSAS COLUNAS PARA BAIXO
            # ADICIONAR NOVOS VALORES (PINTAR SE TROCAR PILOTO) -> PINTAR SE TEMPO PILOTO FOR 3MINS MAIOR QUE MEDIA DO PILOTO
            # ATUALIZAR MELHOR VOLTA MEDIA TEMPO MEDIA PILOTO

    for team_data_line in data_to_add:
        tmp_team_data = {}
        lap_info = {}
        lap_info['day_time'] = team_data_line[0]
        lap_info['team_pos'] = team_data_line[1]
        lap_info['team_nr'] = team_data_line[2]
        lap_info['team_driver'] = team_data_line[3]
        lap_info['team_lap'] = team_data_line[5]
        lap_info['team_total_time'] = team_data_line[6]
        lap_info['team_lap_time'] = team_data_line[7]
        lap_info['team_best_lap'] = team_data_line[8]
        tmp_team_data[lap_info['team_lap']] = tmp_team_data
        data_per_team[lap_info['team_nr']] = tmp_team_data
    
    
    for i in range(len(OBSERVING_TEAMS)):
        if OBSERVING_TEAMS[i] in data_per_team.keys():
            team_data_to_add = data_per_team[OBSERVING_TEAMS[i]]
            sorted_laps_list = sorted(list(team_data_to_add.keys()), reverse=True)
            for j in range(len(sorted_laps_list)):
                requests.append({
                    "updateCells": {
                        "rows": [
                            {
                                "values": {"userEnteredValue": {"stringValue": sorted_laps_list[j]}}
                            }
                        ],
                        "start": {"sheetId": 0, "rowIndex": 13+j, "columnIndex": i*len(INFO_TEAM_TABLE_HEADER)},  # Start from the 2nd row
                        "fields": "userEnteredValue,userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
                    }
                })
    # Execute the batch update request
    result = sheet.batchUpdate(
        spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()

def data_dict_to_list(new_values:dict, old_values:dict):
    res_list = []
    date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in list(new_values.keys()):
        if key not in list (old_values.keys()) or new_values[key] != old_values[key]:
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