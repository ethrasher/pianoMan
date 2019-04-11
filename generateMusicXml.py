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
    dictMeasures = []
    for measure in allMeasures:
        dictSingleMeasure = []
        seenBaseNote = False
        for noteElem in measure:
            #check for adding backup, check if it is the base staff
            if seenBaseNote == False and noteElem.staff%2 == 0:
                seenBaseNote = True
                dictSingleMeasure.append("backup")
            if noteElem.typeName == "note":
                noteDict = noteElem.getXMLDict(divisions=divisions)
                dictSingleMeasure += noteDict
            elif noteElem.typeName == "rest":
                restDict = noteElem.getXMLDict(divisions=divisions)
                dictSingleMeasure += restDict
        dictMeasures.append(dictSingleMeasure)
    return dictMeasures

def formAttributeDictionary(divisions, key, timeBeats, timeBeatType):
    attribute = {"divisions": str(divisions),
                 "key": {"fifths": str(key),
                         "mode": "major"},
                 "time": {"beats": str(timeBeats),
                          "beat-type": str(timeBeatType)},
                 "staves": "2",
                 "clef": [{"sign": "G", "line": "2"}, {"sign": "F", "line": "4"}]}
    return attribute

def formXML(allMeasures, divisions, key, timeBeats, timeBeatType):
    attribute = formAttributeDictionary(divisions=divisions, key=key, timeBeats=timeBeats, timeBeatType=timeBeatType)
    dictMeasures = formXMLDictionaryFromObjects(allMeasures, 1)
    measureDuration = attribute["time"]["beats"]
    generateMusicXML("Swans on the Lake", measureDuration, attribute, dictMeasures)


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
