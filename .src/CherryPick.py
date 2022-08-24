import enum
from glob import glob
from logging import root
import tkinter
import os
import json
import Tooltip

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
    dicoOutput["SelectedKanaOnly"] = []

def Quit():
    global root
    root.quit()

def KanaOnlySelection():
    global root
    for child in root.winfo_children():
        child.destroy()

def VocabularySelection():
    global root
    for child in root.winfo_children():
        child.destroy()
    for iLevel, level in enumerate(listInput):
        button = tkinter.Button(root, text=str(iLevel + 1), command = lambda level=iLevel: SelectLevel(level))
        button.grid(column=iLevel%10, row = iLevel//10)

    iLevel += 10

    button = tkinter.Button(root, text="Quit", command = Quit)
    button.grid(column=0, row = iLevel//10, columnspan=10) 

iLevelSelected = -1
iKanjiCounter = -1
setSelectedVocab = set()

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

FontSize = 30
dicoPerButton = {}

def DisplayNextKanjiChoices():
    global iKanjiCounter
    global root
    global dicoPerButton
    global dicoItemPerId
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
                button.grid(row=iButtonPosition // ColumnCount, column = iButtonPosition % ColumnCount)
                Tooltip.CreateToolTip(button, entry["meanings"][0])
                iButtonPosition += 1
                dicoPerButton[entry["id"]] = button

def DoneWithLevel():
    global dicoOutput
    dicoOutput["SelectedVocab"][str(iLevelSelected)] = list(setSelectedVocab)
    VocabularySelection()

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

setValidVocabularySharedId = set()

for level in dicoSelected["SelectedVocab"]:
    for item in dicoSelected["SelectedVocab"][level]:
        setValidVocabularySharedId.add(item)

for iLevel, level in enumerate(listOutput):
    for item in listInput[iLevel]:
        if(item["type"] == "kanji"):
            level.append(item)
        elif(item["type"] == "vocab" and item["sharedid"] in setValidVocabularySharedId):
            level.append(item)

json.dump(listOutput, open("../Output/Levels.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


