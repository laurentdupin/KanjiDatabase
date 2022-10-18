import tkinter
import os
import json
import Tooltip
import pyperclip
import copy
from googletrans import Translator

#Need to do pip install googletrans==3.1.0a0 for it to work
translator = Translator()

FontSize = 30

if(not(os.path.exists("../.temp/Levels.json"))):
    print("No .temp/Levels.json found")
    exit(1)

if(not(os.path.exists("../output/Levels.json"))):
    print("No output/Levels.json found")
    exit(1)

listInput = json.load(open("../.temp/Levels.json", "r", encoding="utf-8"))
dicoCurrentLevels = json.load(open("../output/Levels.json", "r", encoding="utf-8"))

dicoItemPerId = {}
dicoItemPerIdCurrent = {}

for level in listInput:
    for item in level:
        dicoItemPerId[item["id"]] = item

for level in dicoCurrentLevels:
    for item in dicoCurrentLevels[level]:
        dicoItemPerIdCurrent[item["id"]] = item

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

        langisdone = False

        if(level in dicoOutput["MeaningsTranslations"]):
            for item in dicoOutput["MeaningsTranslations"][level]:
                if(meaningtranslationlang in dicoOutput["MeaningsTranslations"][level][item]):
                    langisdone = True
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

def DisplayNextMeanings():
    global strMeaningTranslationLevelSelected
    global iMeaningTranslationCounter
    global root
    global dicoMeaningEntries
    global dicoOutput
    global translator
    global meaningtranslationlang

    iMeaningTranslationCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    selectedEntry = None

    iCurrentMeanings = 0

    for iPosition, entry in enumerate(dicoCurrentLevels[strMeaningTranslationLevelSelected]):
        if(iCurrentMeanings == iMeaningTranslationCounter):
            selectedEntry = entry
            break
        else:
            iCurrentMeanings += 1

    if(selectedEntry == None):
        DoneWithMeaningTranslationLevel()
        return

    originalentry = selectedEntry

    print(iPosition, len(dicoCurrentLevels[strMeaningTranslationLevelSelected]))

    if(selectedEntry["id"] != selectedEntry["sharedid"]):
        selectedEntry = dicoItemPerIdCurrent[selectedEntry["sharedid"]]

    dicoMeaningEntries = {}

    label = tkinter.Label(root, text=originalentry["display"], width=80)
    label.config(font=('Arial', FontSize))
    label.grid(row=0, column=0, columnspan=8)

    button = tkinter.Button(root, text="Next Empty", command=lambda id=selectedEntry["id"] : SearchNextEmpty(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=0)

    button = tkinter.Button(root, text="Continue", command=lambda id=selectedEntry["id"] : ContinueToNextMeaning(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=1, columnspan=7)

    dicoTranslations = {}

    try:
        translations = translator.translate(selectedEntry["meanings"][0:5], src='en', dest=meaningtranslationlang)
        for translation in translations:
            dicoTranslations[translation.origin] = translation.text
    except:
        pass

    listAddedMeanings = []

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

        for meaning in selectedEntry[meaningname]:
            if(meaning in listAddedMeanings):
                continue

            listAddedMeanings.append(meaning)

            labeltext = meaning

            label = tkinter.Label(root, text=labeltext)
            label.config(font=('Arial', int(FontSize * 0.3)))
            label.grid(row=iCurrentRow, column=2 * iLang)

            entry = tkinter.Entry(root)
            entry.config(font=('Arial', int(FontSize * 0.3)))
            entry.grid(row=iCurrentRow, column=2 * iLang + 1)
            dicoMeaningEntries[language][meaning] = entry

            if(language == "en" and meaning in dicoTranslations):
                translation = dicoTranslations[meaning]
                button = tkinter.Button(root, text=translation, command=lambda text=translation : pyperclip.copy(text))
                button.config(font=('Arial', int(FontSize * 0.3)))
                button.grid(row=iCurrentRow + 1, column=2 * iLang)

            iCurrentRow += 2

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.3)))
        entry.grid(row=iCurrentRow, column=2 * iLang + 1)
        dicoMeaningEntries[language][""]= entry

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
    strSelectedMeaningType = "kanji"
    PreferedMeaningsSelection()

def KanaOnlyPreferedMeaningsSelection():
    global strSelectedMeaningType
    strSelectedMeaningType = "vocab_kana"
    PreferedMeaningsSelection()

def VocabPreferedMeaningsSelection():
    global strSelectedMeaningType
    strSelectedMeaningType = "vocab"
    PreferedMeaningsSelection()

def PreferedMeaningsSelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectPreferedMeaningsLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if(str(iLevel) in dicoOutput["PreferedMeanings"] and strSelectedMeaningType in dicoOutput["PreferedMeanings"][str(iLevel)]):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

iPreferedMeaningsLevelSelected = -1
iPreferedMeaningsCounter = -1
dicoPreferedMeaningsSelections = {}

def SelectPreferedMeaningsLevel(level):
    global iPreferedMeaningsLevelSelected
    global iPreferedMeaningsCounter
    global dicoPreferedMeaningsSelections
    iPreferedMeaningsLevelSelected = level
    iPreferedMeaningsCounter = -1
    dicoPreferedMeaningsSelections = {}
    DisplayNextPreferedMeaningsChoice()

def SelectPreferedMeaning(id, index):
    global dicoPreferedMeaningsSelections

    if(index != 0):
        dicoPreferedMeaningsSelections[id] = index

    DisplayNextPreferedMeaningsChoice()

def DisplayNextPreferedMeaningsChoice():
    global iPreferedMeaningsLevelSelected
    global iPreferedMeaningsCounter
    global root
    global iExpectedReadingCount

    iPreferedMeaningsCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    iCurrentPreferedMeanings = 0
    selectedEntry = None

    setTempValidSharedIds = set()

    for level in dicoOutput["SelectedKanaOnly"]:
        for item in dicoOutput["SelectedKanaOnly"][level]:
            setTempValidSharedIds.add(item)

    for level in dicoOutput["SelectedVocab"]:
        for item in dicoOutput["SelectedVocab"][level]:
            setTempValidSharedIds.add(item)

    dicoCustomKanaOnlySharedIds = {}

    for level in dicoOutput["KanaOnlySharedIds"]:
        for item in dicoOutput["KanaOnlySharedIds"][level]:
            dicoCustomKanaOnlySharedIds[item] = dicoOutput["KanaOnlySharedIds"][level][item]

    for entry in listInput[iPreferedMeaningsLevelSelected]:
        sharedid = entry["sharedid"]

        if(str(sharedid) in dicoCustomKanaOnlySharedIds):
            sharedid = int(dicoCustomKanaOnlySharedIds[str(sharedid)])

        if(entry["type"] != "kanji" and not(sharedid in setTempValidSharedIds)):
            continue

        if(entry["type"] == strSelectedMeaningType):
            
            iExpectedReadingCount = 0
            bPreferedMeanings = False

            if(len(entry["meanings"]) > 1):
                bPreferedMeanings = True

            if(bPreferedMeanings):
                if(iCurrentPreferedMeanings != iPreferedMeaningsCounter):
                    iCurrentPreferedMeanings += 1
                else:
                    selectedEntry = dicoItemPerId[sharedid]
                    break

    if(selectedEntry == None):
        DoneWithPreferedMeaningsLevel()
        return

    label = tkinter.Label(root, text=selectedEntry["display"], width=80)
    label.config(font=('Arial', FontSize))
    label.pack()

    for index, meaning in enumerate(selectedEntry["meanings"]):
        button = tkinter.Button(root, text=meaning, command=lambda id=selectedEntry["sharedid"], index = index: SelectPreferedMeaning(id, index))
        button.config(font=('Arial', int(FontSize * 0.7)))
        button.pack()

def DoneWithPreferedMeaningsLevel():
    global dicoOutput
    global strSelectedMeaningType
    global dicoPreferedMeaningsSelections

    if(not(str(iPreferedMeaningsLevelSelected)) in dicoOutput["PreferedMeanings"]):
        dicoOutput["PreferedMeanings"][str(iPreferedMeaningsLevelSelected)] = {}

    dicoOutput["PreferedMeanings"][str(iPreferedMeaningsLevelSelected)][strSelectedMeaningType] = dicoPreferedMeaningsSelections
    
    if(strSelectedMeaningType == "kanji"):
        KanjiPreferedMeaningsSelection()
    elif(strSelectedMeaningType == "vocab_kana"):
        KanaOnlyPreferedMeaningsSelection()
    else:
        VocabPreferedMeaningsSelection()

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
button = tkinter.Button(root, text="Kanji meaning picker", command=KanjiPreferedMeaningsSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Kana Only meaning picker", command=KanaOnlyPreferedMeaningsSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Vocabulary meaning picker", command=VocabPreferedMeaningsSelection)
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
setValidVocabularySharedId = set()

for level in dicoSelected["SelectedKanaOnly"]:
    for item in dicoSelected["SelectedKanaOnly"][level]:
        setValidKanaOnlyId.add(item)
        if(dicoItemPerId[item]["id"] != dicoItemPerId[item]["sharedid"]):
            setValidVocabularySharedId.add(dicoItemPerId[item]["sharedid"])

for level in dicoSelected["SelectedVocab"]:
    for item in dicoSelected["SelectedVocab"][level]:
        setValidVocabularySharedId.add(item)


dicoKanaOnlySharedIds = {}

for level in dicoSelected["KanaOnlySharedIds"]:
    for item in dicoSelected["KanaOnlySharedIds"][level]:
        dicoKanaOnlySharedIds[int(item)] = int(dicoSelected["KanaOnlySharedIds"][level][item])
        setValidVocabularySharedId.add(dicoKanaOnlySharedIds[int(item)])

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

for level in listInput:
    for item in level:
        if(item["type"] == "vocab_kana" and item["id"] in dicoKanaOnlySharedIds):
            item["sharedid"] = dicoKanaOnlySharedIds[item["id"]]
            item["meanings"] = []
            item["meanings_fr"] = []
            item["meanings_es"] = []
            item["meanings_pt"] = []

        if(item["id"] == item["sharedid"] and item["sharedid"] in dicoReorderedMeanings):
            tempmeaning = item["meanings"][dicoReorderedMeanings[item["sharedid"]]]
            del item["meanings"][dicoReorderedMeanings[item["sharedid"]]]
            item["meanings"].insert(0, tempmeaning)

for inputlevel in listInput:
    for item in inputlevel:

        if(item["id"] in dicoMeaningsTranslationsAndReplacements):
            for lang in dicoMeaningsTranslationsAndReplacements[item["id"]]:
                meaninglistname = "meanings"
                if(lang != "en"):
                    meaninglistname += "_" + lang

                for iMeaning, meaning in enumerate(item[meaninglistname]):
                    if(meaning in dicoMeaningsTranslationsAndReplacements[item["id"]][lang]):
                        item[meaninglistname][iMeaning] = dicoMeaningsTranslationsAndReplacements[item["id"]][lang][meaning]
                    
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
        elif(item["type"] == "vocab" and item["sharedid"] in setValidVocabularySharedId and not("〇" in item["display"] and not(item["id"] == item["sharedid"]))):
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

    for char in vocab["display"]:
        if(char in dicoMinLevelForKanji and dicoMinLevelForKanji[char] > minlevel):
            minlevel = dicoMinLevelForKanji[char]

    dicoMinLevelForVocab[vocab["id"]] = minlevel

    if(minlevel > 100):
        dicoOutput["special"].append(vocab)

for iLevel in dicoOutput:

    if(not(type(iLevel) is int)):
        continue

    level = dicoOutput[iLevel]

    for kanji in listValidKanjis:
        if(dicoMinLevelForKanji[kanji["display"]] == iLevel):
            level.append(kanji)

    if((iLevel - 1) * 10 < len(listValidKanaOnly)):
        level.extend(listValidKanaOnly[(iLevel-1)  * 10: min(iLevel * 10, len(listValidKanaOnly))])

    for vocab in listValidVocabulary:
        if(dicoMinLevelForVocab[vocab["id"]] == iLevel):
            level.append(vocab)

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

    print(iLevel, len(level))

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


