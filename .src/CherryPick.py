import tkinter
import os
import json
import Tooltip
import pyperclip
import copy
import string
from googletrans import Translator

#Need to do pip install googletrans==3.1.0a0 for it to work
translator = Translator()

FontSize = 22

if(not(os.path.exists("../.temp/Levels.json"))):
    print("No .temp/Levels.json found")
    exit(1)

if(not(os.path.exists("../output/Levels.json"))):
    print("No output/Levels.json found")
    exit(1)

if(not(os.path.exists("./SpecialToAdd.txt"))):
    print("No SpecialToAdd.txt found")
    exit(1)

if(not(os.path.exists("./AddedElements.json"))):
    print("No AddedElements.json found")
    exit(1)



listInput = json.load(open("../.temp/Levels.json", "r", encoding="utf-8"))
dicoCurrentLevels = json.load(open("../output/Levels.json", "r", encoding="utf-8"))

listAddedElements = json.load(open("./AddedElements.json", "r", encoding="utf-8"))
dicoChallengeId = {}

if(os.path.exists("../../../Scripts/ChallengesLogic.cs")):
    challengefile = open("../../../Scripts/ChallengesLogic.cs", 'r')
    content = challengefile.read()
    
    newchallengestring = "new List<ChallengeItem>"
    listChallengeIndexes = []
    currentindex = content.index(newchallengestring, 0) + 1

    while(content.find(newchallengestring, currentindex) >= 0):
        namesecond = content.rindex('"', 0, currentindex)
        namefirst = content.rindex('"', 0, namesecond)
        print(content[namefirst + 1:namesecond])
        oldindex = currentindex
        currentindex = content.index(newchallengestring, currentindex) + 1
        listChallengeIndexes.append((oldindex - 1, currentindex, content[namefirst + 1:namesecond]))
        
    refstring = "new ChallengeItem { id = "

    for block in listChallengeIndexes:
        currentindex = block[0]
        dicoChallengeId[block[2]] = []

        while(content.find(refstring, currentindex, block[1]) >= 0):
            currentindex = content.index(refstring, currentindex) + 1
            firstquoteindex = content.index('id = ', currentindex)
            endquoteindex = content.index(',', firstquoteindex)
            dicoChallengeId[block[2]].append(int(content[firstquoteindex+5:endquoteindex]))


dicoItemPerId = {}
dicoItemPerIdCurrent = {}

for item in listAddedElements:
    listInput[-1].append(item)

for level in listInput:
    for item in level:
        dicoItemPerId[item["id"]] = item

for level in dicoCurrentLevels:
    for item in dicoCurrentLevels[level]:
        dicoItemPerIdCurrent[item["id"]] = item

for challenge in dicoChallengeId:
    dicoCurrentLevels[challenge] = []
    for id in dicoChallengeId[challenge]:
        dicoCurrentLevels[challenge].append(dicoItemPerIdCurrent[id])

listSpecialToAdd = []

with open("./SpecialToAdd.txt", 'r') as fileSpecialToAdd:
    for line in fileSpecialToAdd.readlines():
        line = line.replace("\r", "").replace("\n", "")
        listSpecialToAdd.append(int(line))

dicoOutput = {}
 
if(os.path.exists("../.src/Selected.json")):
    dicoOutput = json.load(open("../.src/Selected.json", "r", encoding="utf-8"))

if(not("SelectedVocab" in dicoOutput)):
    dicoOutput["SelectedVocab"] = {}

if(not("SelectedKanaOnly" in dicoOutput)):
    dicoOutput["SelectedKanaOnly"] = {}

if(not("KanaOnlySharedIds" in dicoOutput)):
    dicoOutput["KanaOnlySharedIds"] = {}

if(not("KunReadingSelections" in dicoOutput)):
    dicoOutput["KunReadingSelections"] = {}

if(not("MeaningsTranslations" in dicoOutput)):
    dicoOutput["MeaningsTranslations"] = {}

if(not("PreferedMeanings" in dicoOutput)):
    dicoOutput["PreferedMeanings"] = {}

if(not("PreferedMeaningsfr" in dicoOutput)):
    dicoOutput["PreferedMeaningsfr"] = {}

def Quit():
    global root
    root.quit()

###
###
### KANA ONLY BLOCK
###
###

def KanaOnlySelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectKanaOnlyLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if(str(iLevel) in dicoOutput["SelectedKanaOnly"]):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

iKanaOnlyLevelSelected = -1
iKanaOnlyCounter = -1
setSelectedKanaOnly = set()
dicoKanaOnlySharedIds = {}

def SelectKanaOnlyLevel(level):
    global iKanaOnlyLevelSelected
    global iKanaOnlyCounter
    global setSelectedKanaOnly
    global dicoKanaOnlySharedIds
    iKanaOnlyLevelSelected = level
    iKanaOnlyCounter = -1
    setSelectedKanaOnly = set()
    dicoKanaOnlySharedIds = {}
    DisplayNextKanaOnlyChoice()

def AcceptKanaOnly(kanaonly):
    global sharedidentry
    global setSelectedKanaOnly
    global dicoKanaOnlySharedIds

    if(sharedidentry.get() != ""):
        dicoKanaOnlySharedIds[kanaonly] = sharedidentry.get()

    sharedidentry.delete(0,tkinter.END)
    setSelectedKanaOnly.add(kanaonly)
    DisplayNextKanaOnlyChoice()

def RefuseKanaOnly(kanaonly):
    global sharedidentry
    sharedidentry.delete(0,tkinter.END)
    DisplayNextKanaOnlyChoice()

sharedidentry = None

def DisplayNextKanaOnlyChoice():
    global iKanaOnlyLevelSelected
    global iKanaOnlyCounter
    global root
    global sharedidentry

    iKanaOnlyCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    iCurrentKanaOnly = 0
    selectedEntry = None

    iTotalEntryCount = 0

    for entry in listInput[iKanaOnlyLevelSelected]:
        if(entry["type"] == "vocab_kana"):
            iTotalEntryCount += 1

    for entry in listInput[iKanaOnlyLevelSelected]:
        if(entry["type"] == "vocab_kana"):
            if(iCurrentKanaOnly != iKanaOnlyCounter):
                iCurrentKanaOnly += 1
            else:
                selectedEntry = entry
                break
    
    print(iKanaOnlyCounter, iTotalEntryCount)

    if(selectedEntry == None):
        DoneWithKanaOnlyLevel()
        return

    label = tkinter.Label(root, text=selectedEntry["display"], width=80)
    label.config(font=('Arial', FontSize))
    label.grid(row=0, column=0, columnspan=2)

    displaymeaning = ""

    if(selectedEntry["id"] != selectedEntry["sharedid"]):
        displaymeaning = dicoItemPerId[selectedEntry["sharedid"]]["meanings"][0]
    else:
        displaymeaning = selectedEntry["meanings"][0]

    label = tkinter.Label(root, text=displaymeaning)
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=1, column=0, columnspan=2)

    button = tkinter.Button(root, text="Yes", command=lambda id=selectedEntry["id"]: AcceptKanaOnly(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=2, column = 0)

    if(str(iKanaOnlyLevelSelected) in dicoOutput["SelectedKanaOnly"] and selectedEntry["id"] in dicoOutput["SelectedKanaOnly"][str(iKanaOnlyLevelSelected)]):
        button.config(bg = "LightBlue1")

    button = tkinter.Button(root, text="No", command=lambda id=selectedEntry["id"]: RefuseKanaOnly(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=2, column = 1)

    if(str(iKanaOnlyLevelSelected) in dicoOutput["SelectedKanaOnly"] and not(selectedEntry["id"] in dicoOutput["SelectedKanaOnly"][str(iKanaOnlyLevelSelected)])):
        button.config(bg = "LightBlue1")

    sharedidentry = tkinter.Entry(root)
    sharedidentry.config(font=('Arial', FontSize))
    sharedidentry.grid(row=3, column=0, columnspan=2)

    if(str(iKanaOnlyLevelSelected) in dicoOutput["KanaOnlySharedIds"] and 
        str(selectedEntry["id"]) in dicoOutput["KanaOnlySharedIds"][str(iKanaOnlyLevelSelected)]):
        sharedidentry.delete(0,tkinter.END)
        sharedidentry.insert(0, dicoOutput["KanaOnlySharedIds"][str(iKanaOnlyLevelSelected)][str(selectedEntry["id"])])

    pyperclip.copy(selectedEntry["display"])

def DoneWithKanaOnlyLevel():
    global dicoOutput
    dicoOutput["SelectedKanaOnly"][str(iKanaOnlyLevelSelected)] = list(setSelectedKanaOnly)
    dicoOutput["KanaOnlySharedIds"][str(iKanaOnlyLevelSelected)] = dicoKanaOnlySharedIds
    KanaOnlySelection()

###
###
### VOCABULARY BLOCK
###
###

iLevelSelected = -1
iKanjiCounter = -1
setSelectedVocab = set()

def VocabularySelection():
    global root
    for child in root.winfo_children():
        child.destroy()

    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if(str(iLevel) in dicoOutput["SelectedVocab"]):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

def SelectLevel(level):
    global iLevelSelected
    global iKanjiCounter
    global setSelectedVocab
    iLevelSelected = level
    iKanjiCounter = -1
    setSelectedVocab = set()
    DisplayNextKanjiChoices()

def SelectedVocab(vocab):
    global dicoPerButton
    global setSelectedVocab
    print(vocab)
    setSelectedVocab.add(vocab)
    dicoPerButton[vocab].config(state=tkinter.DISABLED)

dicoPerButton = {}

def DisplayNextKanjiChoices():
    global iLevelSelected
    global iKanjiCounter
    global root
    global dicoPerButton
    iKanjiCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    iCurrentKanji = 0
    selectedEntry = None

    for entry in listInput[iLevelSelected]:
        if(entry["type"] == "kanji"):
            if(iCurrentKanji != iKanjiCounter):
                iCurrentKanji += 1
            else:
                selectedEntry = entry
                break
    
    if(selectedEntry == None):
        DoneWithLevel()
        return

    ColumnCount = 4

    label = tkinter.Label(root, text=selectedEntry["display"])
    label.config(font=('Arial', FontSize))
    label.grid(row=0, column=0, columnspan=ColumnCount)

    button = tkinter.Button(root, text="Continue", command=lambda: DisplayNextKanjiChoices())
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column = 0, columnspan=ColumnCount)

    iButtonPosition = 2 * ColumnCount

    for entry in listInput[iLevelSelected]:
        if(entry["type"] == "vocab"):
            if(entry["id"] != entry["sharedid"]):
                continue

            if(selectedEntry["display"] in entry["display"]):
                button = tkinter.Button(root, text=entry["display"], command=lambda id=entry["id"]: SelectedVocab(id))
                button.config(font=('Arial', FontSize))

                if(entry["id"] in setSelectedVocab):
                    button.config(bg="tan1")
                elif(str(iLevelSelected) in dicoOutput["SelectedVocab"] and 
                    entry["id"] in dicoOutput["SelectedVocab"][str(iLevelSelected)]):
                    button.config(bg="LightBlue1")

                button.grid(row=iButtonPosition // ColumnCount, column = iButtonPosition % ColumnCount)
                Tooltip.CreateToolTip(button, entry["meanings"][0])
                iButtonPosition += 1
                dicoPerButton[entry["id"]] = button

def DoneWithLevel():
    global dicoOutput
    dicoOutput["SelectedVocab"][str(iLevelSelected)] = list(setSelectedVocab)
    VocabularySelection()

###
###
### MEANING TRANSLATION BLOCK
###
###

meaningtranslationlang = "fr"

def FrMeaningTranslation():
    global meaningtranslationlang
    meaningtranslationlang = "fr"
    MeaningTranslationSelection()

def EsMeaningTranslation():
    global meaningtranslationlang
    meaningtranslationlang = "es"
    MeaningTranslationSelection()

def PtMeaningTranslation():
    global meaningtranslationlang
    meaningtranslationlang = "pt"
    MeaningTranslationSelection()

def MeaningTranslationSelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(dicoCurrentLevels):
        button = tkinter.Button(root, text=level, command = lambda level=level: SelectMeaningTranslation(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        langisdone = True

        if(level in dicoCurrentLevels):
            for item in dicoCurrentLevels[level]:
                if(item["sharedid"] == item["id"] and len(item["meanings_" + meaningtranslationlang]) == 0):
                    langisdone = False
                    break

        if(level in dicoOutput["MeaningsTranslations"] and langisdone):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

strMeaningTranslationLevelSelected = -1
iMeaningTranslationCounter = -1
dicoMeaningsTranslations = {}
setMeaningsAlreadyDone = set()
dicoTranslateButtons = {}

def SelectMeaningTranslation(level):
    global strMeaningTranslationLevelSelected
    global iMeaningTranslationCounter
    global dicoMeaningsTranslations
    global setMeaningsAlreadyDone
    strMeaningTranslationLevelSelected = level
    iMeaningTranslationCounter = -1
    dicoMeaningsTranslations = {}
    setMeaningsAlreadyDone = set()
    DisplayNextMeanings()

dicoMeaningEntries = {}

def ContinueToNextMeaning(id):
    global dicoMeaningEntries
    global setMeaningsAlreadyDone

    setMeaningsAlreadyDone.add(id)
    id = str(id)

    for lang in dicoMeaningEntries:
        for meaning in dicoMeaningEntries[lang]:
            if(dicoMeaningEntries[lang][meaning].get() != ""):
                if(not(id in dicoMeaningsTranslations)):
                    dicoMeaningsTranslations[id] = {}
                if(not(lang in dicoMeaningsTranslations[id])):
                    dicoMeaningsTranslations[id][lang] = {}
                dicoMeaningsTranslations[id][lang][meaning] = dicoMeaningEntries[lang][meaning].get()

    DisplayNextMeanings()

def SearchNextEmpty(id):
    global meaningtranslationlang
    global iMeaningTranslationCounter
    global setMeaningsAlreadyDone

    setMeaningsAlreadyDone.add(id)

    iCurrentMeanings = 0

    iMeaningTranslationCounter += 1

    for entry in dicoCurrentLevels[strMeaningTranslationLevelSelected]:
        if(iCurrentMeanings == iMeaningTranslationCounter):
            if(entry["id"] == entry["sharedid"]):
                if(len(entry["meanings_" + meaningtranslationlang]) == 0 and not(entry["sharedid"] in setMeaningsAlreadyDone)):
                    break
                else:
                    iMeaningTranslationCounter += 1
            else:
                sharedEntry = dicoItemPerIdCurrent[entry["sharedid"]]
                if(len(sharedEntry["meanings_" + meaningtranslationlang]) == 0 and not(entry["sharedid"] in setMeaningsAlreadyDone)):
                    break
                else:
                    iMeaningTranslationCounter += 1
    
        iCurrentMeanings += 1

    iMeaningTranslationCounter -= 1

    ContinueToNextMeaning(id)

def Translate():
    global dicoTranslateButtons
    dicoTranslations = {}

    try:
        translations = translator.translate(list(dicoTranslateButtons), src='en', dest=meaningtranslationlang)
        for translation in translations:
            dicoTranslations[translation.origin] = translation.text
    except:
        pass

    for meaning in dicoTranslateButtons:
        if(meaning in dicoTranslations):
            dicoTranslateButtons[meaning].configure(text=dicoTranslations[meaning], command=lambda text=dicoTranslations[meaning] : pyperclip.copy(text))

    dicoTranslateButtons = {}

def DisplayNextMeanings():
    global strMeaningTranslationLevelSelected
    global iMeaningTranslationCounter
    global root
    global dicoMeaningEntries
    global dicoOutput
    global translator
    global meaningtranslationlang
    global dicoTranslateButtons

    dicoTranslateButtons = {}

    iMeaningTranslationCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    selectedEntry = None

    iCurrentMeanings = 0

    for iPosition, entry in enumerate(dicoCurrentLevels[strMeaningTranslationLevelSelected]):
        if(iCurrentMeanings == iMeaningTranslationCounter):
            selectedEntry = dicoItemPerId[entry["id"]]
            break
        else:
            iCurrentMeanings += 1

    if(selectedEntry == None):
        DoneWithMeaningTranslationLevel()
        return

    originalentry = selectedEntry

    print(iPosition, len(dicoCurrentLevels[strMeaningTranslationLevelSelected]))

    if(selectedEntry["id"] != selectedEntry["sharedid"]):
        selectedEntry = dicoItemPerId[selectedEntry["sharedid"]]

    dicoTempKanaOnlySharedIds = {}

    for level in dicoOutput["KanaOnlySharedIds"]:
        for item in dicoOutput["KanaOnlySharedIds"][level]:
            dicoTempKanaOnlySharedIds[int(item)] = int(dicoOutput["KanaOnlySharedIds"][level][item])

    if(selectedEntry["id"] in dicoTempKanaOnlySharedIds):
        selectedEntry = dicoItemPerId[dicoTempKanaOnlySharedIds[selectedEntry["id"]]]

    dicoMeaningEntries = {}

    label = tkinter.Label(root, text=originalentry["display"], width=40)
    label.config(font=('Arial', int(FontSize * 2)))
    label.grid(row=0, column=0, columnspan=8)

    button = tkinter.Button(root, text="Next Empty", command=lambda id=selectedEntry["id"] : SearchNextEmpty(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=0)

    button = tkinter.Button(root, text="Translate", command=lambda : Translate())
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=1, columnspan=3)

    button = tkinter.Button(root, text="Continue", command=lambda id=selectedEntry["id"] : ContinueToNextMeaning(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=4, columnspan=3)

    listAddedMeanings = []

    dicoTempMeaningsTranslationsAndReplacements = {}

    for level in dicoOutput["MeaningsTranslations"]:
        for item in dicoOutput["MeaningsTranslations"][level]:
            dicoTempMeaningsTranslationsAndReplacements[int(item)] = dicoOutput["MeaningsTranslations"][level][item]

    for iLang, language in enumerate(["en", meaningtranslationlang]):
        meaningname = "meanings"

        if(language != "en"):
            meaningname += "_" + language

        label = tkinter.Label(root, text="Original-" + language)
        label.config(font=('Arial', int(FontSize * 0.7)))
        label.grid(row=3, column=2 * iLang)

        label = tkinter.Label(root, text=language)
        label.config(font=('Arial', int(FontSize * 0.7)))
        label.grid(row=3, column=2 * iLang + 1)

        iCurrentRow = 4

        dicoMeaningEntries[language] = {}

        for iMeaning, meaning in enumerate(selectedEntry[meaningname]):
            if(meaning in listAddedMeanings):
                continue

            listAddedMeanings.append(meaning)

            labeltext = meaning

            label = tkinter.Label(root, text=labeltext)
            label.config(font=('Arial', int(FontSize * 0.6)))
            label.grid(row=iCurrentRow, column=2 * iLang)

            entry = tkinter.Entry(root)
            entry.config(font=('Arial', int(FontSize * 0.6)))
            entry.grid(row=iCurrentRow, column=2 * iLang + 1)
            dicoMeaningEntries[language][meaning] = entry

            if(selectedEntry["id"] in dicoTempMeaningsTranslationsAndReplacements and 
                language in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]]):
                for transmeaning in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]][language]:
                    if(transmeaning.lower() == meaning.lower()):
                        entry.insert(0, dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]][language][transmeaning])

            if(language == "en" and iMeaning < 5):  
                button = tkinter.Button(root, text="")
                button.config(font=('Arial', int(FontSize * 0.6)))
                button.grid(row=iCurrentRow + 1, column=2 * iLang)
                dicoTranslateButtons[meaning] = button

            iCurrentRow += 2

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.6)))
        entry.grid(row=iCurrentRow, column=2 * iLang + 1)
        dicoMeaningEntries[language][""]= entry

        if(selectedEntry["id"] in dicoTempMeaningsTranslationsAndReplacements and 
            language in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]] and 
            "" in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]][language]):
            entry.insert(0, dicoTempMeaningsTranslationsAndReplacements[selectedEntry["id"]][language][""])


def DoneWithMeaningTranslationLevel():
    global dicoOutput
    global root

    if(not(strMeaningTranslationLevelSelected in dicoOutput["MeaningsTranslations"])):
        dicoOutput["MeaningsTranslations"][strMeaningTranslationLevelSelected] = {}

    for item in dicoMeaningsTranslations:
        if(item in dicoOutput["MeaningsTranslations"][strMeaningTranslationLevelSelected]):
            for lang in dicoMeaningsTranslations[item]:
                dicoOutput["MeaningsTranslations"][strMeaningTranslationLevelSelected][item][lang] = dicoMeaningsTranslations[item][lang]
        else:
            dicoOutput["MeaningsTranslations"][strMeaningTranslationLevelSelected][item] = dicoMeaningsTranslations[item]
        
    Quit()

###
###
### KUN READING BLOCK
###
###

def KunReadingSelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectKunReadingLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if(str(iLevel) in dicoOutput["KunReadingSelections"]):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

iKunReadingLevelSelected = -1
iKunReadingCounter = -1
dicoKunReadingsSelections = {}

def SelectKunReadingLevel(level):
    global iKunReadingLevelSelected
    global iKunReadingCounter
    global dicoKunReadingsSelections
    iKunReadingLevelSelected = level
    iKunReadingCounter = -1
    dicoKunReadingsSelections = {}
    DisplayNextKunReadingChoice()

iExpectedReadingCount = 0

def SelectKunReading(id, originalreading, newreading):
    global dicoKunReadingsSelections
    global iExpectedReadingCount

    if(not(id in dicoKunReadingsSelections)):
        dicoKunReadingsSelections[id] = {}

    dicoKunReadingsSelections[id][originalreading] = newreading

    print(len(dicoKunReadingsSelections[id]), iExpectedReadingCount)

    if(len(dicoKunReadingsSelections[id]) == iExpectedReadingCount):
        DisplayNextKunReadingChoice()

def DisplayNextKunReadingChoice():
    global iKunReadingLevelSelected
    global iKunReadingCounter
    global root
    global iExpectedReadingCount

    iKunReadingCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    iCurrentKunReadingKanji = 0
    selectedEntry = None
    maxsplitpointcount = 0
    iExpectedReadingCount = 0

    for entry in listInput[iKunReadingLevelSelected]:
        if(entry["type"] == "kanji"):
            
            iExpectedReadingCount = 0
            bPointKunReading = False

            for kunreading in entry["kun_readings"]:
                if("." in kunreading):
                    iExpectedReadingCount += 1
                    bPointKunReading = True
                    maxsplitpointcount = max(maxsplitpointcount, len(kunreading.split(".")))

            if(bPointKunReading):
                if(iCurrentKunReadingKanji != iKunReadingCounter):
                    iCurrentKunReadingKanji += 1
                else:
                    selectedEntry = entry
                    break

    if(selectedEntry == None):
        DoneWithKunReadingLevel()
        return

    label = tkinter.Label(root, text=selectedEntry["display"], width=80)
    label.config(font=('Arial', FontSize))
    label.grid(row=0, column=0, columnspan=maxsplitpointcount)

    currentrow = 1

    for kunreading in selectedEntry["kun_readings"]:
        if("." in kunreading):

            arraypart = kunreading.split(".")
            currentcolumn =  0

            for item in arraypart:
                button = tkinter.Button(root, text=item, command=lambda id=selectedEntry["id"], orireading = kunreading, newreading=item: SelectKunReading(id, orireading, newreading))
                button.config(font=('Arial', int(FontSize * 0.7)))
                button.grid(row=currentrow, column = currentcolumn)
                currentcolumn += 1

            currentrow += 1

def DoneWithKunReadingLevel():
    global dicoOutput
    dicoOutput["KunReadingSelections"][str(iKunReadingLevelSelected)] = dicoKunReadingsSelections
    KunReadingSelection()

###
###
### KUN READING BLOCK
###
###

strSelectedMeaningType = ""

def KanjiPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "kanji"
    strMeaningArray = "meanings"
    strPreferedMeaningsSuffix = ""
    PreferedMeaningsSelection()

def KanaOnlyPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "vocab_kana"
    strMeaningArray = "meanings"
    strPreferedMeaningsSuffix = ""
    PreferedMeaningsSelection()

def VocabPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "vocab"
    strMeaningArray = "meanings"
    strPreferedMeaningsSuffix = ""
    PreferedMeaningsSelection()

def FRKanjiPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "kanji"
    strMeaningArray = "meanings_fr"
    strPreferedMeaningsSuffix = "fr"
    PreferedMeaningsSelection()

def FRKanaOnlyPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "vocab_kana"
    strMeaningArray = "meanings_fr"
    strPreferedMeaningsSuffix = "fr"
    PreferedMeaningsSelection()

def FRVocabPreferedMeaningsSelection():
    global strSelectedMeaningType
    global strMeaningArray
    global strPreferedMeaningsSuffix
    strSelectedMeaningType = "vocab"
    strMeaningArray = "meanings_fr"
    strPreferedMeaningsSuffix = "fr"
    PreferedMeaningsSelection()

def PreferedMeaningsSelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(dicoCurrentLevels):
        button = tkinter.Button(root, text=level, command = lambda level=level: SelectPreferedMeaningsLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if((level in dicoOutput["PreferedMeanings" + strPreferedMeaningsSuffix] and strSelectedMeaningType in dicoOutput["PreferedMeanings" + strPreferedMeaningsSuffix][level]) or
            (level in dicoOutput["PreferedMeanings"] and strSelectedMeaningType in dicoOutput["PreferedMeanings"][level]) ):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

strPreferedMeaningsLevelSelected = -1
strMeaningArray = "meanings"
strPreferedMeaningsSuffix = ""
iPreferedMeaningsCounter = -1
dicoPreferedMeaningsSelections = {}
listPreferedDone = []

def SelectPreferedMeaningsLevel(level):
    global strPreferedMeaningsLevelSelected
    global iPreferedMeaningsCounter
    global dicoPreferedMeaningsSelections
    strPreferedMeaningsLevelSelected = level
    iPreferedMeaningsCounter = -1
    dicoPreferedMeaningsSelections = {}
    DisplayNextPreferedMeaningsChoice()

def SelectPreferedMeaning(id, index, language):
    global dicoPreferedMeaningsSelections
    global listPreferedDone

    if(language in listPreferedDone):
        return

    if(index != 0):
        if(not(language in dicoPreferedMeaningsSelections)):
            dicoPreferedMeaningsSelections[language] = {}

        dicoPreferedMeaningsSelections[language][id] = index

    listPreferedDone.append(language)

    if(len(listPreferedDone) == 2):
        DisplayNextPreferedMeaningsChoice()

def DisplayNextPreferedMeaningsChoice():
    global strPreferedMeaningsLevelSelected
    global iPreferedMeaningsCounter
    global root
    global iExpectedReadingCount
    global strMeaningArray
    global strPreferedMeaningsSuffix
    global listSpecialToAdd
    global listPreferedDone

    iPreferedMeaningsCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    iCurrentPreferedMeanings = 0
    selectedEntry = None
    listPreferedDone = []

    dicoTempMeaningsTranslationsAndReplacements = {}

    for level in dicoOutput["MeaningsTranslations"]:
        for item in dicoOutput["MeaningsTranslations"][level]:
            dicoTempMeaningsTranslationsAndReplacements[int(item)] = dicoOutput["MeaningsTranslations"][level][item]

    dicoCustomKanaOnlySharedIds = {}

    for level in dicoOutput["KanaOnlySharedIds"]:
        for item in dicoOutput["KanaOnlySharedIds"][level]:
            dicoCustomKanaOnlySharedIds[item] = dicoOutput["KanaOnlySharedIds"][level][item]

    originalentry = None

    for entry in dicoCurrentLevels[strPreferedMeaningsLevelSelected]:
        sharedid = entry["sharedid"]

        if(str(sharedid) in dicoCustomKanaOnlySharedIds):
            sharedid = int(dicoCustomKanaOnlySharedIds[str(sharedid)])

        if(entry["type"] == strSelectedMeaningType):
            
            iExpectedReadingCount = 0
            bPreferedMeanings = False

            if(len(dicoItemPerId[sharedid][strMeaningArray]) > 1 or len(dicoItemPerId[sharedid]["meanings"]) > 1):
                bPreferedMeanings = True

            if(bPreferedMeanings):
                if(iCurrentPreferedMeanings != iPreferedMeaningsCounter):
                    iCurrentPreferedMeanings += 1
                else:
                    originalentry = entry
                    selectedEntry = dicoItemPerId[sharedid]
                    break

    if(selectedEntry == None):
        DoneWithPreferedMeaningsLevel()
        return

    dicoTempReorderedMeanings = {}

    for level in dicoOutput["PreferedMeanings"]:
        for kind in dicoOutput["PreferedMeanings"][level]:
            for id in dicoOutput["PreferedMeanings"][level][kind]:
                dicoTempReorderedMeanings[int(id)] = dicoOutput["PreferedMeanings"][level][kind][id]

    dicoTempReorderedMeaningsFr = {}

    for level in dicoOutput["PreferedMeaningsfr"]:
        for kind in dicoOutput["PreferedMeaningsfr"][level]:
            for id in dicoOutput["PreferedMeaningsfr"][level][kind]:
                dicoTempReorderedMeaningsFr[int(id)] = dicoOutput["PreferedMeaningsfr"][level][kind][id]

    button = tkinter.Button(root, text="Continue", command=lambda: DisplayNextPreferedMeaningsChoice())
    button.config(font=('Arial', FontSize))
    button.grid(column=0, row=0, columnspan=2)

    label = tkinter.Label(root, text=originalentry["display"], width=80)
    label.config(font=('Arial', int(FontSize * 1.5)))
    label.grid(column=0, row=1, columnspan=2)

    if(selectedEntry["display"] != originalentry["display"]):
        label = tkinter.Label(root, text=selectedEntry["display"], width=80)
        label.config(font=('Arial', int(FontSize * 1.5)))
        label.grid(column=0, row=2, columnspan=2)

    for iEnum, language in enumerate(["meanings", strMeaningArray]):

        othermeaningsuffix = strPreferedMeaningsSuffix

        if(othermeaningsuffix == ""):
            othermeaningsuffix = "en"

        iRow = 3
        iBlueIndex = 0

        if(language == "meanings" and selectedEntry["sharedid"] in dicoTempReorderedMeanings):
            iBlueIndex = dicoTempReorderedMeanings[selectedEntry["sharedid"]]

        if(language == "meanings_fr" and selectedEntry["sharedid"] in dicoTempReorderedMeaningsFr):
            iBlueIndex = dicoTempReorderedMeaningsFr[selectedEntry["sharedid"]]

        if(selectedEntry["sharedid"] in dicoTempMeaningsTranslationsAndReplacements):
            if(language == "meanings" and 
                "en" in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]] and 
                 "" in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]]["en"]):

                button = tkinter.Button(root, text=dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]]["en"][""], command=lambda id=selectedEntry["sharedid"], language = language: SelectPreferedMeaning(id, 0, language))
                button.config(font=('Arial', int(FontSize * 0.7)))
                button.grid(column=iEnum, row=iRow)
                button.config(bg="wheat1")
                iRow += 1
                iBlueIndex = -1

            if(language == "meanings_fr" and 
                "fr" in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]] and 
                 "" in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]]["fr"]):

                button = tkinter.Button(root, text=dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]]["fr"][""], command=lambda id=selectedEntry["sharedid"], language = language: SelectPreferedMeaning(id, 0, language))
                button.config(font=('Arial', int(FontSize * 0.7)))
                button.grid(column=iEnum, row=iRow)
                button.config(bg="wheat1")
                iRow += 1
                iBlueIndex = -1   

        for index, meaning in enumerate(selectedEntry[language]):
            if(selectedEntry["sharedid"] in dicoTempMeaningsTranslationsAndReplacements and
                othermeaningsuffix in dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]]):
                for othermeaning in  dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]][othermeaningsuffix]:
                    if(othermeaning.lower() == meaning.lower()):
                        meaning = dicoTempMeaningsTranslationsAndReplacements[selectedEntry["sharedid"]][othermeaningsuffix][othermeaning]
                        break
            
            button = tkinter.Button(root, text=meaning, command=lambda id=selectedEntry["sharedid"], index = index, language = language: SelectPreferedMeaning(id, index, language))
            button.config(font=('Arial', int(FontSize * 0.7)))
            button.grid(column=iEnum, row=iRow)
            iRow += 1

            if(iBlueIndex == index): 
                button.config(bg="LightBlue1")


def DoneWithPreferedMeaningsLevel():
    global dicoOutput
    global strSelectedMeaningType
    global dicoPreferedMeaningsSelections
    global strMeaningArray
    global strPreferedMeaningsSuffix

    if(not(str(strPreferedMeaningsLevelSelected)) in dicoOutput["PreferedMeanings" + strPreferedMeaningsSuffix]):
        dicoOutput["PreferedMeanings" + strPreferedMeaningsSuffix][str(strPreferedMeaningsLevelSelected)] = {}
        dicoOutput["PreferedMeanings" + strPreferedMeaningsSuffix][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType] = {}

    if(not(str(strPreferedMeaningsLevelSelected)) in dicoOutput["PreferedMeanings"]):
        dicoOutput["PreferedMeanings"][str(strPreferedMeaningsLevelSelected)] = {}
        dicoOutput["PreferedMeanings"][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType] = {}

    for language in dicoPreferedMeaningsSelections:
        if(language == "meanings"):
            dicoOutput["PreferedMeanings"][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType] = {}
            for item in dicoPreferedMeaningsSelections[language]:
                dicoOutput["PreferedMeanings"][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType][item] = dicoPreferedMeaningsSelections[language][item]

        elif(language == "meanings_fr"):
            dicoOutput["PreferedMeaningsfr"][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType] = {}
            for item in dicoPreferedMeaningsSelections[language]:
                dicoOutput["PreferedMeaningsfr"][str(strPreferedMeaningsLevelSelected)][strSelectedMeaningType][item] = dicoPreferedMeaningsSelections[language][item]

    if(strPreferedMeaningsSuffix == ""):
        if(strSelectedMeaningType == "kanji"):
            KanjiPreferedMeaningsSelection()
        elif(strSelectedMeaningType == "vocab_kana"):
            KanaOnlyPreferedMeaningsSelection()
        else:
            VocabPreferedMeaningsSelection()
    elif(strPreferedMeaningsSuffix == "fr"):
        if(strSelectedMeaningType == "kanji"):
            FRKanjiPreferedMeaningsSelection()
        elif(strSelectedMeaningType == "vocab_kana"):
            FRKanaOnlyPreferedMeaningsSelection()
        else:
            FRVocabPreferedMeaningsSelection()

###
###
### WHATEVER BLOCK
###
###

root = tkinter.Tk()

button = tkinter.Button(root, text="KanaOnly", command=KanaOnlySelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Vocabulary", command=VocabularySelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Fr Per Item Definition", command=FrMeaningTranslation)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Es Per Item Definition", command=EsMeaningTranslation)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Pt Per Item Definition", command=PtMeaningTranslation)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Kun reading picker", command=KunReadingSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Fr Kanji meaning picker", command=FRKanjiPreferedMeaningsSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Fr Kana Only meaning picker", command=FRKanaOnlyPreferedMeaningsSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Fr Vocabulary meaning picker", command=FRVocabPreferedMeaningsSelection)
button.pack()
button.config(font=('Arial', FontSize))
root.mainloop()

json.dump(dicoOutput, open("../.src/Selected.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

listKanjis = [[], [], [], [], [], [], [], []]

for i in range(1, 9):
    with open("../.sources/jouyoukanji/" + str(i) + ".txt", encoding="utf-8") as kanjis:
        for line in kanjis.readlines():
            listKanjis[i - 1].extend(line.split(" "))

dicoSelected = json.load(open("../.src/Selected.json", "r", encoding="utf-8"))

dicoOutput = {}

for i in range(1,101):
    dicoOutput[i] = []

dicoOutput["special"] = []

setValidKanaOnlyId = set()
setSpecialKanaOnlyIds = set()
setValidVocabularySharedId = set()

for level in dicoSelected["SelectedKanaOnly"]:
    for item in dicoSelected["SelectedKanaOnly"][level]:
        setValidKanaOnlyId.add(item)
        if(item in dicoItemPerId and dicoItemPerId[item]["id"] != dicoItemPerId[item]["sharedid"]):
            setValidVocabularySharedId.add(dicoItemPerId[item]["sharedid"])

for level in dicoSelected["SelectedVocab"]:
    for item in dicoSelected["SelectedVocab"][level]:
        setValidVocabularySharedId.add(item)

for item in listSpecialToAdd:
    if(item in dicoItemPerId):
        if(dicoItemPerId[item]["type"] == "vocab"):
            setValidVocabularySharedId.add(dicoItemPerId[item]["sharedid"])
        elif(dicoItemPerId[item]["type"] == "vocab_kana"):
            setValidKanaOnlyId.add(dicoItemPerId[item]["id"])
            setSpecialKanaOnlyIds.add(dicoItemPerId[item]["id"])

dicoKanaOnlySharedIds = {}

for level in dicoSelected["KanaOnlySharedIds"]:
    for item in dicoSelected["KanaOnlySharedIds"][level]:
        dicoKanaOnlySharedIds[int(item)] = int(dicoSelected["KanaOnlySharedIds"][level][item])
        setValidVocabularySharedId.add(dicoKanaOnlySharedIds[int(item)])

for id in list(setValidVocabularySharedId):
    if(id in dicoItemPerId):
        setValidVocabularySharedId.add(dicoItemPerId[id]["sharedid"])

dicoKunReadingReplacements = {}

for level in dicoSelected["KunReadingSelections"]:
    for item in dicoSelected["KunReadingSelections"][level]:
        dicoKunReadingReplacements[int(item)] = dicoSelected["KunReadingSelections"][level][item]

dicoMeaningsTranslationsAndReplacements = {}

for level in dicoSelected["MeaningsTranslations"]:
    for item in dicoSelected["MeaningsTranslations"][level]:
        dicoMeaningsTranslationsAndReplacements[int(item)] = dicoSelected["MeaningsTranslations"][level][item]

dicoReorderedMeanings = {}

for level in dicoSelected["PreferedMeanings"]:
    for kind in dicoSelected["PreferedMeanings"][level]:
        for id in dicoSelected["PreferedMeanings"][level][kind]:
            dicoReorderedMeanings[int(id)] = dicoSelected["PreferedMeanings"][level][kind][id]

dicoReorderedMeaningsFr = {}

for level in dicoSelected["PreferedMeaningsfr"]:
    for kind in dicoSelected["PreferedMeaningsfr"][level]:
        for id in dicoSelected["PreferedMeaningsfr"][level][kind]:
            dicoReorderedMeaningsFr[int(id)] = dicoSelected["PreferedMeaningsfr"][level][kind][id]

for level in listInput:
    for item in level:
        if(item["type"] == "vocab_kana" and item["id"] in dicoKanaOnlySharedIds):
            item["sharedid"] = dicoKanaOnlySharedIds[item["id"]]
            item["meanings"] = []
            item["meanings_fr"] = []
            item["meanings_es"] = []
            item["meanings_pt"] = []

        for dicoReorder, meaningstring in [(dicoReorderedMeanings, "meanings"), (dicoReorderedMeaningsFr, "meanings_fr")]:

            if(item["id"] == item["sharedid"] and item["sharedid"] in dicoReorder):
                if(dicoReorder[item["sharedid"]] < len(item[meaningstring])):
                    tempmeaning = item[meaningstring][dicoReorder[item["sharedid"]]]
                    del item[meaningstring][dicoReorder[item["sharedid"]]]
                    item[meaningstring].insert(0, tempmeaning)
                else:
                    print("Wrong index for", item["display"])

for inputlevel in listInput:
    for item in inputlevel:

        if(item["id"] in dicoMeaningsTranslationsAndReplacements):
            for lang in dicoMeaningsTranslationsAndReplacements[item["id"]]:
                meaninglistname = "meanings"
                if(lang != "en"):
                    meaninglistname += "_" + lang

                for iMeaning, meaning in enumerate(item[meaninglistname]):
                    for othermeaning in dicoMeaningsTranslationsAndReplacements[item["id"]][lang]:
                        if(othermeaning.lower() == meaning.lower()):
                            item[meaninglistname][iMeaning] = dicoMeaningsTranslationsAndReplacements[item["id"]][lang][othermeaning]
                    
                if("" in dicoMeaningsTranslationsAndReplacements[item["id"]][lang]):
                    item[meaninglistname].insert(0, dicoMeaningsTranslationsAndReplacements[item["id"]][lang][""])

        if(item["type"] == "kanji"):
            newreadinglist = []

            for reading in item["kun_readings"]:
                if(item["id"] in dicoKunReadingReplacements and reading in dicoKunReadingReplacements[item["id"]]):
                    readingadjusted = dicoKunReadingReplacements[item["id"]][reading].replace(" ", "").replace("-", "")
                    if(not(readingadjusted in newreadinglist)):
                        newreadinglist.append(readingadjusted)
                else:
                    readingadjusted = reading.replace(" ", "").replace("-", "")
                    if(not(readingadjusted in newreadinglist)):
                        newreadinglist.append(readingadjusted)
            
            item["kun_readings"] = newreadinglist

listValidKanaOnly = []
listValidVocabulary = []

dicoVocabPerKanji = {}

for level in listInput:
    for item in level:

        if(item["type"] == "vocab_kana" and item["id"] in setValidKanaOnlyId):
            listValidKanaOnly.append(item)
        elif(item["type"] == "vocab" and 
                item["sharedid"] in setValidVocabularySharedId and 
                not("〇" in item["display"] and 
                not(item["id"] == item["sharedid"])) and
                not("一一" in item["display"])):
            listValidVocabulary.append(item)
        elif(item["type"] == "kanji"):
            dicoVocabPerKanji[item["display"]] = 0

for vocab in listValidVocabulary:
    for char in vocab["display"]:
        if(char in dicoVocabPerKanji):
            dicoVocabPerKanji[char] += 1

listTempKanji1 = []
listTempKanji2 = []
listTempKanji3 = []

for level in listInput:
    for item in level:
        if(item["type"] == "kanji"):
            if(dicoVocabPerKanji[item["display"]] > 0):
                bFoundInList = False

                for i in range(1, 9):
                    if(item["display"] in listKanjis[i - 1]):
                        if(i < 7):
                            listTempKanji1.append(item)
                        else:
                            listTempKanji2.append(item)
                        bFoundInList = True
                        break

                if(not(bFoundInList)):
                    listTempKanji3.append(item)

listValidKanjis = []
listValidKanjis.extend(listTempKanji1)
listValidKanjis.extend(listTempKanji2)
listValidKanjis.extend(listTempKanji3)

dicoMinLevelForKanji = {}
iCurrentKanjiLevel = 1
iCurrentKanjiInLevel = 0

for kanji in listValidKanjis:
    dicoMinLevelForKanji[kanji["display"]] = iCurrentKanjiLevel
    iCurrentKanjiInLevel += 1

    if(iCurrentKanjiLevel <= 20):
        if(iCurrentKanjiInLevel >= 15):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel <= 40):
        if(iCurrentKanjiInLevel >= 17):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel <= 60):
        if(iCurrentKanjiInLevel >= 20):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel <= 80):
        if(iCurrentKanjiInLevel >= 23):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel <= 90):
        if(iCurrentKanjiInLevel >= 25):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel <= 95):
        if(iCurrentKanjiInLevel >= 35):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

    elif(iCurrentKanjiLevel > 95):
        if(iCurrentKanjiInLevel >= 45):
            iCurrentKanjiLevel += 1
            iCurrentKanjiInLevel = 0

dicoMinLevelForVocab = {}

for vocab in listValidVocabulary:
    minlevel = 1

    bFoundKanji = False

    for char in vocab["display"]:
        if(char in dicoMinLevelForKanji and dicoMinLevelForKanji[char] >= minlevel):
            minlevel = dicoMinLevelForKanji[char]
            bFoundKanji = True

    if(not(bFoundKanji)):
        minlevel = 101

    dicoMinLevelForVocab[vocab["id"]] = minlevel

    if(minlevel > 100):
        dicoOutput["special"].append(vocab)

setAddedKanaOnly = set()

for iLevel in dicoOutput:

    if(not(type(iLevel) is int)):
        continue

    level = dicoOutput[iLevel]

    for kanji in listValidKanjis:
        if(dicoMinLevelForKanji[kanji["display"]] == iLevel):
            level.append(kanji)

    if((iLevel - 1) * 10 < len(listValidKanaOnly)):
        sublist = listValidKanaOnly[(iLevel-1)  * 10: min(iLevel * 10, len(listValidKanaOnly))]
        level.extend(sublist)
        for item in sublist:
            setAddedKanaOnly.add(item["id"])

    for vocab in listValidVocabulary:
        if(dicoMinLevelForVocab[vocab["id"]] == iLevel):
            level.append(vocab)

for item in listValidKanaOnly:
    if(item["id"] in setSpecialKanaOnlyIds and not(item["id"] in setAddedKanaOnly)):
        dicoOutput["special"].append(item)

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]

    for item in level:
        while(None in item["readings"]):
            print("r", item["display"])
            item["readings"].remove(None)
        while(None in item["meanings"]):
            print("en", item["display"])
            item["meanings"].remove(None)
        while(None in item["meanings_fr"]):
            print("fr", item["display"])
            item["meanings_fr"].remove(None)
        while(None in item["meanings_es"]):
            print("es", item["display"])
            item["meanings_es"].remove(None)
        while(None in item["meanings_pt"]):
            print("pt", item["display"])
            item["meanings_pt"].remove(None)

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]
    for item in level:
        for meaninglist in ["meanings", "meanings_fr", "meanings_es", "meanings_pt"]:
            for i, meaning in enumerate(item[meaninglist]):
                while(meaning[0] == ' '):
                    meaning = meaning[1:]

                while(meaning[-1] == ' '):
                    meaning = meaning[:-1]

                if(meaning[0] == "(" and meaning[-1] == ")" and meaning.count("(") == 1 and meaning.count(")") == 1):
                    meaning = meaning[1:-1]

                if(meaning[0] == "("):
                    if(not(")" in meaning)):
                        meaning = meaning[1].upper() + meaning[2:]
                    else:
                        indexfirst = meaning.index(")") + 1

                        while(meaning[indexfirst] == " "):
                            indexfirst += 1

                        meaning = meaning[:indexfirst] + meaning[indexfirst].upper() + meaning[indexfirst + 1:]
                else:
                    meaning = meaning[0].upper() + meaning[1:]

                item[meaninglist][i] = meaning

    for item in level:
        for meaninglist in ["meanings", "meanings_fr", "meanings_es", "meanings_pt"]:
            item[meaninglist] = list(dict.fromkeys(item[meaninglist]))

iNumeralCount = 0

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]
    for item in level:
        for meaninglist in ["meanings", "meanings_fr", "meanings_es", "meanings_pt"]:
            for i, meaning in enumerate(item[meaninglist]):

                bHasNumeral = True

                for char in meaning:
                    if(not(char in string.digits) and char != "." and char != "%" and char != ","):
                        bHasNumeral = False
                        break

                if(i == 0 and bHasNumeral):
                    print(meaning, item["id"], meaninglist, len(item[meaninglist]), item[meaninglist][1])
                    iNumeralCount += 1

                    if(len(item[meaninglist]) > 1):
                        del item[meaninglist][0]
                        break

dicoSharedIdLevels = {}
dicoKanjiPerLevel = {}
dicoSharedPerLevel = {}
dicoReceivingLevel = {}
dicoMoveBackLevel = {}

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]

    iKanjiCount = 0
    setshared = set()

    for item in level:
        setshared.add(item["sharedid"])

        if(item["type"] == "kanji"):
            iKanjiCount += 1

        if(not(item["sharedid"] in dicoSharedIdLevels)):
            dicoSharedIdLevels[item["sharedid"]] = []

        dicoSharedIdLevels[item["sharedid"]].append(iLevel)

    dicoKanjiPerLevel[iLevel] = iKanjiCount
    dicoSharedPerLevel[iLevel] = len(setshared)
    dicoReceivingLevel[iLevel] = 0
    dicoMoveBackLevel[iLevel] = 0

for iLevel in dicoOutput:
    if(iLevel == "special"):
        continue

    level = dicoOutput[iLevel]

    indextodelete = set()

    if(dicoSharedPerLevel[iLevel] > dicoKanjiPerLevel[iLevel] * 8):
        for iItem, item in enumerate(level):
            for otherlevel in dicoSharedIdLevels[item["sharedid"]]:
                if(otherlevel != "special" and int(otherlevel) > int(iLevel) and int(otherlevel) - int(iLevel) < 10 and dicoSharedPerLevel[otherlevel] < dicoKanjiPerLevel[otherlevel] * 8):
                    dicoMoveBackLevel[iLevel] += 1
                    dicoReceivingLevel[otherlevel] += 1
                    dicoOutput[otherlevel].insert(0, item)
                    indextodelete.add(iItem)
                    break

    for i in range(len(level) - 1, -1, -1):
        if(i in indextodelete):
            del level[i]

dicoTargetCount = {
    1 : 120,
    2 : 130,
    3 : 130, 
    4 : 130, 
    5 : 130, 
    6 : 140, 
}

for iLevel in dicoOutput:
    if(iLevel == "special"):
        continue        

    level = dicoOutput[iLevel]

    if(iLevel in dicoTargetCount):
        if(len(level) > dicoTargetCount[iLevel]):
            todisseminate = level[dicoTargetCount[iLevel]:]
            dicoOutput[iLevel] = level[:dicoTargetCount[iLevel]]
            
            for otherlevelid in dicoOutput:
                if(len(todisseminate) == 0):
                    break

                if(otherlevelid == "special" or int(otherlevelid) <= int(iLevel)):
                    continue  

                otherlevel = dicoOutput[otherlevelid]
                sizetoadd = min(dicoKanjiPerLevel[otherlevelid] * 10 - len(otherlevel), len(todisseminate))

                if(sizetoadd > 0):
                    dicoOutput[otherlevelid] = todisseminate[:sizetoadd] + dicoOutput[otherlevelid]
                    todisseminate = todisseminate[sizetoadd:]

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]

    for item in level:
        for iReading, reading in enumerate(item["readings"]):
            item["readings"][iReading] = reading.replace("-", "")

setCharacters = set()

for iLevel in dicoOutput:
    level = dicoOutput[iLevel]

    for item in level:
        for char in item["display"]:
            setCharacters.add(char)

        for meaning in item["meanings"]:
            for char in meaning:
                setCharacters.add(char)

        for meaning in item["meanings_fr"]:
            for char in meaning:
                setCharacters.add(char)

        for meaning in item["meanings_es"]:
            for char in meaning:
                setCharacters.add(char)

        for meaning in item["meanings_pt"]:
            for char in meaning:
                setCharacters.add(char)

        for reading in item["readings"]:
            for char in reading:
                setCharacters.add(char)

        for reading in item["kun_readings"]:
            for char in reading:
                setCharacters.add(char)

with open("../.temp/Characters.txt", "w") as fileCharacters:
    for char in setCharacters:
        fileCharacters.write(hex(ord(char))[2:] + ",")

for iLevel in dicoOutput:
    print(iLevel, len(dicoOutput[iLevel]), dicoSharedPerLevel[iLevel], dicoMoveBackLevel[iLevel], dicoReceivingLevel[iLevel])

print("Numerals", iNumeralCount)

dicoMeaningsTranslationsAndReplacements = {}

for level in dicoSelected["MeaningsTranslations"]:
    for item in dicoSelected["MeaningsTranslations"][level]:
        if(not(int(item) in dicoMeaningsTranslationsAndReplacements)):
            dicoMeaningsTranslationsAndReplacements[int(item)] = dicoSelected["MeaningsTranslations"][level][item]
        elif(dicoSelected["MeaningsTranslations"][level][item] != dicoMeaningsTranslationsAndReplacements[int(item)]):
            print("Multiple meanings for", item)

iItemCount = 0
iKanjiCount = 0
iVocabKanaCount = 0
iVocabCount = 0

iItemCountFr = 0
iKanjiCountFr = 0
iVocabKanaCountFr = 0
iVocabCountFr = 0

iItemCountEs = 0
iKanjiCountEs = 0
iVocabKanaCountEs = 0
iVocabCountEs = 0

iItemCountPt = 0
iKanjiCountPt = 0
iVocabKanaCountPt = 0
iVocabCountPt = 0

iOneMeaningShare = 0

setMissingLevelFr = set()
setMissingLevelEs = set()
setMissingLevelPt = set()

for iLevel in dicoOutput:
    bMissingLevelFr = False
    bMissingLevelEs = False
    bMissingLevelPt = False

    for item in dicoOutput[iLevel]:
        if(item["id"] != item["sharedid"]):
            continue

        if(item["type"] == "kanji"):
            iKanjiCount += 1
            if(len(item["meanings_fr"]) > 0):
                iKanjiCountFr += 1
            if(len(item["meanings_es"]) > 0):
                iKanjiCountEs += 1
            if(len(item["meanings_pt"]) > 0):
                iKanjiCountPt += 1
        elif(item["type"] == "vocab_kana"):
            iVocabKanaCount += 1
            if(len(item["meanings_fr"]) > 0):
                iVocabKanaCountFr += 1
            if(len(item["meanings_es"]) > 0):
                iVocabKanaCountEs += 1
            if(len(item["meanings_pt"]) > 0):
                iVocabKanaCountPt += 1
        elif(item["type"] == "vocab"):
            iVocabCount += 1
            if(len(item["meanings_fr"]) > 0):
                iVocabCountFr += 1
            if(len(item["meanings_es"]) > 0):
                iVocabCountEs += 1
            if(len(item["meanings_pt"]) > 0):
                iVocabCountPt += 1

        iItemCount += 1
        if(len(item["meanings_fr"]) > 0):
            iItemCountFr += 1
        else:
            bMissingLevelFr = True

        if(len(item["meanings_es"]) > 0):
            iItemCountEs += 1
        else:
            bMissingLevelEs = True

        if(len(item["meanings_pt"]) > 0):
            iItemCountPt += 1
        else:
            bMissingLevelPt = True

        if(len(item["meanings"]) == 1):
            iOneMeaningShare += 1

    if(bMissingLevelFr):
        setMissingLevelFr.add(iLevel)

    if(bMissingLevelEs):
        setMissingLevelEs.add(iLevel)

    if(bMissingLevelPt):
        setMissingLevelPt.add(iLevel)

print("ItemFr", iItemCountFr, iItemCount, iItemCountFr/iItemCount*100, "%")
print("KanjiFr", iKanjiCountFr, iKanjiCount, iKanjiCountFr/iKanjiCount*100, "%")
print("VocabKanaFr", iVocabKanaCountFr, iVocabKanaCount, iVocabKanaCountFr/iVocabKanaCount*100, "%")
print("VocabFr", iVocabCountFr, iVocabCount, iVocabCountFr/iVocabCount*100, "%")
print("MissingLevelFr", setMissingLevelFr)

print(" ")

print("ItemEs", iItemCountEs, iItemCount, iItemCountEs/iItemCount*100, "%")
print("KanjiEs", iKanjiCountEs, iKanjiCount, iKanjiCountEs/iKanjiCount*100, "%")
print("VocabKanaEs", iVocabKanaCountEs, iVocabKanaCount, iVocabKanaCountEs/iVocabKanaCount*100, "%")
print("VocabEs", iVocabCountEs, iVocabCount, iVocabCountEs/iVocabCount*100, "%")
print("MissingLevelEs", setMissingLevelEs)

print(" ")

print("ItemPt", iItemCountPt, iItemCount, iItemCountPt/iItemCount*100, "%")
print("KanjiPt", iKanjiCountPt, iKanjiCount, iKanjiCountPt/iKanjiCount*100, "%")
print("VocabKanaPt", iVocabKanaCountPt, iVocabKanaCount, iVocabKanaCountPt/iVocabKanaCount*100, "%")
print("VocabPt", iVocabCountPt, iVocabCount, iVocabCountPt/iVocabCount*100, "%")
print("MissingLevelPt", setMissingLevelPt)

print(" ")

print("OneMeaning", iOneMeaningShare, iItemCount, iOneMeaningShare/iItemCount*100, "%")

json.dump(dicoOutput, open("../Output/Levels.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


