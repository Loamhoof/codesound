from collections import namedtuple
from itertools import chain, groupby
from operator import attrgetter
from time import sleep

from mingus.midi import fluidsynth
from mingus.containers import Note, NoteContainer


NOTE_RANGE = 5
SPEED = 0.05
TimedNote = namedtuple('TimedNote', ('time', 'note'))
TimedNoteContainer = namedtuple('TimedNote', ('time', 'container'))


def init(soundfont_path='FluidR3_GM.sf2', driver='alsa'):
    fluidsynth.init(soundfont_path, driver)


def play_file(file_path='samplefile.py'):
    with open(file_path) as file_descriptor:
        lengths = list(map(len, file_descriptor))

    timed_notes = []
    for index_len, length in enumerate(lengths, 1):
        timed_notes.append([
            TimedNote(sum(lengths[index_range:index_len]) - 1, Note(50 + index_range * 4))
            for index_range, note_cap in enumerate(lengths[0:min(index_len, NOTE_RANGE)])
        ])

    sorted_notes = sorted(chain.from_iterable(timed_notes), key=attrgetter('time'))
    timed_containers = [
        TimedNoteContainer(time, NoteContainer(map(attrgetter('note'), timed_notes)))
        for time, timed_notes in groupby(sorted_notes, key=attrgetter('time'))
    ]

    current_time = 0
    for timed_container in timed_containers:
        sleep((timed_container.time - current_time) * SPEED)
        current_time = timed_container.time
        fluidsynth.play_NoteContainer(timed_container.container)
