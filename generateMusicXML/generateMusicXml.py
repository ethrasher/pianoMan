from lxml import etree
from six import string_types


def generateMusicXML(attributeDict, measuresList):
    # Setup root of XML
    # part-list, score-part, part-name
    root = etree.Element("score-partwise")
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
            noteElement = etree.SubElement(measureElement, "note")
            addData(noteElement, note)

    # Output the completed MusicXML file
    tree = etree.ElementTree(root)
    outputMusicXML(tree)


# Outputs the result MusicXML file with public_id and system_url
def outputMusicXML(tree):
    tree.docinfo.public_id = '-//Recordare//DTD MusicXML 2.0 Partwise//EN'
    tree.docinfo.system_url = 'http://www.musicxml.org/dtds/partwise.dtd'
    xmlContent = etree.tostring(tree, method='xml', pretty_print=True, xml_declaration=True, encoding='UTF-8')
    outputFile = open("outputXML.xml", "wb")
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

generateMusicXML(attribute, measures)