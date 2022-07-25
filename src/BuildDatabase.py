from lxml import etree
import os

if(not(os.path.exists("../build/"))):
    os.mkdir("../build")

jmdict = etree.parse("../sources/jmdict/JMdict.xml") 
root = jmdict.getroot()

dicoEntries = {}

for child in root.getchildren():
    
    if(child.tag == "entry"):

        keyEntry = ""
        dicoEntry = {
            "altKanjiReadings" : [],
            "altKanaReadings" : [],
            "meanings" : []
        }

        for child2 in child.getchildren():

            if(child2.tag == "k_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "keb"):
                        if(keyEntry == ""):
                            keyEntry = child3.text
                        else:
                            dicoEntry["altKanjiReadings"].append(child3.text)
            
            elif(child2.tag == "r_ele"):
                for child3 in child2.getchildren():
                    if(child3.tag == "reb"):
                        if(keyEntry == ""):
                            keyEntry = child3.text
                        else:
                            dicoEntry["altKanaReadings"].append(child3.text)
            
            elif(child2.tag == "s"):
                for child3 in child2.getchildren():
                    if(child3.tag == "g" and (len(child3.attrib) == 0 or ("l" in child3.attrib and child3.get("l") == "eng"))):
                        dicoEntry["meanings"].append(child3.text)

        if(keyEntry != ""):
            dicoEntries[keyEntry] = dicoEntry

print("done")