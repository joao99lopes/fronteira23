# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
FRONTEIRA_SPREADSHEET_ID = '1ENpIhUNnZt3IJ96UB3uhrHk3WFKbf8Ys7duHRhiiod8'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
FRONTEIRA_DB_SHEET = 'DATA DB'
FRONTEIRA_TEAMS_SHEET = 'TEAMS INFO'
FRONTEIRA_DB_SHEET_ID = 0
FRONTEIRA_TEAMS_INFO_SHEET_ID = 1973410618

COLUMNS_TO_USE = ['DateTime', 'Position(Pos.)', 'Numero(No.)', 'Nom(Driver)', 'Groupe(Grp)', 'NbTour(Laps)', 'TpsCumule(Total time)', 'TpsTour(Lap time)', 'MeilleurTour(Best lap)', 'PenaliteNbTour(Laps penality)']

TEAM_NR_POS = 2
DRIVER_POS = 3

MY_TEAM = '7'
RIVALS = ['1', '2', '3', '4', '5', '6', '11', '12', '22', '31', '33', '34', '39', '42', '46', '48', '58', '60', '75']
OBSERVING_TEAMS = [MY_TEAM]+RIVALS

MOCK_DATA_FILES = ["mock-filipe-carvalho-request.json", "mock-mario-oliveira-request.json", "mock-nuno-pires-request.json", "mock-vitor-conceicao-request.json", ]
BASE_URL = "http://24horastt.cronobandeira.com/r1.json?t="

INFO_TEAM_TEMPLATE_HEADER=[
    ['TEAM', 'teamNr'],
    ['CAR', 'carname'],
    ['GROUP', 'groupname'],
    ['LAST POS', 'lastPos'],
    ['MEAN TIME', 'meantime'],
    ['FASTEST LAP', 'laptime', 'drivername'],
    ['DRIVER 1', 'drivername1', 'meantime', 'fastlaptime'],
    ['DRIVER 2', 'drivername2', 'meantime', 'fastlaptime'],
    ['DRIVER 3', 'drivername3', 'meantime', 'fastlaptime'],
    ['DRIVER 4', 'drivername4', 'meantime', 'fastlaptime'],
    ['DRIVER 5', 'drivername5', 'meantime', 'fastlaptime'],
]
INFO_TEAM_TABLE_HEADER = ['LAP ID', 'LAP', 'DAY TIME', 'POS', 'LAP TIME', 'TOTAL TIME', 'DRIVER']

TEAM_INFO_LAP_ID_INDEX = 0
TEAM_INFO_LAP_INDEX = 1
TEAM_INFO_DAY_TIME_INDEX = 2
TEAM_INFO_POS_INDEX = 3
TEAM_INFO_LAP_TIME_INDEX = 4
TEAM_INFO_TOTAL_TIME_INDEX = 5
TEAM_INFO_DRIVER_INDEX = 6

MY_TEAM_COLOURS = {
    'background' : {"red": 0.8, "green": 1.0, "blue": 0.8},
    'pilot_change' : {"red": 0.7, "green": 1.0, "blue": 0.7},
}

TEAM_1_COLOURS = {
    'background' : {"red": 0.7, "green": 0.8, "blue": 1.0},
    'pilot_change' : {"red": 0.8, "green": 0.8, "blue": 1.0},
}

TEAM_2_COLOURS = {
    'background' : {"red": 1.0, "green": 0.8, "blue": 0.8},
    'pilot_change' : {"red": 1.0, "green": 0.7, "blue": 0.7},
}

TEAM_3_COLOURS = {
    'background' : {"red": 1.0, "green": 1.0, "blue": 0.8},
    'pilot_change' : {"red": 1.0, "green": 1.0, "blue": 0.5},
}


COLOURS = [TEAM_1_COLOURS, TEAM_2_COLOURS, TEAM_3_COLOURS]

REQUEST_TIMEOUT = 10