import os
import json
import requests
import importlib
from datetime import datetime
import constants

def retrieve_mock_data():
    from random import randint
    mock_file = constants.MOCK_DATA_FILES[randint(0, len(constants.MOCK_DATA_FILES)-1)]
    print(f"MOCKING FROM: {mock_file}")
    data = {}
    with open(os.path.join(os.getcwd(), 'data-retrieval', 'mock-data', mock_file)) as fp:
        data = json.load(fp)
    res = parse_retrieved_data(data)
    print(datetime.now())
    for i in res.keys():
        print(f"{i}: {res[i]}")
    return res


def retrieve_data(ts:str) -> dict:
    res = {}
    url = constants.BASE_URL + ts
    req = requests.get(url)

    if req.status_code == 200:
        response_text = req.text.lstrip('\ufeff')
        data = json.loads(response_text)
        res = parse_retrieved_data(data)
        print(datetime.now())
        return res

    else:
        print(datetime.now())
        print(f"Request failed with status code: {req.status_code}")


def parse_retrieved_data(data:dict):
    res = {}
    col = []
    fields_per_team = {}
    
    importlib.reload(constants)
    for i in data.keys():
        if i == "Colonnes":
            col = data[i]
        if i =="Donnees":
            lines = data[i]
            for line in lines:
                line = line[1:]
                team_nr = line[constants.TEAM_NR_POS]
                if "}" in team_nr:
                    team_nr = line[constants.TEAM_NR_POS].split("}")[1]
                if team_nr in constants.OBSERVING_TEAMS: 
                    line[constants.TEAM_NR_POS] = team_nr
                    fields_per_team[line[constants.TEAM_NR_POS]] = line
    col = col[1:]
#['DateTime', 'Position(Pos.)', 'Numero(No.)', 'Nom(Driver)', 'Groupe(Grp)', 'NbTour(Laps)', 'TpsCumule(Total time)', 'TpsTour(Lap time)', 'MeilleurTour(Best lap)', 'PenaliteNbTour(Laps penality)']
    
    for team_id in list(fields_per_team.keys()):
        team_res = {}
        for i in range(len(col)):
            if f"{col[i]['Nom']}" in constants.COLUMNS_TO_USE:
                new_value = fields_per_team[team_id][i]
                if "}" in new_value:
                    new_value = new_value.split("}")[1]
                team_res[f"{col[i]['Nom']}"] = new_value
        res[team_id] = team_res

    return res
