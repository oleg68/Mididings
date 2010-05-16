# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import mididings.misc as _misc
import mididings.constants as _constants
from mididings.setup import get_config as _get_config


_NOTE_NUMBERS = {
    'c':   0,
    'c#':  1, 'db':  1,
    'd':   2,
    'd#':  3, 'eb':  3,
    'e':   4,
    'f':   5,
    'f#':  6, 'gb':  6,
    'g':   7,
    'g#':  8, 'ab':  8,
    'a':   9,
    'a#': 10, 'bb': 10,
    'b':  11,
}

_NOTE_NAMES = {
     0: 'c',
     1: 'c#',
     2: 'd',
     3: 'd#',
     4: 'e',
     5: 'f',
     6: 'f#',
     7: 'g',
     8: 'g#',
     9: 'a',
    10: 'a#',
    11: 'b',
}

_CONTROLLER_NAMES = {
     0: 'Bank select (MSB)',
     1: 'Modulation',
     6: 'Data entry (MSB)',
     7: 'Volume',
    10: 'Pan',
    11: 'Expression',
    32: 'Bank select (LSB)',
    38: 'Data entry (LSB)',
    64: 'Sustain',
    65: 'Portamento',
    66: 'Sostenuto',
    67: 'Soft pedal',
    68: 'Legato pedal',
    98: 'NRPN (LSB)',
    99: 'NRPN (MSB)',
   100: 'RPN (LSB)',
   101: 'RPN (MSB)',
   121: 'Reset all controllers',
   123: 'All notes off',
}


def note_number(note, check=True):
    """
    Convert note name/number to MIDI note number.
    """
    try:
        # already a number?
        r = int(note)
    except Exception:
        note = note.lower()
        # find first digit
        for i in range(len(note)):
            if note[i].isdigit() or note[i] == '-':
                break
        try:
            name = note[:i]
            octave = int(note[i:])
            r = _NOTE_NUMBERS[name] + (octave + _get_config('octave_offset')) * 12
        except Exception:
            raise ValueError("invalid note name '%s'" % note)

    if check and (r < 0 or r > 127):
        raise ValueError("note number %d is out of range" % r)
    return r


def note_range(notes):
    """
    Convert note range to tuple of MIDI note numbers.
    """
    try:
        # single note
        n = note_number(notes)
        return (n, n + 1)
    except Exception:
        if isinstance(notes, tuple):
            # tuple of note numbers
            return note_number(notes[0]), note_number(notes[1])
        else:
            try:
                # note range string
                nn = notes.split(':', 1)
                lower = note_number(nn[0]) if nn[0] else 0
                upper = note_number(nn[1]) if nn[1] else 0
                return lower, upper
            except ValueError:
                raise ValueError("invalid note range '%s'" % notes)


def note_name(note):
    """
    Get note name from MIDI note number.
    """
    return _NOTE_NAMES[note % 12] + str((note / 12) - _get_config('octave_offset'))


def tonic_note_number(key):
    return _NOTE_NUMBERS[key]


def controller_name(ctrl):
    """
    Get controller description.
    """
    if ctrl in _CONTROLLER_NAMES:
        return _CONTROLLER_NAMES[ctrl]
    else:
        return None


def event_type(type):
    """
    Check and return event type.
    """
    if type not in (1 << x for x in range(_constants._NUM_EVENT_TYPES)):
        raise ValueError("invalid event type %r" % type)
    return type


def port_number(port):
    """
    Convert port number/name to actual port number.
    """
    if isinstance(port, int):
        return actual(port)
    else:
        # XXX workaround for circular absolute imports
        import mididings.engine as engine

        in_ports = engine.get_in_ports()
        out_ports = engine.get_out_ports()
        is_in = (_misc.issequence(in_ports) and port in in_ports)
        is_out = (_misc.issequence(out_ports) and port in out_ports)

        if is_in and is_out and in_ports.index(port) != out_ports.index(port):
            raise ValueError("port name '%s' is ambiguous" % port)
        elif is_in:
            return in_ports.index(port)
        elif is_out:
            return out_ports.index(port)
        else:
            raise ValueError("invalid port name '%s'" % port)


def channel_number(channel):
    r = actual(channel)
    if r < 0 or r > 15:
        raise ValueError("channel number %d is out of range" % channel)
    return r


def program_number(program, check=True):
    r = actual(program)
    if check and (r < 0 or r > 127):
        raise ValueError("program number %d is out of range" % program)
    return r


def ctrl_number(ctrl):
    if ctrl < 0 or ctrl > 127:
        raise ValueError("controller number %d is out of range" % ctrl)
    return ctrl


def ctrl_value(value, check=True):
    if check and (value < 0 or value > 127):
        raise ValueError("controller value %d is out of range" % value)
    return value


def velocity_value(velocity, check=True):
    if check and (velocity < 0 or velocity > 127):
        raise ValueError("velocity %d is out of range" % velocity)
    return velocity


def scene_number(scene):
    return actual(scene)


def sysex_data(sysex, allow_partial=False):
    sysex = _misc.seq_to_string(sysex)
    if len(sysex) < 2:
        raise ValueError("sysex too short")
    elif sysex[0] != '\xf0':
        raise ValueError("sysex doesn't start with F0")
    elif sysex[-1] != '\xf7' and not allow_partial:
        raise ValueError("sysex doesn't end with F7")
    elif any(ord(c) > 127 for c in sysex[1:-1]):
        raise ValueError("sysex data byte out of range")
    return sysex


def sysex_manufacturer(manufacturer):
    if not _misc.issequence(manufacturer, True):
        manufacturer = [manufacturer]
    manid = _misc.seq_to_string(manufacturer)
    if len(manid) not in (1, 3):
        raise ValueError("manufacturer id must be either one or three bytes")
    elif len(manid) == 3 and manid[0] != '\x00':
        raise ValueError("three-byte manufacturer id must start with null byte")
    elif any(ord(c) > 127 for c in manid):
        raise ValueError("manufacturer id out of range")
    return manid


class NoDataOffset(int):
    """
    An integer type that's unaffected by data offset conversions.
    """
    def __new__(cls, value):
        return int.__new__(cls, value)
    def __repr__(self):
        return 'NoDataOffset(%d)' % self
    def __str__(self):
        return 'NoDataOffset(%d)' % self


def offset(n):
    """
    Add current data offset.
    """
    return n + _get_config('data_offset')


def actual(n):
    """
    Subtract current data offset to get the "real" value used on the C++ side.
    """
    if isinstance(n, NoDataOffset):
        return int(n)
    else:
        return n - _get_config('data_offset')
