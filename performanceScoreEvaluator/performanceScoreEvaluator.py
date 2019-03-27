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

def score2list(score):
    # score.show('text')
    print("----------------------------------")
    parts = score.getElementsByClass(stream.Part)
    result = []
    for part in parts:
        print(part)
        # ISSUE 1: Wrong time signature
        # print(part.timeSignature)
        # part.timeSignature = meter.TimeSignature('3/4')
        # print(part.timeSignature)

        # flatten unnecessary voices in a part so that the converted notes list looks more like MusicXML structure
        part = part.flattenUnnecessaryVoices(force=True)
        offset = 0.0
        prevOffset = 0.0
        noteList = []
        for singleNote in part.flat.notes:
            if (len(result) == 0):
                if (type(singleNote) == note.Rest):
                    continue
                # Update offset as the offset of the first note of the piece
                elif (type(singleNote) == note.Note):
                    offset = singleNote.offset
                    # print("offset updated! Current offset: ", offset)
            if (singleNote.offset == prevOffset):
                noteList.append(singleNote)
            else:
                for oneNote in noteList:
                    result.append(oneNote)
                    print(oneNote, oneNote.offset, oneNote.quarterLength)
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
        print(singleNote, singleNote.offset, singleNote.quarterLength)
    return (result, offset)



def getScore(originalList, userList, i, j, score, originalOffset, userOffset):
    unitScore = 100 / len(originalList)
    while (i < len(originalList) and j < len(userList)):
        correctNote = originalList[i]
        userNote = userList[j]
        # CASE 1: Chords
        if (type(correctNote) == chord.Chord or type(userNote) == chord.Chord):
            # CASE 1: Wrong note with the correct note
            if (type(correctNote) != chord.Chord and correctNote.pitch in userNote.pitches):
                score -= unitScore / 2
            # CASE 2-a: Wrong note without the correct note
            elif (type(userNote) != chord.Chord):
                score -= unitScore
            # both notes are chords, so compare their pitches
            else:
                deductionUnit = max(len(correctNote.pitches), len(userNote.pitches))
                for pitch in correctNote.pitches:
                    # CASE 2-b: Wrong note without the correct note
                    # TODO: Chord comparison
                    if pitch in userNote.pitches:
                        deductionUnit -= 1
                assert(deductionUnit >= 0)
                score -= deductionUnit * unitScore
        else:
            # compare their relative offsets
            # if two notes have the same offset
            if (correctNote.offset - originalOffset == userNote.offset - userOffset):
                # CASE 2-c: Wrong note without the correct note
                if (correctNote.pitch != userNote.pitch):
                    score -= unitScore
                # CASE 3-a: Shorter/longer note
                elif (correctNote.quarterLength != userNote.quarterLength):
                    deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                    score -= deduction
            # if two notes don't have the same offset
            else:
                if (correctNote.pitch == userNote.pitch):
                    # CASE 3-b: Shorter/longer note
                    if (correctNote.quarterLength != userNote.quarterLength):
                        deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                        score -= deduction
                    # deduct points based on offset difference
                    # print(originalOffset, userOffset)
                    # print(correctNote.offset - originalOffset, userNote.offset - userOffset)
                    # print("correct: ", correctNote, correctNote.offset, correctNote.quarterLength)
                    # print("user: ", userNote, userNote.offset, userNote.quarterLength)
                    deduction = unitScore * abs((correctNote.offset - originalOffset) - (userNote.offset - userOffset)) / (correctNote.quarterLength)
                    score -= deduction
                # CASE 4: Missing a note
                else:
                    score -= unitScore
                    j -= 1
        i += 1
        j += 1
    return score


def compare(originalFile, userFile):
    originalStream = xml2stream(originalFile)
    # print(originalStream)
    # originalStream = midi2stream(originalFile)
    userStream = midi2stream(userFile)
    (originalNotesAndRests, originalOffset) = stream2list(originalStream)
    # print("original offset ", originalOffset)
    (userNotesAndRests, userOffset) = score2list(userStream)
    # print("user offset", userOffset)

    # print(originalNotesAndRests)
    # print(userNotesAndRests)

    totalCorrectNotes = len(originalNotesAndRests)
    totalUserNotes = len(userNotesAndRests)
    # print(totalCorrectNotes, totalUserNotes)

    score = getScore(originalNotesAndRests, userNotesAndRests, 0, 0, 100, originalOffset, userOffset)



    # originalStream.show('text')
    # userStream.show('text')
    if (score < 0):
        score = 0
    return score

# print("1. Missing one note: ", compare("midi/swan.mid", "midi/swanWithOneMissingNote.mid"))
# print("2. Missing two consecutive notes: ", compare("midi/swan.mid", "midi/swanWithTwoConsecutiveMissingNotes.mid"))
# print("3. One shorter note: ", compare("midi/swan.mid", "midi/swanWithOneShorterNote.mid"))
# print("4. One wrong note (with the correct note): ", compare("midi/swan.mid", "midi/swanWithOneWrongNoteWithCorrectNote.mid"))
# print("5. One wrong note (without the correct note): ", compare("midi/swan.mid", "midi/swanWithOneWrongNote.mid"))
# print("6. Perfect but rest before starting: ", compare("midi/swan.mid", "midi/swanWithTwoBeatsShifted.mid"))
print("7. Original with original: ", compare("midi/original.musicxml", "midi/myswan2.mid"))
# print("8. Vanessa's input: ", compare("midi/vanessa.mid", "midi/swan.mid"))