import os.path
import time
from performanceScoreEvaluator import compare
from sendToPi import sendFileToPi

def main():
    start_file_path = "start.txt"
    xml_path = "xml/outputXML.musicxml"
    performance_path = "midi/performance.mid"

    # Citation[7]
    while not os.path.exists(start_file_path):
        time.sleep(1)

    if os.path.isfile(start_file_path):
        start_file_dict = {}
        with open(start_file_path) as sf:
            for line in sf:
                (key, val) = line.split(":")
                start_file_dict[key] = val.strip()
        print(start_file_dict)
        start_file_dict['title'] = 'Swans on the Lake'
        gradebook = compare(xml_path, performance_path)
        print(gradebook)

        content = ""
        for key in gradebook:
            content += key + ":" + str(round(gradebook[key])) + "\n"
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        writeFile(scriptPath + "/end.txt", content.strip())
        sendFileToPi("end.txt")

    else:
        raise ValueError("%s isn't a file!" % start_file_path)


def writeFile(path, contents): # Citation[6]
    with open(path, "wt") as f:
        f.write(contents)

main()