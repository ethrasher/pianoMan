import copy
from connectedCompObj import NoteComponent, RestComponent, MeasureBarComponent, AccentComponent
import cv2

def organizeComponents(connectedComponents, lineDist, binaryImg):
    # DESCRIPTION: organizes the connectedComponents into a way the xml generator can use
    # PARAMETERS: connectedComponents: a list of connected components with all features detected
    #               lineDist: the median distance between staff lines
    # RETURN: a list of all measures of ordered notes and rests
    allMeasures = reorganizeNotesByMeasure(connectedComponents, binaryImg)
    allMeasures, keySig = putAccentsOnNotes(allMeasures, lineDist)
    return allMeasures, keySig

def reorganizeNotesByMeasure(connectedComponents, binaryImg):
    # DESCRIPTION: organizes the components by what measure they are in, and then based on staff and x position
    # PARAMETERS: connectedComponents: a 2D list of connectedComponent objects with no organization
    # RETURN: a list of all measures, each measure is a list containing all connected component objects in order of
    #           each note on the first staff (ordered by x location) and then the second staff
    reorgByStaffLoc = reorganizeNotesByStaffLoc(connectedComponents)

    measures = []
    for staffNum in range(0, len(reorgByStaffLoc), 2):
        staff1 = reorgByStaffLoc[staffNum]
        staff2 = reorgByStaffLoc[staffNum+1]
        staff1Measures = []
        curStaff1Measure = []
        staff2Measures = []
        curStaff2Measure = []
        for i in range(len(staff1)):
            curElem = staff1[i]
            if isinstance(curElem, MeasureBarComponent):
                staff1Measures.append(curStaff1Measure)
                curStaff1Measure = []
            else:
                curStaff1Measure.append(curElem)
        if curStaff1Measure != []:
            staff1Measures.append(curStaff1Measure)
        for i in range(len(staff2)):
            curElem = staff2[i]
            if isinstance(curElem, MeasureBarComponent):
                staff2Measures.append(curStaff2Measure)
                curStaff2Measure = []
            else:
                curStaff2Measure.append(curElem)
        if curStaff2Measure != []:
            staff2Measures.append(curStaff2Measure)
        assert(len(staff1Measures) == len(staff2Measures))
        for i in range(len(staff1Measures)):
            if staff1Measures[i] != [] or staff2Measures[i]!=[]:
                measures.append(staff1Measures[i]+staff2Measures[i])
    return measures

def reorganizeNotesByStaffLoc(connectedComponents):
    # DESCRIPTION: organizes the components by what staff they are on, and then based on x position
    # PARAMETERS: connectedComponents: a list of connectedComponent objects with no organization
    # RETURN: a list of all staffs, where each staff is is a list of connected components organized by x location
    allNotesRestsAccents = []
    maxStaff = None
    for comp in connectedComponents:
        if isinstance(comp, NoteComponent) or isinstance(comp, RestComponent) or isinstance(comp, AccentComponent) or isinstance(comp, MeasureBarComponent):
            allNotesRestsAccents.append(comp)
            if maxStaff == None or comp.staff > maxStaff:
                maxStaff = comp.staff
    notesByStaff = [[] for i in range(maxStaff)]
    for item in allNotesRestsAccents:
        notesByStaff[item.staff-1].append(item)
    fullList = []
    for staff in notesByStaff:
        staff.sort(key=lambda note: note.x0)
        # remove anything before the first measure bar location
        itemNum = 0
        while(not isinstance(staff[itemNum], MeasureBarComponent)):
            itemNum += 1
        staff = staff[itemNum:]

        fullList.append(staff)
    return fullList

def putAccentsOnNotes(allMeasures, distBetweenStaffLines):
    # DESCRIPTION: alters and/or dots each note by if they have an accidental or based on key signature or if they have a dot
    # PARAMETERS: allMeasures: a list of connectedComponent objects organized by measure
    #                   distBetweenStaffLines: the median distance between staff lines
    # RETURN: a list of all measures where each staff is is a list of notes and rests altered by dots and sharps/flats/naturals/key sigs
    newAllMeasures = []
    accentToNoteDistThreshold = distBetweenStaffLines * 2
    flatsSharps, keySig = getFlatsSharps(allMeasures[0], accentToNoteDistThreshold=accentToNoteDistThreshold)
    for measureNum in range(len(allMeasures)):
        measure = allMeasures[measureNum]
        newMeasure = putAccentsOnNotesInMeasure(measure, accentToNoteDistThreshold, copy.copy(flatsSharps), measureNum)
        if newMeasure != []:
            newAllMeasures.append(newMeasure)
    return newAllMeasures, keySig

def getFlatsSharps(firstMeasure, accentToNoteDistThreshold):
    # DESCRIPTION: takes the first measure and returns a dictionary for the keysig
    # PARAMETERS: firstMeasure: a list of connectedComponent objects in the first measure fully organized
    #               accentToNoteDistThreshold: the furthest an accent can be away from a note and still considered part of it
    # RETURN: a dictionary of pitch ('A', 'B', ...) to any alters for that pitch based on the found key signature
    keySig = 0
    noteElemIndex = 0
    noteElem = firstMeasure[noteElemIndex]
    lastNote = None
    #print(firstMeasure[0].subTypeName)
    #firstMeasure[0].drawComponentOnCanvas()
    #cv2.waitKey(0)

    while isinstance(noteElem, AccentComponent):
        if noteElem.subTypeName == "sharp":
            keySig += 1
        elif noteElem.subTypeName == "flat":
            keySig -= 1
        lastNote = noteElem
        noteElemIndex += 1
        #print(noteElemIndex)
        noteElem = firstMeasure[noteElemIndex]
    if isinstance(noteElem, RestComponent):
        # a rest cannot have a sharp or flat, all previous ones must be part of keySig
        return getKeySigDict(keySig=keySig), keySig
    elif lastNote == None:
        assert(keySig == 0)
        return getKeySigDict(keySig=keySig), keySig
    else:
        # need to check that the last note is actually part of the keySig and not part of the first note
        # need to check each pitch in this note and the dist between them and accent
        accentCenterX = (lastNote.x0 + lastNote.x1)/2
        accentCenterY = (lastNote.y0 + lastNote.y1)/2
        for pitchCircle in noteElem.circles[0, :]:
            pitchCircleY = pitchCircle[1]+noteElem.y0
            pitchCircleX = pitchCircle[0]+noteElem.x0
            accentToNoteDist = ((accentCenterX-pitchCircleX)**2 + (accentCenterY-pitchCircleY)**2)**.5
            if accentToNoteDist <= accentToNoteDistThreshold:
                # close enough to be considered part of the note itself
                # need to correct for the extra one added/subtracted to keySig
                if lastNote.subTypeName == "sharp":
                    keySig -= 1
                elif lastNote.subTypename == "flat":
                    keySig += 1
                return getKeySigDict(keySig=keySig), keySig
        # All pitches were far enough away
        return getKeySigDict(keySig=keySig), keySig


def putDotOnNote(noteElem, dotElem, accentToNoteDistThreshold):
    # DESCRIPTION: attempts to place the dot on the last note found
    # PARAMETERS: noteElem: the last note found that we might attach a dot to
    #               dotElem: the connectedComponent representing a dot accent
    #               accentToNoteDistThreshold: the furthest an accent can be away from a note and still considered part of it
    # RETURN: None
    if len(noteElem.pitches) == 1:
        # easy case, only one pitch to dot
        noteElem.dottedPitches[0] = True
    else:
        # need to figure out which pitch is closest to the dot
        dotCenterX = (dotElem.x0 + dotElem.x1)/2
        dotCenterY = (dotElem.y0 + dotElem.y1)/2
        bestPitchIndex = None
        bestPitchDist = None
        pitchIndex = 0
        for pitchCircle in noteElem.circles[0, :]:
            pitchCircleY = pitchCircle[1]+noteElem.y0
            pitchCircleX = pitchCircle[0]+noteElem.x0
            dotToNoteDist = ((dotCenterX-pitchCircleX)**2 + (dotCenterY-pitchCircleY)**2)**.5
            if dotToNoteDist <= accentToNoteDistThreshold and  (bestPitchDist == None or dotToNoteDist < bestPitchDist):
                bestPitchDist = dotToNoteDist
                bestPitchIndex = pitchIndex
            pitchIndex += 1
        if bestPitchIndex != None:
            noteElem.dottedPitches[bestPitchIndex] = True

def putAccidentalOnNote(noteElem, accentElem, flatsSharps, accentToNoteDistThreshold, measureNum):
    # DESCRIPTION: attempts to alter one of the pitches in the note based on accidentals
    # PARAMETERS: noteElem: the note component where one pitch should be altered
    #               accentElem: the connectedComponent representing an accidental
    #               flatsSharps: the dictionary of pitches and how to alter them for this measure
    #               accentToNoteDistThreshold: the furthest an accent can be away from a note and still considered part of it
    # RETURN: None
    if len(noteElem.pitches) == 1:
        # easy case, only one pitch to change
        noteElem.alterPitches[0] = accentElem.subTypeName
        alteredPitchStep = noteElem.pitches[0]["step"]
        flatsSharps[alteredPitchStep] = accentElem.subTypeName
    else:
        # need to find which pitch is the closest
        accentCenterX = (accentElem.x0 + accentElem.x1) / 2
        accentCenterY = (accentElem.y0 + accentElem.y1) / 2
        bestPitchIndex = None
        bestPitchDist = None
        pitchIndex = 0
        for pitchCircle in noteElem.circles[0, :]:
            pitchCircleY = pitchCircle[1] + noteElem.y0
            pitchCircleX = pitchCircle[0] + noteElem.x0
            accentToNoteDist = ((accentCenterX - pitchCircleX) ** 2 + (accentCenterY - pitchCircleY) ** 2) ** .5
            if accentToNoteDist <= accentToNoteDistThreshold and (bestPitchDist == None or accentToNoteDist < bestPitchDist):
                bestPitchIndex = pitchIndex
                bestPitchDist = accentToNoteDist
            pitchIndex += 1
        if bestPitchIndex != None:
            noteElem.alterPitches[bestPitchIndex] = accentElem.subTypeName
            alteredPitchStep = noteElem.pitches[bestPitchIndex]["step"]
            flatsSharps[alteredPitchStep] = accentElem.subTypeName


def putAccentsOnNotesInMeasure(measure, accentToNoteDistThreshold, flatsSharps, measureNum):
    # DESCRIPTION: attempts to alter each of the notes in the measure based on accidentals, key sig, and dots
    # PARAMETERS: measure: the list of notes, rests, and accents in the measure ordered fully
    #               accentToNoteDistThreshold: the furthest an accent can be away from a note and still considered part of it
    #               flatsSharps: the dictionary of pitches and how to alter them for this measure
    # RETURN: a new list of all the notes and rests in the measure, altered by their accents and key sig
    newMeasure = []
    lastAccentBeforeNoteRest = None
    seenNoteRest = False
    alterNextNote = False
    for noteElemNum in range(len(measure)):
        noteElem = measure[noteElemNum]
        if seenNoteRest == False and isinstance(noteElem, AccentComponent):
            lastAccentBeforeNoteRest = noteElem
            alterNextNote = True
            # we don't want to actually add the accent itself
            continue
        elif seenNoteRest == False and (isinstance(noteElem, NoteComponent) or isinstance(noteElem, RestComponent)):
            seenNoteRest = True

        if isinstance(noteElem, AccentComponent):
            lastAccentBeforeNoteRest = None
            alterNextNote = None
            if noteElem.subTypeName == "dot" and len(newMeasure)>0:
                # look at last note in the measure
                lastNote = newMeasure[-1]
                if isinstance(lastNote, NoteComponent) and lastNote.staff == noteElem.staff:
                    putDotOnNote(noteElem=lastNote, dotElem=noteElem, accentToNoteDistThreshold=accentToNoteDistThreshold)
            elif noteElem.subTypeName == "sharp":
                lastAccentBeforeNoteRest = noteElem
                alterNextNote = True
            elif noteElem.subTypeName == "flat":
                lastAccentBeforeNoteRest = noteElem
                alterNextNote = True
            elif noteElem.subTypeName == "natural":
                lastAccentBeforeNoteRest = noteElem
                alterNextNote = True
            elif noteElem.subTypeName == "tie" or noteElem.subTypeName == "other":
                #ignore this case, not doing anything with these accents for now
                pass
            else:
                raise Exception("Unknown Accent type: "+noteElem.subTypeName)

        elif isinstance(noteElem, RestComponent):
            # cannot do anything accent-wise to  rest, but reset any other accent information
            newMeasure.append(noteElem)
            alterNextNote = None
            lastAccentBeforeNoteRest = None

        elif isinstance(noteElem, NoteComponent):
            newMeasure.append(noteElem)
            noteElem.dottedPitches = [False]*len(noteElem.pitches)
            noteElem.alterPitches = ["natural"]*len(noteElem.pitches)
            if lastAccentBeforeNoteRest != None and alterNextNote != None and noteElem.staff==lastAccentBeforeNoteRest.staff:
                putAccidentalOnNote(noteElem, lastAccentBeforeNoteRest, flatsSharps, accentToNoteDistThreshold, measureNum)
            # need to check if the key or other accidentals in the measure alter each pitch
            for pitchIndex in range(len(noteElem.pitches)):
                pitch = noteElem.pitches[pitchIndex]["step"]
                noteElem.alterPitches[pitchIndex] = flatsSharps[pitch]
            lastAccentBeforeNoteRest = None
            alterNextNote = None

    return newMeasure


def getKeySigDict(keySig):
    # DESCRIPTION: returns the dictionary of what notes are changed from the key signature
    # PARAMETERS: keySig: int representing how many sharps (+1) or flats(-1) for this keySignature
    # RETURN: a dictionary of each pitch and whether it is flat, sharp or natural
    sharpsFlats = {"A":"natural", "B":"natural", "C":"natural", "D":"natural", "E":"natural", "F":"natural", "G":"natural"}
    if keySig >= 1:
        sharpsFlats["F"] = "sharp"
    if keySig >= 2:
        sharpsFlats["C"] = "sharp"
    if keySig >= 3:
        sharpsFlats["G"] = "sharp"
    if keySig >= 4:
        sharpsFlats["D"] = "sharp"
    if keySig >= 5:
        sharpsFlats["A"] = "sharp"
    if keySig >= 6:
        sharpsFlats["E"] = "sharp"
    if keySig >= 7:
        sharpsFlats["B"] = "sharp"
    if keySig <= -1:
        sharpsFlats["B"] = "flat"
    if keySig <= -2:
        sharpsFlats["E"] = "flat"
    if keySig <= -3:
        sharpsFlats["A"] = "flat"
    if keySig <= -4:
        sharpsFlats["D"] = "flat"
    if keySig <= -5:
        sharpsFlats["G"] = "flat"
    if keySig <= -6:
        sharpsFlats["C"] = "flat"
    if keySig <= -7:
        sharpsFlats["F"] = "flat"
    return sharpsFlats
