from lxml import etree
import os

if(not(os.path.exists("../build/"))):
    os.mkdir("../build")

dicoFrequencies = {}

with open("../sources/frequency-leeds/44492-japanese-words-latin-lines-removed.txt", "r") as frequencyleeds:
    iCounter = 0

    for line in frequencyleeds.readlines():

        line = line.replace("\r", "").replace("\n", "")
        if(not(line in dicoFrequencies)):
            dicoFrequencies[line] = {"freq" : iCounter, "occ" : 1}
        else:
            dicoFrequencies[line]["freq"] = (dicoFrequencies[line]["freq"] * dicoFrequencies[line]["occ"] + iCounter) / (dicoFrequencies[line]["occ"] + 1)
            dicoFrequencies[line]["occ"] += 1

        iCounter += 1
        

with open("../sources/frequency-wiki/Freq1-10000.txt", "r") as frequencywiki:
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

with open("../sources/frequency-wiki/Freq10001-20000.txt", "r") as frequencywiki:
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

root = jmdict.getroot()

listEntries = []

for child in root.getchildren():
    
    if(child.tag == "entry"):

        dicoEntry = {
            "reading" : "",
            "altKanjiReadings" : [],
            "altKanaReadings" : [],
            "meanings" : [],
            "frequencies" : [],
            "usually_kana" : False
        }

        for child2 in child.getchildren():

            if(child2.tag == "k_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "keb"):
                        if(dicoEntry["reading"] == ""):
                            dicoEntry["reading"] = child3.text
                        else:
                            dicoEntry["altKanjiReadings"].append(child3.text)
            
            elif(child2.tag == "r_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "reb"):
                        if(dicoEntry["reading"] == ""):
                            dicoEntry["reading"] = child3.text
                        else:
                            dicoEntry["altKanaReadings"].append(child3.text)
            
            elif(child2.tag == "s"):
                for child3 in child2.getchildren():
                    if(child3.tag == "misc" and "&uk;" in child3.text):
                        dicoEntry["usually_kana"] = True

                    if(child3.tag == "g" and (len(child3.attrib) == 0 or ("l" in child3.attrib and child3.get("l") == "eng"))):
                        dicoEntry["meanings"].append(child3.text)

        if(dicoEntry["reading"] != ""):
            listEntries.append(dicoEntry)

            if(dicoEntry["reading"] in dicoFrequencies):
                dicoEntry["frequencies"].append(dicoFrequencies[dicoEntry["reading"]]["freq"])

            for reading in dicoEntry["altKanjiReadings"]:
                if(reading in dicoFrequencies):
                    dicoEntry["frequencies"].append(dicoFrequencies[reading]["freq"])

            if(dicoEntry["usually_kana"]):
                for reading in dicoEntry["altKanaReadings"]:
                    if(reading in dicoFrequencies):
                        dicoEntry["frequencies"].append(dicoFrequencies[reading]["freq"])

def fitness(x):
    if(len(x["frequencies"]) == 0):
        return float("inf")

    return min(x["frequencies"])

listEntries.sort(key=lambda x: fitness(x))

print("done")