from distutils.log import debug
from re import S
from lxml import etree
import os
import functools
import jaconv
import copy
import json
import hashlib

if(not(os.path.exists("../output/"))):
    os.mkdir("../output")

dicoKanjis = {}

kanjidic = etree.parse("../sources/kanjidic/kanjidic2.xml") 
kanjidicroot = kanjidic.getroot()

for child in kanjidicroot.getchildren():

    if(child.tag == "character"):

        dicoKanji = {
            "literal" : "",
            "freq" : -1,
            "freq_vocab" : -1,
            "freq_vocab_entry" : {},
            "freq_average" : -1,
            "readings_on" : [],
            "readings_kun" : [],
            "meanings" : [],
            "entries_ordered" : []
        }

        for child2 in child.getchildren():
            if(child2.tag == "literal"):
                dicoKanji["literal"] = child2.text

            elif(child2.tag == "misc"):
                for child3 in child2.getchildren():
                    if(child3.tag == "freq"):
                        dicoKanji["freq"] = int(child3.text)

            elif(child2.tag == "reading_meaning"):
                for child3 in child2.getchildren():
                    if(child3.tag == "rmgroup"):
                        for child4 in child3.getchildren():
                            if(child4.tag == "reading" and child4.get("r_type") == "ja_on"):
                                dicoKanji["readings_on"].append(child4.text)
                            elif(child4.tag == "reading" and child4.get("r_type") == "ja_kun"):
                                dicoKanji["readings_kun"].append(child4.text)
                            elif(child4.tag == "meaning" and (child4.get("m_lang") == "en" or child4.get("m_lang") == None)):
                                dicoKanji["meanings"].append(child4.text)

        if(dicoKanji["literal"] != ""):
            dicoKanjis[dicoKanji["literal"]] = dicoKanji

listKanjis = []

for kanji in dicoKanjis:
    listKanjis.append(dicoKanjis[kanji])

listKanjis.sort(key = lambda x : (10000000 if x["freq"] == -1 else x["freq"]))

dicoFrequencies = {}

with open("../sources/frequency-leeds/44492-japanese-words-latin-lines-removed.txt", "r", encoding="utf8") as frequencyleeds:
    iCounter = 0

    for line in frequencyleeds.readlines():

        line = line.replace("\r", "").replace("\n", "")
        if(not(line in dicoFrequencies)):
            dicoFrequencies[line] = {"freq" : iCounter, "occ" : 1}
        else:
            dicoFrequencies[line]["freq"] = (dicoFrequencies[line]["freq"] * dicoFrequencies[line]["occ"] + iCounter) / (dicoFrequencies[line]["occ"] + 1)
            dicoFrequencies[line]["occ"] += 1

        iCounter += 1
        

with open("../sources/frequency-wiki/Freq1-10000.txt", "r", encoding="utf8") as frequencywiki:
    iCounter = 0

    for line in frequencywiki.readlines():
        line = line.replace("\r", "").replace("\n", "")

        if(len(line) >= 1 and line[0] == "#"):
            line = line[line.index("[[") + 2:line.index("]]")]

            if(not(line in dicoFrequencies)):
                dicoFrequencies[line] = {"freq" : iCounter, "occ" : 1}
            else:
                dicoFrequencies[line]["freq"] = (dicoFrequencies[line]["freq"] * dicoFrequencies[line]["occ"] + iCounter) / (dicoFrequencies[line]["occ"] + 1)
                dicoFrequencies[line]["occ"] += 1

            iCounter += 1

with open("../sources/frequency-wiki/Freq10001-20000.txt", "r", encoding="utf8") as frequencywiki:
    iCounter = 10000

    for line in frequencywiki.readlines():
        line = line.replace("\r", "").replace("\n", "")

        if(len(line) >= 1 and line[0] == "#"):
            line = line[line.index("{{l/ja|") + 7:line.index("}}")]

            if(not(line in dicoFrequencies)):
                dicoFrequencies[line] = {"freq" : iCounter, "occ" : 1}
            else:
                dicoFrequencies[line]["freq"] = (dicoFrequencies[line]["freq"] * dicoFrequencies[line]["occ"] + iCounter) / (dicoFrequencies[line]["occ"] + 1)
                dicoFrequencies[line]["occ"] += 1

            iCounter += 1

jmdict = etree.parse("../sources/jmdict/JMdict.xml") 
jmdictroot = jmdict.getroot()

listEntries = []

for child in jmdictroot.getchildren():
    
    if(child.tag == "entry"):

        dicoEntry = {
            "reading" : "",
            "kana_only" : False,
            "altKanjiReadings" : [],
            "altKanaReadings" : [],
            "meanings" : [],
            "frequencies" : [],
            "freq_detail" : [],
            "usually_kana" : False,
            "pri" : [],
            "reading_in_freq_list" : False,
            "otherMeanings" : []
        }

        listKanjiReadings = []

        for child2 in child.getchildren():
            if(child2.tag == "k_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "keb"):
                        listKanjiReadings.append(child3.text)

        dicoKanaReadings = {}
        strNonRestrictedReading = ""

        for child2 in child.getchildren():
            if(child2.tag == "r_ele"):
                strReading = ""
                bRestriction = False

                for child3 in child2.getchildren():
                    if(child3.tag == "reb"):
                        strReading = child3.text
                    elif(child3.tag == "re_restr"):
                        bRestriction = True
                        dicoKanaReadings[child3.text] = strReading 
                
                if(not(bRestriction)):
                    strNonRestrictedReading = strReading
                        
        for reading in listKanjiReadings:
            if(not(reading in dicoKanaReadings)):
                dicoKanaReadings[reading] = strNonRestrictedReading

        for child2 in child.getchildren():

            if(child2.tag == "k_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "keb"):
                        if(dicoEntry["reading"] == ""):
                            dicoEntry["reading"] = child3.text
                        else:
                            if(dicoKanaReadings[dicoEntry["reading"]] == dicoKanaReadings[child3.text]):
                                dicoEntry["altKanjiReadings"].append(child3.text)
                    
                    elif(child3.tag == "ke_pri"):
                        if(not(child3.text in dicoEntry["pri"])):
                            dicoEntry["pri"].append(child3.text)
            
            elif(child2.tag == "r_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "reb"):
                        if(dicoEntry["reading"] == ""):
                            dicoEntry["reading"] = child3.text
                            dicoEntry["kana_only"] = True
                        else:
                            dicoEntry["altKanaReadings"].append(child3.text)

                    elif(child3.tag == "re_pri"):
                        if(not(child3.text in dicoEntry["pri"])):
                            dicoEntry["pri"].append(child3.text)
            
            elif(child2.tag == "s"):
                for child3 in child2.getchildren():
                    if(child3.tag == "misc" and child3.text == "uk"):
                        dicoEntry["usually_kana"] = True

                    if(child3.tag == "g" and (len(child3.attrib) == 0 or ("l" in child3.attrib and child3.get("l") == "eng"))):
                        dicoEntry["meanings"].append(child3.text)

        if(dicoEntry["reading"] != ""):
            listEntries.append(dicoEntry)

listMainReading = []

for dicoEntry in listEntries:
    listMainReading.append(dicoEntry["reading"])

for dicoEntry in listEntries:
    for pri in dicoEntry["pri"]:
        if(len(pri) == 4 and pri[0:2] == "nf"):
            freq = int(pri[2:4]) * 500
            dicoEntry["frequencies"].append(freq)
            dicoEntry["freq_detail"].append({"read" : pri, "freq" : freq})


    if(dicoEntry["reading"] in dicoFrequencies):
        dicoEntry["frequencies"].append(dicoFrequencies[dicoEntry["reading"]]["freq"])
        dicoEntry["freq_detail"].append({"read" : dicoEntry["reading"], "freq" : dicoFrequencies[dicoEntry["reading"]]["freq"]})
        if(dicoFrequencies[dicoEntry["reading"]]["freq"] < 5000):
            dicoEntry["reading_in_freq_list"] = True

    for reading in dicoEntry["altKanjiReadings"]:
        if(reading in dicoFrequencies and not(reading in listMainReading)):
            dicoEntry["frequencies"].append(dicoFrequencies[reading]["freq"])
            dicoEntry["freq_detail"].append({"read" : reading, "freq" : dicoFrequencies[reading]["freq"]})

    if(dicoEntry["usually_kana"] and not(dicoEntry["kana_only"]) and len(dicoEntry["altKanaReadings"]) > 0):
            if(dicoEntry["altKanaReadings"][0] in dicoFrequencies):
                dicoEntry["frequencies"].append(dicoFrequencies[dicoEntry["altKanaReadings"][0]]["freq"])
                dicoEntry["freq_detail"].append({"read" : dicoEntry["altKanaReadings"][0], "freq" : dicoFrequencies[dicoEntry["altKanaReadings"][0]]["freq"]})

def fitness(x):
    if(len(x["frequencies"]) == 0):
        return 1000000

    return min(x["frequencies"])

def islow(obj):
    return ((
        "spec2" in obj["pri"] or 
        "ichi2" in obj["pri"] or 
        "news2" in obj["pri"] or 
        "gai2" in obj["pri"] or 
    len(obj["pri"]) == 0) and not(
        "spec1" in obj["pri"] or 
        "news1" in obj["pri"] or
        obj["kana_only"] or
        obj["reading_in_freq_list"]
    ))

#の
def compare(obj1, obj2):
    low1 = islow(obj1)
    low2 = islow(obj2)

    if(low2 and not(low1)):
        return -1

    if(low1 and not(low2)):
        return 1

    fit1 = fitness(obj1)
    fit2 = fitness(obj2)

    if(fit1 == fit2):
        if(len(obj1["pri"]) > len(obj2["pri"])):
            return -1
        elif(len(obj2["pri"]) > len(obj1["pri"])):
            return 1
        else:
            return 0

    return fit1 - fit2

listEntries.sort(key=functools.cmp_to_key(compare))

lowIndex = 0

listRemoved = []
dicoLowestEntry = {}
dicoLowestEntryPerChar = {}

for i in range(len(listEntries)):
    reading = listEntries[i]["reading"]

    if(reading == "の"):
        print("no", i)
    
    if(not(reading in dicoLowestEntry)):
        dicoLowestEntry[reading] = i
    
    for char in reading:
        if(not(char in dicoLowestEntryPerChar)):
            dicoLowestEntryPerChar[char] = {"index" : i, "entry" : listEntries[i]}

    for otherreading in listEntries[i]["altKanjiReadings"]:
        for char in otherreading:
            if(not(char in dicoLowestEntryPerChar)):
                dicoLowestEntryPerChar[char] = {"index" : i, "entry" : listEntries[i]}

for i in range(len(listEntries) - 1, -1, -1):
    reading = listEntries[i]["reading"]
    if(dicoLowestEntry[reading] != i):
        listEntries[dicoLowestEntry[reading]]["otherMeanings"].append(listEntries[i])
        del listEntries[i]

dicoEntries = {}

for entry in listEntries:
    dicoEntries[entry["reading"]] = entry

for i in range(len(listEntries)):
    low = islow(listEntries[i])
    if(low):
        lowIndex = i
        print("low", lowIndex)
        break

listVocabKanjis = []

for kanji in dicoKanjis:
    if(kanji in dicoLowestEntryPerChar):
        dicoKanjis[kanji]["freq_vocab"] = dicoLowestEntryPerChar[kanji]["index"]
        dicoKanjis[kanji]["freq_vocab_entry"] = dicoLowestEntryPerChar[kanji]["entry"]
        listVocabKanjis.append(dicoKanjis[kanji])

listVocabKanjis.sort(key = lambda x : (10000000 if x["freq_vocab"] == -1 else x["freq_vocab"]))

for i in range(len(listVocabKanjis)):
    if(listVocabKanjis[i]["freq_vocab"] != -1):
        listVocabKanjis[i]["freq_vocab"] = i + 1

listAverageKanjis = []

for entry in listKanjis:
    if(entry["freq"] == -1 or entry["freq_vocab"] == -1):
        entry["freq_average"] = -1
    else:
        entry["freq_average"] = (2 * entry["freq_vocab"] + entry["freq"]) / 3

    listAverageKanjis.append(entry)

listAverageKanjis.sort(key = lambda x : (10000000 if x["freq_average"] == -1 else x["freq_average"]))

for i in range (len(listAverageKanjis)):
    if(listAverageKanjis[i]["freq_average"] == -1):
        print("total kanjis", i)
        break

listKanaOnly = []
SetTrueKanaOnly = set()
SetUsuallyKana = set()

for entry in listEntries:
    if(entry["usually_kana"] or entry["kana_only"]): 
        if(not(entry["kana_only"]) and entry["usually_kana"] and entry["altKanaReadings"][0] in SetUsuallyKana):
            continue
        listKanaOnly.append(entry)
    if(entry["kana_only"]):
        SetTrueKanaOnly.add(entry["reading"])
    if(not(entry["kana_only"]) and entry["usually_kana"]):
        SetUsuallyKana.add(entry["altKanaReadings"][0])

for i in range(len(listKanaOnly) - 1, -1, -1):
    if(not(listKanaOnly[i]["kana_only"]) and listKanaOnly[i]["usually_kana"]):
        if(listKanaOnly[i]["altKanaReadings"][0] in SetTrueKanaOnly):
            del listKanaOnly[i]

listLevels = []
dicoKanjiLevel = {}

iId = 0

for i in range(1, 101):
    level = []

    for kana in listKanaOnly[20 * (i - 1) : 20 * i]:
        dicoEntry = {
            "id" : iId,
            "sharedid" : iId,
            "type" : "vocab_kana",
            "display" : "",
            "readings" : [],
            "kun_readings" : [],
            "meanings" : kana["meanings"]
        }

        if(kana["kana_only"]):
            dicoEntry["display"] = kana["reading"]
        else:
            dicoEntry["display"] = kana["altKanaReadings"][0]

        iId += 1
        level.append(dicoEntry)

    for kanji in listAverageKanjis[25 * (i - 1) : 25 * i]:
        dicoEntry = {
            "id" : iId,
            "sharedid" : iId,
            "type" : "kanji",
            "display" : kanji["literal"],
            "readings" : list(map(jaconv.kata2hira, kanji["readings_on"])),
            "kun_readings" : list(map(jaconv.kata2hira, kanji["readings_kun"])),
            "meanings" : kanji["meanings"]
        }

        dicoKanjiLevel[kanji["literal"]] = (i - 1)

        iId += 1
        level.append(dicoEntry)

    listLevels.append(level)

setMainVocabReadings = set()
dicoSecondaryVocabReadings = {}

def CheckReadingValidity(reading):
    global dicoKanjiLevel
    global dicoKanjis

    bValid = False

    for char in reading:
        if(char in dicoKanjiLevel):
            bValid = True

        if(char in dicoKanjis and not(char in dicoKanjiLevel)):
            print("Invalid Kanji", char)
            bValid = False
            break
    
    return bValid

for entry in listEntries[:lowIndex]:
    if(entry["kana_only"]):
        continue

    if(CheckReadingValidity(entry["reading"])):
        setMainVocabReadings.add(entry["reading"])

    altreadings = copy.deepcopy(entry["altKanjiReadings"])

    for otherentry in entry["otherMeanings"]:
        altreadings.extend(otherentry["altKanjiReadings"])

    for reading in altreadings:

        if(not(reading in dicoSecondaryVocabReadings)):
            dicoSecondaryVocabReadings[reading] = 0

        dicoSecondaryVocabReadings[reading] += 1

for entry in listEntries[:lowIndex]:
    if(entry["kana_only"]):
        continue

    dicoEntry = {
        "id" : iId,
        "sharedid" : iId,
        "type" : "vocab",
        "display" : entry["reading"],
        "readings" : entry["altKanaReadings"],
        "kun_readings" : [],
        "meanings" : entry["meanings"]
    }

    readinglist = [entry["reading"]]
    readinglist.extend(entry["altKanjiReadings"])

    for otherentry in entry["otherMeanings"]:
        dicoEntry["meanings"].extend(otherentry["meanings"])
        dicoEntry["meanings"] = list(dict.fromkeys(dicoEntry["meanings"]))
        dicoEntry["readings"].extend(otherentry["altKanaReadings"])
        dicoEntry["readings"] = list(dict.fromkeys(dicoEntry["readings"]))
        readinglist.extend(otherentry["altKanjiReadings"])

    dicoEntry["readings"] = list(dict.fromkeys(list(map(jaconv.kata2hira, dicoEntry["readings"]))))
    readinglist = list(dict.fromkeys(readinglist))

    sharedid = iId

    for iReading, reading in enumerate(readinglist):
        levelreading = -1
        bValid = False

        if(reading in dicoSecondaryVocabReadings and dicoSecondaryVocabReadings[reading] > 1):
            print("Invalid Secondary Reading", reading)
            continue

        if(CheckReadingValidity(reading) and (iReading == 0 or not(reading in setMainVocabReadings))):

            for char in reading:
                if(char in dicoKanjiLevel and dicoKanjiLevel[char] > levelreading):
                    levelreading = dicoKanjiLevel[char]

            dicoCopy = copy.deepcopy(dicoEntry)
            dicoCopy["id"] = iId
            dicoCopy["sharedid"] = sharedid
            dicoCopy["display"] = reading

            if(iId != sharedid):
                dicoCopy["meanings"] = []
                dicoCopy["readings"] = []

            iId += 1
            listLevels[levelreading].append(dicoCopy)

for ilevel, level in enumerate(listLevels):
    for i in range(len(level) - 1, -1, -1):
        item = level[i]
        if(len(item["meanings"]) == 0 and item["id"] == item["sharedid"]):
            print(ilevel, item)
            del(level[i])

        if((len(item["readings"]) + len(item["kun_readings"])) == 0 and item["id"] == item["sharedid"] and item["type"] != "vocab_kana"):
            print(ilevel, item)
            del(level[i])

iCurrentKanaPosition = 2000

for ilevel, level in enumerate(listLevels):
    while(len(level) < 150):
        kana = listKanaOnly[iCurrentKanaPosition]

        dicoEntry = {
            "id" : iId,
            "sharedid" : iId,
            "type" : "vocab_kana",
            "display" : "",
            "readings" : [],
            "kun_readings" : [],
            "meanings" : kana["meanings"]
        }

        if(kana["kana_only"]):
            dicoEntry["display"] = kana["reading"]
        else:
            dicoEntry["display"] = kana["altKanaReadings"][0]

        iId += 1
        iCurrentKanaPosition += 1
        level.append(dicoEntry)

for i in range(len(listLevels)):
    print(i, len(listLevels[i]))

dicoHashConversion = {}
uint64max = 18446744073709551616

for level in listLevels:
    for item in level:
        newid = int(hashlib.md5((item["type"] + ":" + item["display"]).encode("utf8")).hexdigest(), 16) % uint64max
        dicoHashConversion[item["id"]] = newid
        item["id"] = newid

for level in listLevels:
    for item in level:
        item["sharedid"] = dicoHashConversion[item["sharedid"]]

json.dump(listLevels, open("../output/Levels.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

print("DONE VOCABULARY")


        