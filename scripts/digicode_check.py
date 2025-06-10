#!/usr/bin/env python3
import yaml
from datetime import datetime
import sys
import os
import paho.mqtt.client as paho
import json

# Paramètres récupérés
code = sys.argv[1]
type_ = sys.argv[2]

# Fichier de log
log_file = "/config/digicode_logs.txt"

#MQTT
broker = "mymqtt.local" # IP ou alias du broner
port = 1883 # port du mqtt
userMqtt = 'myUser' # utilisateur mqtt
passwdMqtt = 'fuck1ngDifficultPassword!' # mot de passe mqtt
topicOk = 'rfid/ok'
topicNok = 'rfid/nok'

def on_publish(client, userdata, result):  # create function for callback
    pass

def sendMqtt(topic, data):
    client = paho.Client("digicodeCheck")  # create client object
    client.username_pw_set(userMqtt, passwdMqtt)
    client.on_publish = on_publish  # assign function to callback
    client.connect(broker, port)  # establish connection
    ret = client.publish(topic, data)  # publish

# Charger les utilisateurs
with open("/config/digicode_users.yaml", "r", encoding="utf-8") as f:
    users = yaml.safe_load(f)

# Rechercher l'utilisateur
matched_label = None
for key, user in users.items():
    if user.get("active")== True and str(user.get("code")) == code and user.get("type") == type_:
        matched_label = user.get("label")
        break

# Heure actuelle
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Journaliser
if matched_label:
    log_line = f"[{now}] ✅ Accès autorisé : {matched_label} ({type_})\n"
    dataOk = {
        "dateHeure": now,
        "type": type_,
        "user": matched_label
    }
    sendMqtt(topicOk, json.dumps(dataOk, indent=4))
else:
    log_line = f"[{now}] ❌ Accès refusé : code={code}, type={type_}\n"
    dataNok = {
        "dateHeure": now,
        "type": type_,
        "code": code
    }
    sendMqtt(topicNok, json.dumps(dataNok, indent=4))
    
print(log_line)
with open(log_file, "a", encoding="utf-8") as log:
    log.write(log_line)