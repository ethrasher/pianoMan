from lxml import etree
from six import string_types
import os


def generateMusicXML(fileName, measureDuration, attributeDict, measuresList):
    # Setup root of XML
    # part-list, score-part, part-name
    root = etree.Element("score-partwise")
    credit = etree.SubElement(root, "credit")
    creditWords = etree.SubElement(credit, "credit-words")
    creditWords.text = fileName
    partList = etree.SubElement(root, "part-list")
    scorePart = etree.SubElement(partList, "score-part", id="P1")
    partName = etree.SubElement(scorePart, "part-name")
    partName.text = "Piano"

    # Create a page
    part = etree.SubElement(root, "part", id="P1")

    # Add notes to the page
    for i in range(len(measuresList)):
        measureElement = etree.SubElement(part, "measure", number=str(i + 1))

        if (i == 0):
            attributes = etree.SubElement(measureElement, "attributes")
            addData(attributes, attributeDict)

        for note in measuresList[i]:
            if isinstance(note, dict):
                noteElement = etree.SubElement(measureElement, "note")
                addData(noteElement, note)
            else:
                # need to add backup
                #Create backup dict
                backupDict = {"duration":str(measureDuration)}
                backupElement = etree.SubElement(measureElement, "backup")
                addData(backupElement, backupDict)

    # Output the completed MusicXML file
    tree = etree.ElementTree(root)
    outputMusicXML(tree)


# Outputs the result MusicXML file with public_id and system_url
def outputMusicXML(tree):
    tree.docinfo.public_id = '-//Recordare//DTD MusicXML 2.0 Partwise//EN'
    tree.docinfo.system_url = 'http://www.musicxml.org/dtds/partwise.dtd'
    xmlContent = etree.tostring(tree, method='xml', pretty_print=True, xml_declaration=True, encoding='UTF-8')
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    print("writing file to: ", scriptPath + "/outBoundFiles/outputXML.xml")
    outputFile = open(scriptPath + "/outBoundFiles/outputXML.xml", "wb")
    outputFile.write(xmlContent)


# Recursively sets all data which was passed in as a dictionary
def addData(root, data):
    if isinstance(data, dict):
        for (key, value) in data.items():
            if isinstance(value, list):
                for i in range(len(value)):
                    element = etree.SubElement(root, key, number=str(i + 1))
                    addData(element, value[i])
            else:
                element = etree.SubElement(root, key)
                addData(element, value)
    elif isinstance(data, string_types):
        root.text = data


def formXMLDictionaryFromObjects(allMeasures, divisions):
    print("Size all Measures", len(allMeasures))
    dictMeasures = []
    for measure in allMeasures:
        print("Size of this measure", len(measure))
        dictSingleMeasure = []
        seenBaseNote = False
        for noteElem in measure:
            #check for adding backup, check if it is the base staff
            if seenBaseNote == False and noteElem.staff%2 == 0:
                seenBaseNote = True
                dictSingleMeasure.append("backup")
            if noteElem.typeName == "note":
                noteDict = turnNoteIntoDict(noteElem, divisions)
                dictSingleMeasure += noteDict
            elif noteElem.typeName == "rest":
                restDict = turnRestIntoDict(noteElem, divisions)
                dictSingleMeasure += restDict
        dictMeasures.append(dictSingleMeasure)
    return dictMeasures

def turnNoteIntoDict(noteElem, divisions):
    notes = []
    for noteElemIndex in range(len(noteElem.pitches)):
        noteDict = dict()
        if noteElem.alterPitches[noteElemIndex] == "sharp":
            noteElem.pitches[noteElemIndex]["alter"] = 1
        elif noteElem.alterPitches[noteElemIndex] == "flat":
            noteElem.pitches[noteElemIndex]["alter"] = -1
        for key in noteElem.pitches[noteElemIndex]:
            noteElem.pitches[noteElemIndex][key] = str(noteElem.pitches[noteElemIndex][key])
        noteDict["pitch"] = noteElem.pitches[noteElemIndex]
        if noteElem.durationName == "quarter":
            noteDict["duration"] = str(divisions)
        elif noteElem.durationName == "half":
            noteDict["duration"] = str(2*divisions)
        elif noteElem.durationName == "whole":
            noteDict["duration"] = str(4*divisions)
        elif noteElem.durationName == "eighth":
            noteDict["duration"] = str(int(divisions//2))
        elif noteElem.durationName == "sixteenth":
            noteDict["duration"] = str(int(divisions//4))
        noteDict["type"] = str(noteElem.durationName)
        noteDict["stem"] = str(noteElem.stem)
        prelimStaff = noteElem.staff % 2
        if prelimStaff == 1:
            noteDict["staff"] = "1"
        else:
            noteDict["staff"] = "2"
        if noteElem.dottedPitches[noteElemIndex]:
            noteDict["dot"] = None
            noteDict["duration"] = str(int(int(noteDict["duration"])*1.5))
        if noteElemIndex > 0:
            noteDict["chord"] = None
        notes.append(noteDict)
    return notes

def turnRestIntoDict(restElem, divisions):
    restDict = dict()
    restDict["rest"] = None
    if restElem.durationName == "quarter":
        restDict["duration"] = str(divisions)
    elif restElem.durationName == "half":
        restDict["duration"] = str(2 * divisions)
    elif restElem.durationName == "whole":
        restDict["duration"] = str(4 * divisions)
    elif restElem.durationName == "eighth":
        restDict["duration"] = str(int(divisions // 2))
    elif restElem.durationName == "sixteenth":
        restDict["duration"] = str(int(divisions // 4))
    restDict["type"] = str(restElem.durationName)
    restDict["staff"] = str(restElem.staff % 2)
    return [restDict]

def formXML(allMeasures):
    dictMeasures = formXMLDictionaryFromObjects(allMeasures, 1)
    measureDuration = attribute["time"]["beats"]
    generateMusicXML("fileName here", measureDuration, attribute, dictMeasures)


###########EXAMPLES FOR DEVELOPING BELOW
#generateMusicXML(attribute, measures)

# Example attribute dictionary
attribute = {"divisions": "1",
             "key": {"fifths": "0",
                      "mode": "major"},
             "time": {"beats": "3",
                      "beat-type": "4"},
             "staves": "2",
             "clef": [{"sign": "G", "line": "2"}, {"sign": "F", "line": "4"}]}


# Example list of measures
# measures: List<List<Note>>
# Each measure is a list of notes
measures = [
    [{"pitch": {"step": "C", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "C", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "dot": "",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "G", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "G", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     }],

    [{"pitch": {"step": "A", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "A", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "G", "octave": "4"},
     "duration": "2",
     "voice": "1",
     "type": "half",
     "stem": "up",
     "staff": "1"
     }],

    [{"pitch": {"step": "F", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "F", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "E", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "E", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     }],

    [{"pitch": {"step": "D", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "D", "octave": "4"},
     "duration": "1",
     "voice": "1",
     "type": "quarter",
     "stem": "up",
     "staff": "1"
     },
    {"pitch": {"step": "C", "octave": "4"},
     "duration": "2",
     "voice": "1",
     "type": "half",
     "stem": "up",
     "staff": "1"
     }]
]
