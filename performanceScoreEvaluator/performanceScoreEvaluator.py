from music21 import *

# Converts a musicXML file to a Stream object
def xml2stream(filename):
    s = converter.parse(filename)
    return s


# Converts a MIDI file to a Score object
def midi2score(filename):
    mf = midi.MidiFile()
    mf.open(filename)
    mf.read()
    mf.close()
    s = midi.translate.midiFileToStream(mf)
    return s


# Note comparison function: lower offset - higher offset
#                           shorter quarterLength - longer quarterLength
def note_sort(note):
    if type(note) == chord.Chord:
        return (note.offset, note.quarterLength, "Z")
    else:
        return (note.offset, note.quarterLength, str(note.pitch.name))


# Converts a Score object to a list of notes
def score2list(score):
    parts = score.getElementsByClass(stream.Part)
    result = []

    for part in parts:
        offset = 0.0
        prevOffset = 0.0
        noteList = []
        # Flatten unnecessary voices in a part so that the converted notes list looks more like MusicXML structure
        for singleNote in part.flat.notes:
            if (len(result) == 0 and len(noteList) == 0):
                if (type(singleNote) == note.Rest):
                    continue
                # Update offset as the offset of the first note of the piece
                elif (type(singleNote) == note.Note or type(singleNote) == chord.Chord):
                    offset = singleNote.offset
            if (singleNote.offset == prevOffset):
                if (type(singleNote) == chord.Chord):
                    for chordNote in singleNote:
                        noteList.append(chordNote)
                else:
                    noteList.append(singleNote)
            else:
                # Before adding notes to the result list, sort the notes with same offset by quarterLength
                noteList.sort(key=lambda x: x.quarterLength)
                for oneNote in noteList:
                    result.append(oneNote)
                noteList = []
                if (type(singleNote) == chord.Chord):
                    for chordNote in singleNote:
                        chordNote.offset = singleNote.offset
                        # print(chordNote, chordNote.offset)
                        noteList.append(chordNote)
                else:
                    noteList = [singleNote]
                prevOffset = singleNote.offset
    result.sort(key=note_sort)
    return (result, offset)


# Converts a Stream object to a list of notes
def stream2list(str, hand):
    result = []
    offset = 0.0
    # If the user selected treble-only or bass-only mode
    if (hand != "both"):
        for part in str.parts:
            for measure in part.getElementsByClass(stream.Measure):
                # If the user chose bass-only mode (left hand only), remove notes in treble clef
                if (hand == "bass" and measure.clef == clef.TrebleClef()):
                    str.remove(part)
                    break
                # If the user chose treble-only mode (right hand only), remove notes in bass clef
                if (hand == "treble" and measure.clef == clef.BassClef()):
                    str.remove(part)
                    break

    # Add all sorted notes
    for singleNote in str.semiFlat.notes:
        if (len(result) == 0):
            if (type(singleNote) == note.Note):
                offset = singleNote.offset
        if (type(singleNote) == chord.Chord):
            for chordNote in singleNote:
                chordNote.offset = singleNote.offset
                result.append(chordNote)
        else:
            result.append(singleNote)
    result.sort(key=note_sort)

    return (result, offset)


# Prints a notes list; displays pitch, offset, and quarterLength of each note object
def print_notes_list(lst, offset):
    for singleNote in lst:
        if (type(singleNote) != chord.Chord):
            print(singleNote.pitch.name, singleNote.offset - offset, singleNote.quarterLength)
        else:
            print(singleNote, singleNote.offset - offset, singleNote.quarterLength)


# Calculates the score by comparing the original list of notes and user's list of notes
def get_score(originalList, userList, originalOffset, userOffset):
    # Default gradebook
    gradebook = {'score': 100, 'hit': 0, 'miss': 0, 'wrong': 0,'duration': 0, 'early': 0, 'late': 0}
    gradebook['hit'] = len(originalList)
    unitScore = 33 / len(originalList)
    i = 0
    j = 0
    bestOffsetDiff = [0, 0, 0]

    while (i < len(originalList) and j < len(userList)):
        correctNote = originalList[i]
        userNote = userList[j]


        # TYPE 1: Chords
        if (type(correctNote) == chord.Chord or type(userNote) == chord.Chord):
            # CASE 1: Wrong note with the correct note
            if (type(correctNote) != chord.Chord and correctNote.pitch in userNote.pitches):
                gradebook['wrong'] += 1
                gradebook['hit'] -= 1
                gradebook['score'] -= unitScore / 2
                # print("CASE 1: wrong note with the correct note")

            # CASE 2-a: Wrong note without the correct note
            elif (type(userNote) != chord.Chord):
                gradebook['wrong'] += 1
                gradebook['hit'] -= 1
                gradebook['score'] -= unitScore / 2
                # print("CASE 2-a: Wrong note without the correct note")

            # Both notes are chords, so compare their pitches
            else:
                deductionUnit = max(len(correctNote.pitches), len(userNote.pitches))
                for pitch in correctNote.pitches:
                    # CASE 2-b: Wrong note with the correct note
                    if pitch in userNote.pitches:
                        gradebook['wrong'] += 1
                        gradebook['hit'] -= 1
                        deductionUnit -= 1
                        # print("CASE 2-b: Wrong note with the correct note")

                # Deduction unit (number of wrong notes) cannot be a negative value
                assert(deductionUnit >= 0)

        # TYPE 2: Notes
        else:
            # print("Score: ", gradebook['score'])
            # print("COMPARING")
            # print("1.", correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
            # print("2.", userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
            # Compare their relative offsets
            # If two notes have the same offset (correct start timing)
            if (correctNote.offset - originalOffset == userNote.offset - userOffset):
                # CASE 2-c: Wrong note without the correct note
                if (correctNote.pitch.name[0] != userNote.pitch.name[0]):
                    gradebook['wrong'] += 1
                    gradebook['hit'] -= 1
                    gradebook['score'] -= unitScore
                    # print("CASE 2-c: Correct offset, Wrong note without the correct note")

                # CASE 3-a: Shorter/longer notes
                elif (correctNote.quarterLength != userNote.quarterLength):
                    gradebook['duration'] += 1
                    gradebook['hit'] -= 1
                    deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                    # gradebook['score'] -= deduction / 10
                    gradebook['score'] -= deduction
                    # print("CASE 3-a: Correct offset, shorter/longer notes")

            # If two notes have different offsets
            else:
                # Same pitch (correct notes but wrong start timing)
                if (correctNote.pitch.name[0] == userNote.pitch.name[0]):

                    # CASE 3-b: Shorter/longer note
                    if (correctNote.quarterLength != userNote.quarterLength):
                        if (abs(correctNote.quarterLength - userNote.quarterLength) > 0.1):
                            deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / correctNote.quarterLength
                            # gradebook['score'] -= deduction / 10
                            gradebook['score'] -= deduction
                            # print("CASE 3-b: Diff offset, shorter/longer notes")

                    # Deduct points based on their offset difference
                    # If correctNote's quarterLength is 0, prevent division by 0
                    if (correctNote.quarterLength == 0):
                        # gradebook['score'] -= unitScore / 10
                        gradebook['score'] -= unitScore
                    elif (abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset)) > min(bestOffsetDiff)):
                        bestOffsetDiff[bestOffsetDiff.index(min(bestOffsetDiff))] = abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset))
                        deduction = unitScore * abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset)) / (correctNote.quarterLength)
                        # gradebook['score'] -= deduction / 10
                        gradebook['score'] -= deduction
                        if (correctNote.offset - originalOffset > userNote.offset - userOffset):
                            gradebook['early'] += 1
                        else:
                            gradebook['late'] += 1
                        gradebook['hit'] -= 1
                        # print("CASE 3: Offset diff")

                # CASE 4: Missing a note
                else:
                    gradebook['miss'] += 1
                    gradebook['hit'] -= 1
                    gradebook['score'] -= unitScore
                    if (correctNote.offset - originalOffset > userNote.offset - userOffset):
                        i -= 1
                        gradebook['miss'] -= 1
                        gradebook['hit'] += 1
                    elif (correctNote.offset - originalOffset == userNote.offset - userOffset):
                        if (correctNote.quarterLength > userNote.quarterLength):
                            i -= 1
                        else:
                            j -= 1
                    else:
                        j -= 1
                    # print("CASE 4: Missing a note")
                    # print(correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
                    # print(userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
        i += 1
        j += 1

    # If user got a negative score overall, set it to 0
    if (gradebook['score'] < 0):
        gradebook['score'] = 0

    # Checks if the sum of all notes in all criteria matches the total number of notes in the original list
    if (gradebook['hit'] + gradebook['miss']
            + gradebook['wrong'] + gradebook['duration']
            + gradebook['early'] + gradebook['late'] != len(originalList)):
        print("Gradebook Error: doesn't sum to number of notes")

    return gradebook


# Compares a musicXML file with a MIDI file
def compare(originalFile, userFile, hand):
    # Convert two files to corresponding Stream/Score object
    originalStream = xml2stream(originalFile)
    userScore = midi2score(userFile)

    # Convert Stream/Score objects to lists of notes
    # Pass the original stream and hand information - Both/Bass/Treble
    (originalNotesAndRests, originalOffset) = stream2list(originalStream, hand)
    (userNotesAndRests, userOffset) = score2list(userScore)
    # print_notes_list(originalNotesAndRests, originalOffset)
    # print("---------------------------------------------------")
    # print_notes_list(userNotesAndRests, userOffset)

    gradebook = get_score(originalNotesAndRests, userNotesAndRests, originalOffset, userOffset)
    return gradebook


# Test functions
def testAll():
    testSwan()
    testDoReMi()
    testYGAFIM()

def testSwan():
    print("Testing Swans on the Lake MIDI files....")
    print("1. Missing one note: ", compare("xml/swans.xml", "midi/swanWithOneMissingNote.mid", "both"))
    print("2. Missing two consecutive notes: ", compare("xml/swans.xml", "midi/swanWithTwoConsecutiveMissingNotes.mid", "both"))
    print("3. One shorter note: ", compare("xml/swans.xml", "midi/swanWithOneShorterNote.mid", "both"))
    print("4. One wrong note (with the correct note): ", compare("xml/swans.xml", "midi/swanWithOneWrongNoteWithCorrectNote.mid", "both"))
    print("5. One wrong note (without the correct note): ", compare("xml/swans.xml", "midi/swanWithOneWrongNote.mid", "both"))
    print("6. Perfect but rest before starting: ", compare("xml/swans.xml", "midi/swanWithTwoBeatsShifted.mid", "both"))
    print("7. Good Performance: ", compare("xml/swans.xml", "midi/User Performance.mid", "both"))
    print("8. Bad Performance: ", compare("xml/swans.xml", "midi/BadPerformance.mid", "both"))
    print("9. Bad Performance 2: ", compare("xml/swans.xml", "midi/BadPerformance2.mid", "both"))
    print("10. Demo Performance: ", compare("xml/swans.xml", "midi/DemoPerformance.mid", "both"))
    print("11. Ableton Performance: ", compare("xml/swans.xml", "midi/bpm49swanAbleton.mid", "both"))
    print("12. BPM 56: ", compare("xml/swans.xml", "midi/bpm56swan.mid", "both"))
    print("13. BPM 62: ", compare("xml/swans.xml", "midi/swan62swan2.mid", "both"))
    print("14. BPM 71: ", compare("xml/swans.xml", "midi/bpm71swan.mid", "both"))
    print("15. BPM 83: ", compare("xml/swans.xml", "midi/bpm83swan.mid", "both"))
    print("16. Treble: ", compare("xml/swans.xml", "midi/swanTreble.mid", "treble"))
    print("17. Bass: ", compare("xml/swans.xml", "midi/swanBass.mid", "bass"))
    print("\n")

def testDoReMi():
    print("Testing Do Re Mi MIDI files....")
    print(compare("xml/outputXML.xml", "midi/perf1.mid", "both"))
    print(compare("xml/outputXML.xml", "midi/perf2.mid", "both"))
    print(compare("xml/outputXML.xml", "midi/perf3bass.mid", "bass"))
    print(compare("xml/outputXML.xml", "midi/perf4.mid", "both"))
    print(compare("xml/outputXML.xml", "midi/oldp.mid", "both"))
    print("\n")

def testYGAFIM():
    print("Testing You've Got a Friend in Me....")
    print(compare("xml/outputXML.xml", "midi/friend1.mid", "both"))
    print(compare("xml/outputXML.xml", "midi/friend2.mid", "both"))
    print(compare("xml/outputXML.xml", "midi/friend3bass.mid", "bass"))
    print("\n")

# testAll()