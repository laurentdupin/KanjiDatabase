from lxml import etree
import os
import functools

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

parser = etree.XMLParser()
jmdict = etree.parse("../sources/jmdict/JMdict.xml", parser=parser) 

root = jmdict.getroot()

listEntries = []

for child in root.getchildren():
    
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

        for child2 in child.getchildren():

            if(child2.tag == "k_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "keb"):
                        if(dicoEntry["reading"] == ""):
                            dicoEntry["reading"] = child3.text
                        else:
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
    if(dicoEntry["reading"] in dicoFrequencies):
        dicoEntry["frequencies"].append(dicoFrequencies[dicoEntry["reading"]]["freq"])
        dicoEntry["freq_detail"].append({"read" : dicoEntry["reading"], "freq" : dicoFrequencies[dicoEntry["reading"]]["freq"]})
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
        "ichi1" in obj["pri"] or 
        "news1" in obj["pri"] or 
        "gai1" in obj["pri"] or 
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

for i in range(len(listEntries)):
    reading = listEntries[i]["reading"]

    if(reading == "の"):
        print("no", i)
    
    if(not(reading in dicoLowestEntry)):
        dicoLowestEntry[reading] = i

for i in range(len(listEntries) - 1, -1, -1):
    reading = listEntries[i]["reading"]
    if(dicoLowestEntry[reading] != i):
        listEntries[dicoLowestEntry[reading]]["otherMeanings"].append(listEntries[i])
        del listEntries[i]

for i in range(len(listEntries)):
    low = islow(listEntries[i])
    if(low):
        lowIndex = i
        print("low", lowIndex)
        break

print("done")