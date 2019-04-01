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
    # score.show('text')
    print("----------------------------------")
    parts = score.getElementsByClass(stream.Part)
    result = []
    for part in parts:
        # print(part)
        # ISSUE 1: Wrong time signature
        # print(part.timeSignature)
        # part.timeSignature = meter.TimeSignature('3/4')
        # print(part.timeSignature)

        # flatten unnecessary voices in a part so that the converted notes list looks more like MusicXML structure
        # part = part.flattenUnnecessaryVoices(force=True)
        # print(part)
        offset = 0.0
        prevOffset = 0.0
        noteList = []
        for singleNote in part.flat.notes:
            if (len(result) == 0 and len(noteList) == 0):
            # if (len(result) == 0):
                if (type(singleNote) == note.Rest):
                    # print("Rest before the first note!")
                    continue
                # Update offset as the offset of the first note of the piece
                elif (type(singleNote) == note.Note):
                    offset = singleNote.offset
                    # print("offset updated! Current offset: ", offset)
            if (singleNote.offset == prevOffset):
                noteList.append(singleNote)
                # print(len(result))
            else:
                noteList.sort(key=lambda x: x.quarterLength)
                for oneNote in noteList:
                    result.append(oneNote)
                    # print(oneNote, oneNote.offset, oneNote.quarterLength)
                noteList = [singleNote]
                prevOffset = singleNote.offset
            # print(singleNote, singleNote.offset, singleNote.quarterLength)
    # print(result)
    # print("-------------------------------------------------")
    return (result, offset)


def stream2list(str):
    # str.show('text')
    result = []
    offset = 0.0
    for singleNote in str.semiFlat.notes:
        if (len(result) == 0):
            if (type(singleNote) == note.Rest):
                continue
            elif (type(singleNote) == note.Note):
                offset = singleNote.offset
        result.append(singleNote)
        # print(singleNote, singleNote.offset, singleNote.quarterLength)
    result.sort(key=noteSort)
    return (result, offset)

def printNotesList(lst, offset):
    for singleNote in lst:
        if (type(singleNote) != chord.Chord):
            print(singleNote.pitch.name, singleNote.offset - offset, singleNote.quarterLength)
        else:
            print(singleNote, singleNote.offset - offset, singleNote.quarterLength)


def getScore(originalList, userList, originalOffset, userOffset):
    unitScore = 100 / len(originalList)
    i = 0
    j = 0
    score = 100
    while (i < len(originalList) and j < len(userList)):
        correctNote = originalList[i]
        userNote = userList[j]
        # TYPE 1: Chords
        if (type(correctNote) == chord.Chord or type(userNote) == chord.Chord):
            # CASE 1: Wrong note with the correct note
            if (type(correctNote) != chord.Chord and correctNote.pitch in userNote.pitches):
                score -= unitScore / 2
                print("CASE 1")
            # CASE 2-a: Wrong note without the correct note
            elif (type(userNote) != chord.Chord):
                score -= unitScore
                print("CASE 2-a")
            # both notes are chords, so compare their pitches
            else:
                deductionUnit = max(len(correctNote.pitches), len(userNote.pitches))
                for pitch in correctNote.pitches:
                    # CASE 2-b: Wrong note without the correct note
                    # TODO: Chord comparison
                    if pitch in userNote.pitches:
                        print("CASE 2-b")
                        deductionUnit -= 1
                assert(deductionUnit >= 0)
                score -= deductionUnit * unitScore
            print(correctNote, userNote)
        # TYPE 2: Notes
        else:
            # compare their relative offsets
            # if two notes have the same offset
            if (correctNote.offset - originalOffset == userNote.offset - userOffset):
                # CASE 2-c: Wrong note without the correct note
                if (correctNote.pitch.name != userNote.pitch.name):
                    score -= unitScore
                    print("CASE 2-c")
                    print("correct: ", correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
                    print("user: ", userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
                    print("--")
                # CASE 3-a: Shorter/longer note
                elif (correctNote.quarterLength != userNote.quarterLength):
                    deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                    score -= deduction
                    print("CASE 3-a")
                    print("correct: ", correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
                    print("user: ", userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
                    print("--")
            # if two notes have different offsets
            else:
                if (correctNote.pitch.name == userNote.pitch.name):
                    # CASE 3-b: Shorter/longer note
                    if (correctNote.quarterLength != userNote.quarterLength):
                        deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                        score -= deduction
                        print("CASE 3-b")
                        print("correct: ", correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
                        print("user: ", userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
                        print("converted: ", tempo.convertTempoByReferent(userNote.offset - userOffset, 1, 2))
                        print("converted: ", tempo.convertTempoByReferent(userNote.quarterLength, 1, 2))
                        print("--")
                    # deduct points based on offset difference
                    # print(originalOffset, userOffset)
                    # print(correctNote.offset - originalOffset, userNote.offset - userOffset)
                    # print("correct: ", correctNote, correctNote.offset, correctNote.quarterLength)
                    # print("user: ", userNote, userNote.offset, userNote.quarterLength)
                    if (correctNote.quarterLength == 0):
                        print("Correct note's quarterLength is 0")
                        score -= unitScore
                    else:
                        deduction = unitScore * abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset)) / (correctNote.quarterLength)
                        score -= deduction
                # CASE 4: Missing a note
                else:
                    score -= unitScore
                    j -= 1
                    print("CASE 4")
                    print("correct: ", correctNote.pitch.name, correctNote.offset - originalOffset, correctNote.quarterLength)
                    print("user: ", userNote.pitch.name, userNote.offset - userOffset, userNote.quarterLength)
                    print("converted: ", tempo.convertTempoByReferent(userNote.offset - userOffset, 1, 3))
            # print("correct: ", correctNote.pitch.name, correctNote.offset, correctNote.quarterLength)
            # print("user: ", userNote.pitch.name, userNote.offset, userNote.quarterLength)
        i += 1
        j += 1
        # print(i, j)
    return score


def compare(originalFile, userFile):
    originalStream = xml2stream(originalFile)
    # print(originalStream)
    # originalStream = midi2stream(originalFile)
    userStream = midi2stream(userFile)
    (originalNotesAndRests, originalOffset) = stream2list(originalStream)
    # print(userStream.tempo)
    print("original offset ", originalOffset)
    # userStream.show('text')
    # printNotesList(originalNotesAndRests, originalOffset)
    (userNotesAndRests, userOffset) = score2list(userStream)
    print("user offset", userOffset)
    # printNotesList(userNotesAndRests, userOffset)

    # print(originalNotesAndRests)
    # print(userNotesAndRests)

    totalCorrectNotes = len(originalNotesAndRests)
    totalUserNotes = len(userNotesAndRests)
    # print(totalCorrectNotes, totalUserNotes)

    score = getScore(originalNotesAndRests, userNotesAndRests, originalOffset, userOffset)



    # originalStream.show('text')
    # print("----------------------------")
    # userStream.show('text')
    if (score < 0):
        score = 0
    return score

# print("1. Missing one note: ", compare("midi/original.mxl", "midi/swanWithOneMissingNote.mid"))
# print("2. Missing two consecutive notes: ", compare("midi/original.mxl", "midi/swanWithTwoConsecutiveMissingNotes.mid"))
# print("3. One shorter note: ", compare("midi/original.mxl", "midi/swanWithOneShorterNote.mid"))
# print("4. One wrong note (with the correct note): ", compare("midi/original.mxl", "midi/swanWithOneWrongNoteWithCorrectNote.mid"))
# print("5. One wrong note (without the correct note): ", compare("midi/original.mxl", "midi/swanWithOneWrongNote.mid"))
# print("6. Perfect but rest before starting: ", compare("midi/original.mxl", "midi/swanWithTwoBeatsShifted.mid"))
# print("7. Original with original: ", compare("midi/original.mxl", "midi/myswan2.mid"))
# print("8. Vanessa's input: ", compare("midi/original.musicxml", "midi/test5034.mid"))
# print("9. should be 100: ", compare("midi/original.mxl", "midi/original.mxl"))