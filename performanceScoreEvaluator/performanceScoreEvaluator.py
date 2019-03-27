from music21 import *


def midi2stream(filename):
    mf = midi.MidiFile()
    mf.open(filename)
    mf.read()
    mf.close()
    s = midi.translate.midiFileToStream(mf)
    return s

def score2list(score):
    parts = score.getElementsByClass(stream.Part)
    result = []
    for part in parts:
        # ISSUE 1: Wrong time signature
        # print(part.timeSignature)
        # part.timeSignature = meter.TimeSignature('3/4')
        # print(part.timeSignature)
        # voices = part.getElementsByClass(stream.Voice)
        # for voice in voices:
        #     # print(len(voice.notesAndRests))
        #     numNotesInVoice = 0
        #     if (len(voice.notesAndRests) > 0):
        #         # print(len(voice.notesAndRests))
        #         if (type(voice.notesAndRests[0]) == note.Rest):
        #             # print("rest detected")
        #             voice.remove(voice.notesAndRests[0])
        #     # print("voice")
        #     for n in voice.notesAndRests:
        #         # print(n)
        #         pass
        # flatten unnecessary voices in a part so that the converted notes list looks more like MusicXML structure
        part = part.flattenUnnecessaryVoices(force=True)
        # for singleNote in part.notesAndRests:
        for singleNote in part.flat.notes:
            # print(onenote)
            offset = 0.0
            if (len(result) == 0):
                if (type(singleNote) == note.Rest):
                    continue
                elif (type(singleNote) == note.Note):
                    offset = singleNote.offset
                    print("offset updated! Current offset: ", offset)

            result.append(singleNote)
            print(singleNote, singleNote.activeSite, singleNote.offset)
        # voices = part.getElementsByClass(stream.Voice)
        # for voice in voices:
        #     numNotesInVoice = 0
        #     for noteOrRest in voice.notesAndRests:
        #         if (numNotesInVoice == 0 and type(noteOrRest) == note.Rest):
        #             continue
        #         result.append(noteOrRest)
        #         numNotesInVoice += 1
    print(result)
    print("-------------------------------------------------")
    return (result, offset)

def getScore(originalList, userList, i, j, score):
    # print(i, j)
    unitScore = 100 / len(originalList)
    while (i < len(originalList) and j < len(userList)):
        correctNote = originalList[i]
        userNote = userList[j]
        if (type(correctNote) == chord.Chord or type(userNote) == chord.Chord):
            # wrong note with the correct note
            if (type(correctNote) != chord.Chord and correctNote.pitch in userNote.pitches):
                score -= unitScore / 2
            # wrong note without the correct note
            elif (type(userNote) != chord.Chord):
                score -= unitScore
            # both notes are chords, so compare the pitches
            else:
                deductionUnit = max(len(correctNote.pitches), len(userNote.pitches))
                for pitch in correctNote.pitches:
                    if pitch in userNote.pitches:
                        deductionUnit -= 1
                assert(deductionUnit >= 0)
                score -= deductionUnit * unitScore
        elif (type(correctNote) == note.Rest or type(userNote) == note.Rest):
            pass
        # if pitch of the notes are different, different unitScore
        elif (correctNote.pitch != userNote.pitch):
            # print(correctNote.pitch, userNote.pitch)
            score -= unitScore
            # if (correctNote.duration == userNote.duration):
            #     continue
            # if (abs(i - j) <= 1):
            #     # print(j - i)
            #     score3 = getScore(originalList, userList, i + 1, j, score)
            #     score2 = getScore(originalList, userList, i, j + 1, score)
            #     score1 = getScore(originalList, userList, i + 1, j + 1, score)
            #     # if (j == i + 1):
            #     #     print(score1, score2)
            #     return max(score1, score2, score3)
                # return max(getScore(originalList, userList, i + 1, j + 1, score), getScore(originalList, userList, i, j + 1, score))
        else:
            # if duration of the notes are different, deduct points regarding the duration difference
            if (correctNote.quarterLength != userNote.quarterLength):
            # print(correctNote.pitch, userNote.pitch)
            # print(correctNote.quarterLength, userNote.quarterLength)
                deduction = unitScore * abs(correctNote.quarterLength - userNote.quarterLength) / (correctNote.quarterLength)
                score -= deduction
        i += 1
        j += 1
    return score

def compare(originalFile, userFile):
    originalStream = midi2stream(originalFile)
    userStream = midi2stream(userFile)
    (originalNotesAndRests, originalOffset) = score2list(originalStream)
    (userNotesAndRests, userOffset) = score2list(userStream)

    # print(originalNotesAndRests)
    # print(userNotesAndRests)

    totalCorrectNotes = len(originalNotesAndRests)
    totalUserNotes = len(userNotesAndRests)
    # print(totalCorrectNotes, totalUserNotes)

    score = getScore(originalNotesAndRests, userNotesAndRests, 0, 0, 100)



    # originalStream.show('text')
    # userStream.show('text')
    return score

print("1. Missing one note: ", compare("midi/swan.mid", "midi/swanWithOneMissingNote.mid"))
# print("2. Missing two consecutive notes: ", compare("midi/swan.mid", "midi/swanWithTwoConsecutiveMissingNotes.mid"))
# print("3. One shorter note: ", compare("midi/swan.mid", "midi/swanWithOneShorterNote.mid"))
# print("4. One wrong note (with the correct note): ", compare("midi/swan.mid", "midi/swanWithOneWrongNoteWithCorrectNote.mid"))
# print("5. One wrong note (without the correct note): ", compare("midi/swan.mid", "midi/swanWithOneWrongNote.mid"))
print("6. Perfect but rest before starting: ", compare("midi/swan.mid", "midi/swanWithTwoBeatsShifted.mid"))
# print("7. Original with original: ", compare("midi/swan.mid", "midi/swan.mid"))
# print("8. Vanessa's input: ", compare("midi/vanessa.mid", "midi/swan.mid"))