import re
import Credentials
import boto3
import os
import json
import uuid

strOutputDirectory = "../audiofiles/"

if(not(os.path.exists(strOutputDirectory))):
    os.mkdir(strOutputDirectory)

dicoGuids = {}

if(not(os.path.exists(strOutputDirectory + "guidconversions.json"))):
    json.dump(dicoGuids, open(strOutputDirectory + "guidconversions.json", "w", encoding="utf8"))
else:
    dicoGuids = json.load(open(strOutputDirectory + "guidconversions.json", "r", encoding="utf8"))

listLevels = json.load(open("../output/Levels.json", "r", encoding="utf8"))

setReadings = set()

for level in listLevels:
    for item in level:
        if(item["type"] == "vocab_kana"):
            setReadings.add(item["display"].replace("-", ""))
        else:
            for reading in item["readings"]:
                setReadings.add(reading.replace("-", ""))
            for reading in item["kun_readings"]:
                setReadings.add(reading.replace("-", ""))

for reading in list(setReadings):
    if("まわ" in reading):
        print(reading)

    if("." in reading):
        for part in reading.split("."):
            setReadings.add(part)
        setReadings.remove(reading)

print("Readings :", len(setReadings))

charCount = 0

for reading in setReadings:
    charCount += len(reading)

    if(not(reading in dicoGuids)):
        dicoGuids[reading] = str(uuid.uuid4())

print("CharCount", charCount)

json.dump(dicoGuids, open(strOutputDirectory + "guidconversions.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

polly_client = boto3.Session(
                aws_access_key_id=Credentials.AWS_ACCESS_KEY,                     
                aws_secret_access_key=Credentials.AWS_SECRET_ACCESS_KEY,
                region_name="eu-west-2").client("polly")

for reading in dicoGuids:
    filepath = strOutputDirectory + dicoGuids[reading] + ".mp3"

    if(not(os.path.exists(filepath))):
        print(reading, filepath)

        response = polly_client.synthesize_speech(
            Engine="standard",
            LanguageCode="ja-JP",
            VoiceId="Mizuki",
            OutputFormat="mp3", 
            TextType="text",
            Text = reading)

        file = open(filepath, "wb")
        file.write(response["AudioStream"].read())
        file.close()
