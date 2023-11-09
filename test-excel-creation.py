import time
import requests
import json
from datetime import datetime

base_url = "http://24horastt.cronobandeira.com/r1.json?t="


def retrieve_data(ts:str) -> dict:
    col=[]
    fields=[]    
    res={}
    url = base_url + ts
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
                    if line[2] == '7':  # campo que contem o id da equipa
                        fields = line
                        
        for i in range(len(col)):
            plus=""
            if col[i]['Texte'] != '':
                plus = f"({col[i]['Texte']})"
            # print(f"{col[i]['Nom']}{plus} : {fields[i]}")
            res[f"{col[i]['Nom']}{plus}"] = fields[i]   
            
        print(str(datetime.now()).split(".")[0])
        # print(res)
        for i in res.keys():
            print(f"{i}: {res[i]}")
        return res

    else:
        print(f"Request failed with status code: {req.status_code}")

#->main
last_value:dict = {}
while True:
    timestamp = str(int(time.time()))
    new_value = retrieve_data(ts=timestamp)
    if (new_value != last_value):
        print("######################\n##### NEW VALUES #####\n######################\n")
        last_value=new_value
    time.sleep(5)
    print("\n--------\n")