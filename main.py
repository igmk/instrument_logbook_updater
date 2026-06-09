from flask import Flask, render_template, request, url_for, flash, redirect
import yaml
from xmlrpc import client
import urllib.parse
import requests
import datetime

app = Flask(__name__)

with open('config.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

def addWikiEntry(wikiURL, wikiApiToken,wikiPage,eventType,dt,notes,operator):
    # get old Page
    response = requests.post(
        wikiURL+"/core.getPage",
        json={
            "page": wikiPage,
            },
        headers={'Content-type': 'application/json', "Authorization": f'Bearer {wikiApiToken}'}
    )
    content = response.json()["result"]
    # add new Content
    dateStr1 = dt.strftime("%d.%m.%Y")
    dateStr2 = dt.strftime("%Y/%m/%d %H:%M")
    newContent = f"==== {dateStr1} ====\n --- //{operator} {dateStr2}//\n  * {eventType}: {notes}\n"
    newContent = newContent+content
    #upload to wiki
    response = requests.post(
        wikiURL+"/core.savePage",
        json={
            "page": wikiPage,
            "text": newContent,
            "summary": "api update",
            "isminor": "true"
            },
        headers={'Content-type': 'application/json', "Authorization": f'Bearer {wikiApiToken}'}
    )



def addCloudnetEntry(cloudnetApiToken,instrumentUuid,eventType,detail,result,date,endDate,notes):
    url = 'https://cloudnet.fmi.fi/api/instrument-logs'
    headers = {'X-Auth-Token': cloudnetApiToken}
    myobj = {
        "instrumentUuid":instrumentUuid,
        "eventType":eventType,
        "detail":detail,
        "result":result,
        "date":date,
        "endDate":endDate,
        "notes":notes,
    }
    x = requests.post(url, json = myobj,headers=headers)
    print(x.text)


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        if request.form["code"] == config["accessCode"]:
            # find instrument
            for entry in config["instruments"]:
                if entry["name"] == request.form["instrument"]:
                    # found instrument
                    print(request.form)
                    if "wikiPage" in entry:
                        print("update wiki")
                        addWikiEntry(
                            config["wikiURL"],
                            config["wikiApiToken"],
                            entry["wikiPage"],
                            request.form["event-type"],
                            datetime.datetime.strptime(request.form["date"]+"T"+request.form["time"],"%Y-%m-%dT%H:%M"),
                            request.form["event-notes"],
                            request.form["operator"]


                        )
                    if "cloudnetUUID" in entry:
                        print("update actris")
                        addCloudnetEntry(
                            config["cloudnetApiKey"],entry["cloudnetUUID"],
                            request.form["event-type"],
                            None,
                            None,
                            request.form["date"]+"T"+request.form["time"],
                            request.form["date"]+"T"+request.form["time"],
                            request.form["event-notes"]+" - performed by: "+request.form["operator"]
                        )
                else:
                    continue
        else:
            print("wrong code")

    return render_template('index.html', team=config["team"], instruments=[entry["name"] for entry in config["instruments"]])
