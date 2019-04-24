if __name__ == "__main__":
    import os.path
    import time
    from performanceScoreEvaluator import compare
    from sendToPi import sendFileToPi
else:
    import os.path
    import time
    from performanceScoreEvaluator.performanceScoreEvaluator import compare
    from performanceScoreEvaluator.sendToPi import sendFileToPi

def main(sendToPi, performanceScoreOnly = False):
    if performanceScoreOnly:
        script_path = os.path.dirname(os.path.realpath(__file__))
        performance_path = script_path + "/midi/performance.mid"
        start_file_path = script_path + "/../outBoundFiles/start.txt"
        end_file_path = script_path + "/../outBoundFiles/end.txt"
        xml_path = script_path + "/../outBoundFiles/outputXML.xml"

    else:
        script_path = os.path.dirname(os.path.realpath(__file__))
        performance_path = script_path + "/midi/performance.mid"
        start_file_path = script_path + "/../outBoundFiles/start.txt"
        end_file_path = script_path + "/../outBoundFiles/end.txt"
        xml_path = script_path + "/../outBoundFiles/outputXML.xml"

    print("scriptpath:", script_path)
    print("performancepath", performance_path)
    print("startfilepath", start_file_path)
    print("xmlpath", xml_path)

    # Citation[7]
    # Wait until start.txt, musicxml, user performance MIDI file exist
    counter = 0
    while not os.path.exists(performance_path) or not os.path.exists(start_file_path) or not os.path.exists(xml_path):
        print("here: %d"%counter)
        print(os.path.exists(performance_path))
        print(os.path.exists(start_file_path))
        print(os.path.exists(xml_path))
        counter+=1
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
        write_file(end_file_path, content.strip())
        if sendToPi:
            sendFileToPi(end_file_path)

        # Delete start.txt, end.txt, outputxml, and user performance MIDI file
        '''try:
            # os.remove(start_file_path)
            # os.remove(end_file_path)
            # os.remove(xml_path)
            # os.remove(performance_path)
        except OSError:
            print("Error while deleting files.")'''

    else:
        raise ValueError("%s isn't a file!" % start_file_path)


def write_file(path, contents): # Citation[6]
    with open(path, "wt") as f:
        f.write(contents)

if __name__ == "__main__":
    main(False, True)