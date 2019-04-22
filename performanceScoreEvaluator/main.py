import os.path
import time
from performanceScoreEvaluator import compare
from sendToPi import sendFileToPi

def main():
    start_file_path = "/outBoundFiles/start.txt"
    end_file_path = "/outBoundFiles/end.txt"
    xml_path = "/outBoundFiles/outputXML.musicxml"
    performance_path = "midi/performance.mid"
    script_path = os.path.dirname(os.path.realpath(__file__))

    # Citation[7]
    # Wait until start.txt, musicxml, user performance MIDI file exist
    while not os.path.exists(performance_path) or not os.path.exists(start_file_path) or not os.path.exists(xml_path):
        time.sleep(1)

    if os.path.isfile(start_file_path) and os.path.isfile(xml_path) and os.path.isfile(performance_path):
        start_file_dict = {}
        # Parse the start.txt file from OMR
        with open(start_file_path) as sf:
            for line in sf:
                (key, val) = line.split(":")
                start_file_dict[key] = val.strip()

        # Run performance score evaluator
        gradebook = compare(xml_path, performance_path, start_file_dict['hand'])
        print(gradebook)

        # Store the output gradebook as a txt file and send it to pi (end.txt)
        content = ""
        for key in gradebook:
            content += key + ":" + str(round(gradebook[key])) + "\n"
        write_file(script_path + "/" + end_file_path, content.strip())
        sendFileToPi(end_file_path)

        # Delete start.txt, end.txt, outputxml, and user performance MIDI file
        try:
            os.remove(start_file_path)
            os.remove(end_file_path)
            os.remove(xml_path)
            # os.remove(performance_path)
        except OSError:
            print("Error while deleting files.")

    else:
        raise ValueError("%s isn't a file!" % start_file_path)


def write_file(path, contents): # Citation[6]
    with open(path, "wt") as f:
        f.write(contents)

main()