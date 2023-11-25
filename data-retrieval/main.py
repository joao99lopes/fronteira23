import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from data_retrieval_utils import *
from google_sheets_operations import *
from google_auth import check_credentials

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
            else:
                last_value = parse_sheet_values(values)

            # new_value = retrieve_data(ts=str(int(time.time())))       # USE IN PROD 
            new_value = retrieve_mock_data()                            # USE IN DEV
            if (new_value != last_value):
                print("######################\n##### NEW VALUES #####\n######################\n")
                if has_data==False:
                    write_header(sheet)
            new_data=data_dict_to_list(new_value, last_value)
            append_to_general_sheet(sheet, new_data, last_value)
            append_to_teams_sheet(sheet, new_data)
            
            last_value=new_value
            time.sleep(5)
            print("\n--------\n")
      
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()