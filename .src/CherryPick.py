import enum
from glob import glob
from logging import root
import tkinter
import os
import json
from turtle import color
import Tooltip

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

def SelectKanaOnlyLevel(level):
    global iKanaOnlyLevelSelected
    global iKanaOnlyCounter
    global setSelectedKanaOnly
    iKanaOnlyLevelSelected = level
    iKanaOnlyCounter = -1
    setSelectedKanaOnly = set()
    DisplayNextKanaOnlyChoice()

def AcceptKanaOnly(kanaonly):
    setSelectedKanaOnly.add(kanaonly)
    DisplayNextKanaOnlyChoice()

def RefuseKanaOnly(kanaonly):
    DisplayNextKanaOnlyChoice()

def DisplayNextKanaOnlyChoice():
    global iKanaOnlyLevelSelected
    global iKanaOnlyCounter
    global root

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

    label = tkinter.Label(root, text=selectedEntry["meanings"][0])
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

def DoneWithKanaOnlyLevel():
    global dicoOutput
    dicoOutput["SelectedKanaOnly"][str(iKanaOnlyLevelSelected)] = list(setSelectedKanaOnly)
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
### WHATEVER BLOCK
###
###

root = tkinter.Tk()
button = tkinter.Button(root, text="KanaOnly", command=KanaOnlySelection)
button.pack()
button = tkinter.Button(root, text="Vocabulary", command=VocabularySelection)
button.pack()
button = tkinter.Button(root, text="Per Item Definition")
button.pack()
root.mainloop()

json.dump(dicoOutput, open("../.src/Selected.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
dicoSelected = json.load(open("../.src/Selected.json", "r", encoding="utf-8"))

listOutput = []

for level in listInput:
    listOutput.append([])

setValidKanaOnlyId = set()

for level in dicoSelected["SelectedKanaOnly"]:
    for item in dicoSelected["SelectedKanaOnly"][level]:
        setValidKanaOnlyId.add(item)

setValidVocabularySharedId = set()

for level in dicoSelected["SelectedVocab"]:
    for item in dicoSelected["SelectedVocab"][level]:
        setValidVocabularySharedId.add(item)

listValidKanaOnly = []

for level in listInput:
    for item in level:
        if(item["type"] == "vocab_kana" and item["id"] in setValidKanaOnlyId):
            listValidKanaOnly.append(item)

iCurrentKanaOnlyCursor = 0

for iLevel, level in enumerate(listOutput):
    for item in listInput[iLevel]:
        if(item["type"] == "kanji"):
            level.append(item)
        elif(item["type"] == "vocab" and item["sharedid"] in setValidVocabularySharedId):
            if("〇" in item["display"] and not(item["id"] == item["sharedid"])):
                continue
            level.append(item)

    if(iLevel * 20 < len(listValidKanaOnly)):
        level.extend(listValidKanaOnly[iLevel * 20: min((iLevel + 1) * 20, len(listValidKanaOnly))])


json.dump(listOutput, open("../Output/Levels.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


