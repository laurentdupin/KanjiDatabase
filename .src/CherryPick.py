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
    print("No Levels.json found")
    exit(1)

listInput = json.load(open("../.temp/Levels.json", "r", encoding="utf-8"))

dicoItemPerId = {}

for level in listInput:
    for item in level:
        dicoItemPerId[item["id"]] = item

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

def MeaningTranslationSelection():
    global root
    global dicoOutput
    for child in root.winfo_children():
        child.destroy()
    
    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectMeaningTranslation(level))
        button.grid(column=iLevel%10, row = iLevel//10)

        if(str(iLevel) in dicoOutput["MeaningsTranslations"]):
            button.config(bg="LightBlue1")

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

iMeaningTranslationLevelSelected = -1
iMeaningTranslationCounter = -1
dicoMeaningsTranslations = {}
setAlreadyDoneInThisLevel = set()
bSearchNextEmpty = False

def SelectMeaningTranslation(level):
    global iMeaningTranslationLevelSelected
    global iMeaningTranslationCounter
    global dicoMeaningsTranslations
    global setAlreadyDoneInThisLevel
    global bShouldTranslate
    global bSearchNextEmpty
    iMeaningTranslationLevelSelected = level
    iMeaningTranslationCounter = -1
    dicoMeaningsTranslations = {}
    setAlreadyDoneInThisLevel = set()
    bShouldTranslate.set(1)
    bSearchNextEmpty = False
    DisplayNextMeanings()

dicoMeaningEntries = {}

def SearchNextEmpty(id):
    global bSearchNextEmpty
    bSearchNextEmpty = True
    ContinueToNextMeaning(id)

def ContinueToNextMeaning(id):
    id = str(id)
    global dicoMeaningEntries

    for meaning in dicoMeaningEntries:
        for lang in dicoMeaningEntries[meaning]:
            if(dicoMeaningEntries[meaning][lang].get() != ""):
                if(not(id in dicoMeaningsTranslations)):
                    dicoMeaningsTranslations[id] = {}
                if(not(meaning in dicoMeaningsTranslations[id])):
                    dicoMeaningsTranslations[id][meaning] = {}
                dicoMeaningsTranslations[id][meaning][lang] = dicoMeaningEntries[meaning][lang].get()

    DisplayNextMeanings()

def ChangeEntryContent(entry, text):
    entry.delete(0, tkinter.END)
    entry.insert(0, text)

def DisplayNextMeanings():
    global iMeaningTranslationLevelSelected
    global iMeaningTranslationCounter
    global root
    global dicoMeaningEntries
    global dicoOutput
    global translator
    global setAlreadyDoneInThisLevel
    global bShouldTranslate
    global bSearchNextEmpty

    iMeaningTranslationCounter += 1

    for child in root.winfo_children():
        child.destroy()
    
    selectedEntry = None

    iCurrentMeanings = 0

    dicoTempKanaOnlySharedIds = {}

    for level in dicoOutput["KanaOnlySharedIds"]:
        for item in dicoOutput["KanaOnlySharedIds"][level]:
            dicoTempKanaOnlySharedIds[int(item)] = int(dicoOutput["KanaOnlySharedIds"][level][item])

    for iPosition, entry in enumerate(listInput[iMeaningTranslationLevelSelected]):
        setTempValidKanaOnlyId = set()
        setTempValidVocabularySharedId = set()

        for level in dicoOutput["SelectedKanaOnly"]:
            for item in dicoOutput["SelectedKanaOnly"][level]:
                setTempValidKanaOnlyId.add(item)
                if(dicoItemPerId[item]["id"] != dicoItemPerId[item]["sharedid"]):
                    setTempValidVocabularySharedId.add(dicoItemPerId[item]["sharedid"])

        for level in dicoOutput["SelectedVocab"]:
            for item in dicoOutput["SelectedVocab"][level]:
                setTempValidVocabularySharedId.add(item)

        for level in dicoSelected["KanaOnlySharedIds"]:
            for item in dicoSelected["KanaOnlySharedIds"][level]:
                setTempValidVocabularySharedId.add(int(dicoSelected["KanaOnlySharedIds"][level][item]))

        if(entry["id"] in setTempValidKanaOnlyId or entry["sharedid"] in setTempValidVocabularySharedId or entry["type"] == "kanji"):
            if(iCurrentMeanings == iMeaningTranslationCounter):
                selectedEntry = entry
                break
            else:
                iCurrentMeanings += 1

    if(selectedEntry == None):
        DoneWithMeaningTranslationLevel()
        return

    print(iPosition, len(listInput[iMeaningTranslationLevelSelected]))

    if(selectedEntry["id"] != selectedEntry["sharedid"]):
        selectedEntry = dicoItemPerId[selectedEntry["sharedid"]]

    if(selectedEntry["id"] in dicoTempKanaOnlySharedIds):
        selectedEntry = dicoItemPerId[dicoTempKanaOnlySharedIds[selectedEntry["id"]]]

    if(selectedEntry["id"] in setAlreadyDoneInThisLevel):
        DisplayNextMeanings()
        return

    setAlreadyDoneInThisLevel.add(selectedEntry["id"])

    dicoMeaningEntries = {}

    label = tkinter.Label(root, text=selectedEntry["display"], width=80)
    label.config(font=('Arial', FontSize))
    label.grid(row=0, column=0, columnspan=5)

    button = tkinter.Button(root, text="Next Empty", command=lambda id=selectedEntry["id"] : SearchNextEmpty(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=0)

    button = tkinter.Button(root, text="Continue", command=lambda id=selectedEntry["id"] : ContinueToNextMeaning(id))
    button.config(font=('Arial', FontSize))
    button.grid(row=1, column=1, columnspan=3)

    checkbutton = tkinter.Checkbutton(root, text='Translations',variable=bShouldTranslate, onvalue=1, offvalue=0)
    checkbutton.config(font=('Arial', FontSize))
    checkbutton.grid(row=2, column=0, columnspan=5)

    label = tkinter.Label(root, text="Original-en")
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=3, column=0)

    label = tkinter.Label(root, text="en")
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=3, column=1)

    label = tkinter.Label(root, text="fr")
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=3, column=2)

    label = tkinter.Label(root, text="pt")
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=3, column=3)

    label = tkinter.Label(root, text="es")
    label.config(font=('Arial', int(FontSize * 0.7)))
    label.grid(row=3, column=4)

    iCurrentRow = 4

    dicoTranslationsFr = {}

    if(bShouldTranslate.get() != 0 and not(bSearchNextEmpty)):
        try:
            translationsfr = translator.translate(selectedEntry["meanings"][0:5], src='en', dest='fr')
            for translation in translationsfr:
                dicoTranslationsFr[translation.origin] = translation.text
        except:
            pass

    iCurrentMeaningLevel = iMeaningTranslationLevelSelected

    for level in dicoOutput["MeaningsTranslations"]:
        if(str(selectedEntry["id"]) in dicoOutput["MeaningsTranslations"][level]):
            iCurrentMeaningLevel = int(level)
            break

    bNotEmpty = False

    listAddedMeanings = []

    for meaning in selectedEntry["meanings"]:
        if(meaning in listAddedMeanings):
            continue

        listAddedMeanings.append(meaning)

        bMeaningAlreadyIn = (str(iCurrentMeaningLevel) in dicoOutput["MeaningsTranslations"] and 
                            str(selectedEntry["id"]) in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)] and
                            meaning in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])])

        label = tkinter.Label(root, text=meaning)
        label.config(font=('Arial', int(FontSize * 0.3)))
        label.grid(row=iCurrentRow, column=0)

        dicoMeaningEntries[meaning] = {}

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.3)))
        entry.grid(row=iCurrentRow, column=1)
        dicoMeaningEntries[meaning]["en"] = entry

        if(bMeaningAlreadyIn and "en" in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]):
            entry.delete(0, tkinter.END)
            entry.insert(0, dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]["en"])
            bNotEmpty = True

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.3)))
        entry.grid(row=iCurrentRow, column=2)
        dicoMeaningEntries[meaning]["fr"] = entry

        if(bMeaningAlreadyIn and "fr" in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]):
            entry.delete(0, tkinter.END)
            entry.insert(0, dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]["fr"])
            bNotEmpty = True

        if(meaning in dicoTranslationsFr):
            translation = dicoTranslationsFr[meaning]
            button = tkinter.Button(root, text=translation, command=lambda entry=entry, text=translation : ChangeEntryContent(entry, text))
            button.config(font=('Arial', int(FontSize * 0.3)))
            button.grid(row=iCurrentRow + 1, column=2)

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.3)))
        entry.grid(row=iCurrentRow, column=3)
        dicoMeaningEntries[meaning]["pt"] = entry

        if(bMeaningAlreadyIn and "pt" in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]):
            entry.delete(0, tkinter.END)
            entry.insert(0, dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]["pt"])
            bNotEmpty = True

        entry = tkinter.Entry(root)
        entry.config(font=('Arial', int(FontSize * 0.3)))
        entry.grid(row=iCurrentRow, column=4)
        dicoMeaningEntries[meaning]["es"] = entry

        if(bMeaningAlreadyIn and "es" in dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]):
            entry.delete(0, tkinter.END)
            entry.insert(0, dicoOutput["MeaningsTranslations"][str(iCurrentMeaningLevel)][str(selectedEntry["id"])][meaning]["es"])
            bNotEmpty = True

        iCurrentRow += 2

    if(bSearchNextEmpty and bNotEmpty):
        root.after(1, lambda id=selectedEntry["id"] : ContinueToNextMeaning(id))
    elif(bSearchNextEmpty):
        iMeaningTranslationCounter -= 1
        setAlreadyDoneInThisLevel.remove(selectedEntry["id"])
        bSearchNextEmpty = False
        root.after(1, lambda id=selectedEntry["id"] : ContinueToNextMeaning(id))

def DoneWithMeaningTranslationLevel():
    global dicoOutput
    dicoOutput["MeaningsTranslations"][str(iMeaningTranslationLevelSelected)] = dicoMeaningsTranslations

    for level in dicoOutput["MeaningsTranslations"]:
        if(level == str(iMeaningTranslationLevelSelected)):
            continue

        for id in dicoMeaningsTranslations:
            if(id in dicoOutput["MeaningsTranslations"][level]):
                del dicoOutput["MeaningsTranslations"][level][id]


    MeaningTranslationSelection()

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

    for kunreading in entry["kun_readings"]:
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
### WHATEVER BLOCK
###
###

root = tkinter.Tk()

bShouldTranslate = tkinter.IntVar()

button = tkinter.Button(root, text="KanaOnly", command=KanaOnlySelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Vocabulary", command=VocabularySelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Per Item Definition", command=MeaningTranslationSelection)
button.pack()
button.config(font=('Arial', FontSize))
button = tkinter.Button(root, text="Kun reading picker", command=KunReadingSelection)
button.pack()
button.config(font=('Arial', FontSize))
root.mainloop()

json.dump(dicoOutput, open("../.src/Selected.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
dicoSelected = json.load(open("../.src/Selected.json", "r", encoding="utf-8"))

listOutput = []

for level in listInput:
    listOutput.append([])

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

listValidKanaOnly = []

for level in listInput:
    for item in level:
        if(item["type"] == "vocab_kana" and item["id"] in setValidKanaOnlyId):
            listValidKanaOnly.append(item)

for level in listInput:
    for item in level:
        if(item["type"] == "vocab_kana" and item["id"] in dicoKanaOnlySharedIds):
            item["sharedid"] = dicoKanaOnlySharedIds[item["id"]]
            item["meanings"] = []
            item["meanings_fr"] = []
            item["meanings_es"] = []
            item["meanings_pt"] = []

iCurrentKanaOnlyCursor = 0

for iLevel, level in enumerate(listOutput):
    for item in listInput[iLevel]:
        if(item["id"] in dicoMeaningsTranslationsAndReplacements):
            listemptiedmeanings = []
            originalmeanings = copy.deepcopy(item["meanings"])

            for i in range(len(originalmeanings)):
                if(originalmeanings[i] in dicoMeaningsTranslationsAndReplacements[item["id"]]):
                    for lang in dicoMeaningsTranslationsAndReplacements[item["id"]][originalmeanings[i]]:
                        if(lang == "en"):
                            item["meanings"][i] = dicoMeaningsTranslationsAndReplacements[item["id"]][originalmeanings[i]]["en"]
                        else:
                            affectedlistname = "meanings_" + lang

                            if(not(affectedlistname in listemptiedmeanings)):
                                item[affectedlistname] = []
                                listemptiedmeanings.append(affectedlistname)

                            if(not(dicoMeaningsTranslationsAndReplacements[item["id"]][originalmeanings[i]][lang] in item[affectedlistname])):
                                item[affectedlistname].append(dicoMeaningsTranslationsAndReplacements[item["id"]][originalmeanings[i]][lang])

        if(item["type"] == "kanji"):

            for iReading, reading in enumerate(item["kun_readings"]):
                if(reading.endswith("-")):
                    item["kun_readings"][iReading] = reading[:-1]

            newreadinglist = []

            for reading in item["kun_readings"]:
                if(not(reading in newreadinglist)):
                    newreadinglist.append(reading)

            if(item["id"] in dicoKunReadingReplacements):
                newreadinglist = []

                for reading in item["kun_readings"]:
                    if(reading in dicoKunReadingReplacements[item["id"]]):
                        if(not(dicoKunReadingReplacements[item["id"]][reading] in newreadinglist)):
                            newreadinglist.append(dicoKunReadingReplacements[item["id"]][reading])
                    else:
                        if(not(reading in newreadinglist)):
                            newreadinglist.append(reading)
                
                item["kun_readings"] = newreadinglist
                
            level.append(item)
        elif(item["type"] == "vocab" and item["sharedid"] in setValidVocabularySharedId):
            if("〇" in item["display"] and not(item["id"] == item["sharedid"])):
                continue
            level.append(item)

    if(iLevel * 10 < len(listValidKanaOnly)):
        level.extend(listValidKanaOnly[iLevel * 10: min((iLevel + 1) * 10, len(listValidKanaOnly))])


json.dump(listOutput, open("../Output/Levels.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


