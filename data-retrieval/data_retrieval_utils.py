import os
import json
import requests

from constants import *

def retrieve_mock_data():
    from random import randint
    mock_file = MOCK_DATA_FILES[randint(0, len(MOCK_DATA_FILES)-1)]
    print(f"MOCKING FROM: {mock_file}")
    data = {}
    with open(os.path.join(os.getcwd(), 'data-retrieval', 'mock-data', mock_file)) as fp:
        data = json.load(fp)
    res = parse_retrieved_data(data)
    for i in res.keys():
        print(f"{i}: {res[i]}")
    return res


def retrieve_data(ts:str) -> dict:
    res = {}
    url = BASE_URL + ts
    req = requests.get(url)

    if req.status_code == 200:
        response_text = req.text.lstrip('\ufeff')
        data = json.loads(response_text)
        res = parse_retrieved_data(data)
        for i in res.keys():
            print(f"{i}: {res[i]}")
        return res

    else:
        print(f"Request failed with status code: {req.status_code}")


def parse_retrieved_data(data:dict):
    res = {}
    col = []
    fields_per_team = {}
 
    for i in data.keys():
        if i == "Colonnes":
            col = data[i]
        if i =="Donnees":
            lines = data[i]
            for line in lines:
                if line[TEAM_NR_POS] in OBSERVING_TEAMS: 
                    fields_per_team[line[TEAM_NR_POS]] = line
    
    for team_id in list(fields_per_team.keys()):
        team_res = {}
        for i in range(len(col)):
            plus=""
            if col[i]['Texte'] != '':
                plus = f"({col[i]['Texte']})"
            if f"{col[i]['Nom']}{plus}" in COLUMNS_TO_USE:
                team_res[f"{col[i]['Nom']}{plus}"] = fields_per_team[team_id][i]
        res[team_id] = team_res

    return res
