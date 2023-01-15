import re
import Credentials
import boto3
import os
import json
import uuid
import KanaReadings

strOutputDirectory = "../audiofiles/"

if(not(os.path.exists(strOutputDirectory))):
    os.mkdir(strOutputDirectory)

dicoGuids = {}

if(not(os.path.exists(strOutputDirectory + "guidconversions.json"))):
    json.dump(dicoGuids, open(strOutputDirectory + "guidconversions.json", "w", encoding="utf8"))
else:
    dicoGuids = json.load(open(strOutputDirectory + "guidconversions.json", "r", encoding="utf8"))

dicoLevels = json.load(open("../output/Levels.json", "r", encoding="utf8"))

setReadings = set()

for reading in KanaReadings.listKanaReadings:
    setReadings.add(reading)

for level in dicoLevels:
    for item in dicoLevels[level]:
        if(item["type"] == "vocab_kana"):
            setReadings.add(item["display"].replace("-", ""))
        else:
            for reading in item["readings"]:
                setReadings.add(reading.replace("-", ""))
            for reading in item["kun_readings"]:
                setReadings.add(reading.replace("-", ""))

for reading in list(setReadings):
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

dicoReplaceReadings = {
    "は" : "は。",
    "へ" : "<speak><phoneme alphabet='ipa' ph='he'>へ</phoneme></speak>",
    "し" : "<speak><phoneme alphabet='ipa' ph='ɕi'>し</phoneme></speak>"
}

for reading in dicoGuids:
    filepath = strOutputDirectory + dicoGuids[reading] + ".mp3"

    if(not(os.path.exists(filepath))):
        print(reading, filepath)

        if(reading in dicoReplaceReadings):
            reading = dicoReplaceReadings[reading]

        texttype = "text"

        if(reading[0] == "<"):
            texttype = "ssml"

        response = polly_client.synthesize_speech(
            Engine="standard",
            LanguageCode="ja-JP",
            VoiceId="Mizuki",
            OutputFormat="mp3", 
            TextType=texttype,
            Text = reading)

        file = open(filepath, "wb")
        file.write(response["AudioStream"].read())
        file.close()


