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


def add_cell_format(cell, data_row, last_team_values) -> dict:
    cell_with_formatting = {"userEnteredValue": {"stringValue": cell}}
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
    cols = ['DAY TIME', 'POS', 'LAP', 'LAP TIME', 'TOTAL TIME', 'DRIVER']
    requests = []
    
    for i in range(len(data_to_add)):
        data_row = data_to_add[i]
        
        # SACAR DADOS COLUNA EQUIPA
        # PUXAR ESSAS COLUNAS PARA BAIXO
        # ADICIONAR NOVOS VALORES (PINTAR SE TROCAR PILOTO) -> PINTAR SE TEMPO PILOTO FOR 3MINS MAIOR QUE MEDIA DO PILOTO
        # ATUALIZAR MELHOR VOLTA MEDIA TEMPO MEDIA PILOTO
        
        
        # last_team_values = {}
        # if data_row[TEAM_NR_POS] in list(last_values.keys()):
        #     last_team_values = last_values[data_row[TEAM_NR_POS]]
        # row_values = []

        # for j in range(len(data_row)):
        #     cell = data_row[j]
        #     cell_with_formatting = add_cell_format(cell, data_row, last_team_values)

        #     row_values.append(cell_with_formatting)
        #     requests.append({
        #         "updateCells": {
        #             "rows": [
        #                 {
        #                     "values": row_values
        #                 }
        #             ],
        #             "start": {"sheetId": 0, "rowIndex": 1+i, "columnIndex": 0},  # Start from the 2nd row
        #             "fields": "userEnteredValue,userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
        #         }
        # })
    
    return


def data_dict_to_list(new_values:dict, old_values:dict):
    res_list = []
    date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in list(new_values.keys()):
        if key not in list (old_values.keys()) or new_values[key] != old_values[key]:
            res_list.append([date_and_time]+list({col:new_values[key][col] for col in new_values[key]}.values()))
    return res_list
    
