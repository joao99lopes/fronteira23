from __future__ import print_function

import os.path
import time
import requests
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
FRONTEIRA_SPREADSHEET_ID = '1ENpIhUNnZt3IJ96UB3uhrHk3WFKbf8Ys7duHRhiiod8'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
FRONTEIRA_DB_SHEET = 'DATA DB'

TEAM_NR_POS = 2
MY_TEAM = '7'
TEAMS_OBSERVER_LIST = ['7', '10']


BASE_URL = "http://24horastt.cronobandeira.com/r1.json?t="
COLUMNS_TO_USE = ['DateTime', 'Position(Pos.)', 'Numero(No.)', 'Nom(Driver)', 'Groupe(Grp)', 'NbTour(Laps)', 'TpsCumule(Total time)', 'TpsTour(Lap time)', 'MeilleurTour(Best lap)', 'PenaliteNbTour(Laps penality)']

def retrieve_data(ts:str) -> dict:
    col = []
    fields_per_team = {}
    res = {}
    url = BASE_URL + ts
    req = requests.get(url)

    if req.status_code == 200:
        response_text = req.text.lstrip('\ufeff')
        data = json.loads(response_text)
        for i in data.keys():
            if i == "Colonnes":
                col = data[i]
            if i =="Donnees":
                lines = data[i]
                for line in lines:
                    if line[TEAM_NR_POS] in TEAMS_OBSERVER_LIST: 
                        fields_per_team[line[TEAM_NR_POS]] = line
        for team_id in list(fields_per_team.keys()):
            team_res = {}
            for i in range(len(col)):
                plus=""
                if col[i]['Texte'] != '':
                    plus = f"({col[i]['Texte']})"
                team_res[f"{col[i]['Nom']}{plus}"] = fields_per_team[team_id][i]
            res[team_id] = team_res
                
        for i in res.keys():
            print(f"{i}: {res[i]}")
        return res

    else:
        print(f"Request failed with status code: {req.status_code}")


def append_to_sheet(sheet, data_to_add):
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
        row_values = []

        for cell in data_row:
            cell_with_formatting = {
                "userEnteredValue": {"stringValue": cell}
            }
            if data_row[2] == MY_TEAM:
                # Apply bold formatting to the cell
                cell_with_formatting["userEnteredFormat"] = {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.0}

                }

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



def check_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def parse_received_data(new_values:dict):
    res_list = []
    date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key in list(new_values.keys()):
        res_list.append([date_and_time]+list({col:new_values[key][col] for col in COLUMNS_TO_USE if col in new_values[key]}.values()))
    return res_list
    

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = check_credentials()

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        has_data = True
        last_value = {}
        
        while True:
            #get current state of DB
            result = sheet.values().get(spreadsheetId=FRONTEIRA_SPREADSHEET_ID,
                                        range=FRONTEIRA_DB_SHEET).execute()
            values = result.get('values', [])

            if not values:
                print('No data found. DB is empty.')
                has_data=False

            timestamp = str(int(time.time()))
            new_value = retrieve_data(ts=timestamp)
            if (new_value != last_value):
                print("######################\n##### NEW VALUES #####\n######################\n")
                if has_data==False:
                    write_header(sheet)
            # new_data=[str(datetime.now())]+list({k:new_value[k] for k in COLUMNS_TO_USE if k in new_value}.values())
            new_data=parse_received_data(new_value)
            append_to_sheet(sheet, new_data)
            
            last_value=new_value
            time.sleep(5)
            print("\n--------\n")
      
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()