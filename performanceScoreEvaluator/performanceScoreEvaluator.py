from music21 import *


def xml2stream(filename):
    s = converter.parse(filename)
    return s

def midi2stream(filename):
    mf = midi.MidiFile()
    mf.open(filename)
    mf.read()
    mf.close()
    s = midi.translate.midiFileToStream(mf)
    return s

def noteSort(note):
    if type(note) == chord.Chord:
        return (note.offset, note.quarterLength, "Z")
    else:
        return (note.offset, note.quarterLength, str(note.pitch.name))

def score2list(score):
    parts = score.getElementsByClass(stream.Part)
    result = []
    for part in parts:
        # flatten unnecessary voices in a part so that the converted notes list looks more like MusicXML structure
        offset = 0.0
        prevOffset = 0.0
        noteList = []
        for singleNote in part.flat.notes:
            if (len(result) == 0 and len(noteList) == 0):
                if (type(singleNote) == note.Rest):
                    continue
                # Update offset as the offset of the first note of the piece
                elif (type(singleNote) == note.Note):
                    offset = singleNote.offset
            if (singleNote.offset == prevOffset):
                noteList.append(singleNote)
            else:
                noteList.sort(key=lambda x: x.quarterLength)
                for oneNote in noteList:
                    result.append(oneNote)
                noteList = [singleNote]
                prevOffset = singleNote.offset
    return (result, offset)


def stream2list(str, hand):
    result = []
    offset = 0.0
    if (hand != "both"):
        for part in str.parts:
            for measure in part.getElementsByClass(stream.Measure):
                # if the performer chose to play bass clef only (left hand)
                if (hand == "bass" and measure.clef == clef.TrebleClef()):
                    str.remove(part)
                    break
                # if the performer chose to play treble clef only (right hand)
                if (hand == "treble" and measure.clef == clef.BassClef()):
                    str.remove(part)
                    break
    for singleNote in str.semiFlat.notes:
        if (len(result) == 0):
            if (type(singleNote) == note.Note):
                offset = singleNote.offset
        result.append(singleNote)
    result.sort(key=noteSort)
    return (result, offset)

def printNotesList(lst, offset):
    for singleNote in lst:
        if (type(singleNote) != chord.Chord):
            print(singleNote.pitch.name, singleNote.offset - offset, singleNote.quarterLength)
        else:
            print(singleNote, singleNote.offset - offset, singleNote.quarterLength)


def getScore(originalList, userList, originalOffset, userOffset):
    # correctly/wrong duration/missed
    gradebook = {'score': 100, 'hit': 0, 'miss': 0, 'wrong': 0,'duration': 0, 'early': 0, 'late': 0}
    gradebook['hit'] = len(originalList)
    unitScore = 100 / len(originalList)
    i = 0
    j = 0
    # score = 100
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
                # print("CASE 1")
            # CASE 2-a: Wrong note without the correct note
            elif (type(userNote) != chord.Chord):
                gradebook['wrong'] += 1
                gradebook['hit'] -= 1
                gradebook['score'] -= unitScore
                # print("CASE 2-a")
            # both notes are chords, so compare their pitches
            else:
                deductionUnit = max(len(correctNote.pitches), len(userNote.pitches))
                for pitch in correctNote.pitches:
                    # CASE 2-b: Wrong note with the correct note
                    if pitch in userNote.pitches:
                        # print("CASE 2-b")
                        gradebook['wrong'] += 1
                        gradebook['hit'] -= 1
                        deductionUnit -= 1
                assert(deductionUnit >= 0)
                gradebook['score'] -= deductionUnit * unitScore
        # TYPE 2: Notes
        else:
            # compare their relative offsets
            # if two notes have the same offset
            if (correctNote.offset - originalOffset == userNote.offset - userOffset):
                # CASE 2-c: Wrong note without the correct note
                if (correctNote.pitch.name != userNote.pitch.name):
                    gradebook['wrong'] += 1
                    gradebook['hit'] -= 1
                    gradebook['score'] -= unitScore
                    # print("CASE 2-c")
                # CASE 3-a: Shorter/longer note
                elif (correctNote.quarterLength != userNote.quarterLength):
                    gradebook['duration'] += 1
                    gradebook['hit'] -= 1
                    deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                    gradebook['score'] -= deduction
                    # print("CASE 3-a")
            # if two notes have different offsets
            else:
                if (correctNote.pitch.name == userNote.pitch.name):
                    # CASE 3-b: Shorter/longer note
                    gradebook['duration'] += 1
                    gradebook['hit'] -= 1
                    if (correctNote.quarterLength != userNote.quarterLength):
                        deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                        gradebook['score'] -= deduction
                        # print("CASE 3-b")
                    # deduct points based on offset difference
                    # if correctNote's quarterLength is 0, prevent division by 0
                    if (correctNote.quarterLength == 0):
                        gradebook['score'] -= unitScore
                    else:
                        deduction = unitScore * abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset)) / (correctNote.quarterLength)
                        gradebook['score'] -= deduction
                # CASE 4: Missing a note
                else:
                    gradebook['miss'] += 1
                    gradebook['hit'] -= 1
                    gradebook['score'] -= unitScore
                    if (correctNote.offset - originalOffset > userNote.offset - userOffset):
                        i -= 1
                    else:
                        j -= 1
                    # print("CASE 4")
        i += 1
        j += 1
    return gradebook

def compare(originalFile, userFile):
    originalStream = xml2stream(originalFile)
    userStream = midi2stream(userFile)
    # Pass the original stream and hand information - Bass/Treble
    (originalNotesAndRests, originalOffset) = stream2list(originalStream, "both")
    (userNotesAndRests, userOffset) = score2list(userStream)
    totalCorrectNotes = len(originalNotesAndRests)
    totalUserNotes = len(userNotesAndRests)

    gradebook = getScore(originalNotesAndRests, userNotesAndRests, originalOffset, userOffset)
    if (gradebook['score'] < 0):
        gradebook['score'] = 0
    return gradebook


# print("1. Missing one note: ", compare("midi/outputXML.musicxml", "midi/swanWithOneMissingNote.mid"))
# print("2. Missing two consecutive notes: ", compare("midi/outputXML.musicxml", "midi/swanWithTwoConsecutiveMissingNotes.mid"))
# print("3. One shorter note: ", compare("midi/outputXML.musicxml", "midi/swanWithOneShorterNote.mid"))
# print("4. One wrong note (with the correct note): ", compare("midi/outputXML.musicxml", "midi/swanWithOneWrongNoteWithCorrectNote.mid"))
# print("5. One wrong note (without the correct note): ", compare("midi/outputXML.musicxml", "midi/swanWithOneWrongNote.mid"))
# print("6. Perfect but rest before starting: ", compare("midi/outputXML.musicxml", "midi/swanWithTwoBeatsShifted.mid"))
# print("7. Good Performance: ", compare("midi/outputXML.musicxml", "midi/User Performance.mid"))
# print("8. Bad Performance: ", compare("midi/outputXML.musicxml", "midi/BadPerformance.mid"))
# print("9. Bad Performance 2: ", compare("midi/outputXML.musicxml", "midi/BadPerformance2.mid"))
# print("10. Demo Performance: ", compare("midi/outputXML.musicxml", "midi/DemoPerformance.mid"))
# print("11. Ableton Performance: ", compare("midi/outputXML.musicxml", "midi/bpm49swanAbleton.mid"))
# print("12. BPM 56: ", compare("midi/outputXML.musicxml", "midi/bpm56swan.mid"))
# print("13. BPM 62: ", compare("midi/outputXML.musicxml", "midi/swan62swan2.mid"))
# print("14. BPM 71: ", compare("midi/outputXML.musicxml", "midi/bpm71swan.mid"))
# print("15. BPM 83: ", compare("midi/outputXML.musicxml", "midi/bpm83swan.mid"))
# print("16. Treble: ", compare("midi/outputXML.musicxml", "midi/swanTreble.mid"))
# print("17. Bass: ", compare("midi/outputXML.musicxml", "midi/swanBass.mid"))
