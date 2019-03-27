import copy

def organizeComponents(connectedComponents, lineDist):
    allMeasures = reorganizeNotesByMeasure(connectedComponents)
    allMeasures = putAccentsOnNotes(allMeasures, lineDist)
    return allMeasures

def reorganizeNotesByStaffLoc(connectedComponents):
    allNotesRestsAccents = []
    maxStaff = None
    for comp in connectedComponents:
        if comp.typeName == "note" or comp.typeName == "rest" or comp.typeName == "accent" or comp.typeName == "measure bar":
            allNotesRestsAccents.append(comp)
            if maxStaff == None or comp.staff > maxStaff:
                maxStaff = comp.staff
    notesByStaff = [[] for i in range(maxStaff)]
    for item in allNotesRestsAccents:
        notesByStaff[item.staff-1].append(item)
    fullList = []
    for staff in notesByStaff:
        staff.sort(key=lambda note: note.x0)
        fullList.append(staff)
    return fullList

def reorganizeNotesByMeasure(connectedComponents):
    reorgByStaffLoc = reorganizeNotesByStaffLoc(connectedComponents)
    measures = []
    curMeasureStaff1 = []
    curMeasureStaff2 = []
    for staffNum in range(0, len(reorgByStaffLoc), 2):
        staff1 = reorgByStaffLoc[staffNum]
        staff2 = reorgByStaffLoc[staffNum+1]
        staff1ElemNum = 0
        staff2ElemNum = 0
        curStaff = 1
        while (staff2ElemNum < len(staff2)):
            if curStaff == 1:
                noteElem = staff1[staff1ElemNum]
                staff1ElemNum += 1
            else:
                noteElem = staff2[staff2ElemNum]
                staff2ElemNum += 1
            if curStaff == 1 and curMeasureStaff1 == [] and (noteElem.typeName == "measure bar" or noteElem.typeName == "accent"):
                continue
            if curStaff == 2 and curMeasureStaff2 == [] and (noteElem.typeName == "measure bar" or noteElem.typeName == "accent"):
                continue
            if noteElem.typeName == "measure bar":
                if curStaff == 1:
                    curStaff = 2
                elif curStaff == 2:
                    measures.append(curMeasureStaff1+curMeasureStaff2)
                    curMeasureStaff1 = []
                    curMeasureStaff2 = []
                    curStaff = 1
            else:
                if curStaff == 1:
                    curMeasureStaff1.append(noteElem)
                else:
                    curMeasureStaff2.append(noteElem)
    if curMeasureStaff1 != [] or curMeasureStaff2 != []:
        measures.append(curMeasureStaff1+curMeasureStaff2)
    return measures

#####REORGANIZE NOTES BY PUTTING ACCENTS ON NOTES

def putAccentsOnNotes(allMeasures, distBetweenStaffLines):
    newAllMeasures = []
    accentToNoteDistThreshold = distBetweenStaffLines * 2
    flatsSharps = getFlatsSharps(allMeasures[0], accentToNoteDistThreshold=accentToNoteDistThreshold)
    for measureNum in range(len(allMeasures)):
        measure = allMeasures[measureNum]
        newMeasure = putAccentsOnNotesInMeasure(measure, accentToNoteDistThreshold, copy.copy(flatsSharps))
        newAllMeasures.append(newMeasure)
    return newAllMeasures

def getFlatsSharps(firstMeasure, accentToNoteDistThreshold):
    keySig = 0
    noteElemIndex = 0
    noteElem = firstMeasure[noteElemIndex]
    lastNote = None
    while noteElem.typeName == "accent":
        if noteElem.subTypeName == "sharp":
            keySig += 1
        elif noteElem.subTypeName == "flat":
            keySig -= 1
        lastNote = noteElem
        noteElemIndex += 1
        noteElem = firstMeasure[noteElemIndex]
    if noteElem.typeName == "rest":
        # a rest cannot have a sharp or flat, all previous ones must be part of keySig
        return getKeySigDict(keySig=keySig)
    elif lastNote == None:
        assert(keySig == 0)
        return getKeySigDict(keySig=keySig)
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
                return getKeySigDict(keySig=keySig)
        # All pitches were far enough away
        return getKeySigDict(keySig=keySig)


def putDotOnNote(noteElem, dotElem, accentToNoteDistThreshold):
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

def putAccentOnNote(noteElem, accentElem, flatsSharps, accentToNoteDistThreshold):
    # need to alter a pitch, but which one
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


def putAccentsOnNotesInMeasure(measure, accentToNoteDistThreshold, flatsSharps):
    newMeasure = []
    lastAccentBeforeNoteRest = None
    seenNoteRest = False
    alterNextNote = False
    for noteElemNum in range(len(measure)):
        noteElem = measure[noteElemNum]
        if seenNoteRest == False and noteElem.typeName == "accent":
            lastAccentBeforeNoteRest = noteElem
            alterNextNote = True
            # we don't want to actually add the accent itself
            continue
        elif seenNoteRest == False and (noteElem.typeName == "note" or noteElem.typeName == "flat"):
            seenNoteRest = True

        if noteElem.typeName == "accent":
            lastAccentBeforeNoteRest = None
            alterNextNote = None
            if noteElem.subTypeName == "dot" and len(newMeasure)>0:
                # look at last note in the measure
                lastNote = newMeasure[-1]
                if lastNote.typeName == "note":
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

        elif noteElem.typeName == "rest":
            # cannot do anything accent-wise to  rest, but reset any other accent information
            newMeasure.append(noteElem)
            alterNextNote = None
            lastAccentBeforeNoteRest = None

        elif noteElem.typeName == "note":
            newMeasure.append(noteElem)
            noteElem.dottedPitches = [False]*len(noteElem.pitches)
            noteElem.alterPitches = ["natural"]*len(noteElem.pitches)
            if lastAccentBeforeNoteRest != None and alterNextNote != None:
                putAccentOnNote(noteElem, lastAccentBeforeNoteRest, flatsSharps, accentToNoteDistThreshold)
            # need to check if the key or other accidentals in the measure alter each pitch
            for pitchIndex in range(len(noteElem.pitches)):
                pitch = noteElem.pitches[pitchIndex]["step"]
                noteElem.alterPitches[pitchIndex] = flatsSharps[pitch]

    return newMeasure


def getKeySigDict(keySig):
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
