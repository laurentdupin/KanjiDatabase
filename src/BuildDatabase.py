from lxml import etree
import os
import functools

if(not(os.path.exists("../build/"))):
    os.mkdir("../build")

dicoKanjis = {}

kanjidic = etree.parse("../sources/kanjidic/kanjidic2.xml") 
kanjidicroot = kanjidic.getroot()

for child in kanjidicroot.getchildren():

    if(child.tag == "character"):

        dicoKanji = {
            "literal" : "",
            "freq" : -1,
            "freq_vocab" : -1,
            "readings_on" : [],
            "readings_kun" : [],
            "meanings" : []
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
dicoLowestEntryPerChar = {}

for i in range(len(listEntries)):
    reading = listEntries[i]["reading"]

    if(reading == "の"):
        print("no", i)
    
    if(not(reading in dicoLowestEntry)):
        dicoLowestEntry[reading] = i
    
    for char in reading:
        if(not(char in dicoLowestEntryPerChar)):
            dicoLowestEntryPerChar[char] = i

    for otherreading in listEntries[i]["altKanjiReadings"]:
        for char in otherreading:
            if(not(char in dicoLowestEntryPerChar)):
                dicoLowestEntryPerChar[char] = i

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
        dicoKanjis[kanji]["freq_vocab"] = dicoLowestEntryPerChar[kanji]
        listVocabKanjis.append(dicoKanjis[kanji])

listVocabKanjis.sort(key = lambda x : (10000000 if x["freq_vocab"] == -1 else x["freq_vocab"]))

for i in range(len(listVocabKanjis)):
    if(listVocabKanjis[i]["freq_vocab"] != -1):
        listVocabKanjis[i]["freq_vocab"] = i + 1

print("DONE VOCABULARY")


        