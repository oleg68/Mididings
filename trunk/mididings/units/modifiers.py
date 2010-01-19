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

import _mididings

from mididings.units.base import _Unit, _unit_repr
from mididings.units.base import Chain, Filter, Split, Pass
from mididings.units.splits import VelocitySplit
from mididings.units.generators import NoteOn, NoteOff

import mididings.util as _util
import mididings.misc as _misc
import mididings.constants as _constants


@_unit_repr
def Port(port):
    return _Unit(_mididings.Port(_util.port_number(port)))


@_unit_repr
def Channel(channel):
    return _Unit(_mididings.Channel(_util.channel_number(channel)))


@_unit_repr
def Transpose(offset):
    return _Unit(_mididings.Transpose(offset))


def Note(note):
    return Filter(_constants.NOTE) % Split({
        _constants.NOTEON:  NoteOn(note, _constants.EVENT_VELOCITY),
        _constants.NOTEOFF: NoteOff(note, _constants.EVENT_VELOCITY),
    })


@_unit_repr
def Velocity(*args, **kwargs):
    value, mode = _misc.call_overload(args, kwargs, [
            lambda offset: (offset, 1),
            lambda multiply: (multiply, 2),
            lambda fixed: (fixed, 3),
            lambda gamma: (gamma, 4),
            lambda curve: (curve, 5),
        ]
    )
    return _Unit(_mididings.Velocity(value, mode))


@_misc.deprecated('Velocity')
def VelocityMultiply(value):
    return Velocity(multiply=value)

@_misc.deprecated('Velocity')
def VelocityFixed(value):
    return Velocity(fixed=value)

@_misc.deprecated('Velocity')
def VelocityCurve(gamma):
    return Velocity(gamma=gamma)


@_unit_repr
def VelocitySlope(*args, **kwargs):
    notes, values, mode = _misc.call_overload(args, kwargs, [
            lambda notes, offset: (notes, offset, 1),
            lambda notes, multiply: (notes, multiply, 2),
            lambda notes, fixed: (notes, fixed, 3),
            lambda notes, gamma: (notes, gamma, 4),
            lambda notes, curve: (notes, curve, 5),
        ]
    )
    note_numbers = [_util.note_number(n) for n in notes]

    if len(notes) != len(values):
        raise ValueError("notes and velocity values must be sequences of the same length")
    if len(notes) < 2:
        raise ValueError("need at least two notes")
    if sorted(note_numbers) != note_numbers:
        raise ValueError("notes must be in ascending order")

    return _Unit(_mididings.VelocitySlope(
        _misc.make_int_vector(note_numbers),
        _misc.make_float_vector(values), mode
    ))


@_misc.deprecated('VelocitySlope')
def VelocityGradient(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), offset=(value_lower, value_upper))

@_misc.deprecated('VelocitySlope')
def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), multiply=(value_lower, value_upper))

@_misc.deprecated('VelocitySlope')
def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), fixed=(value_lower, value_upper))


def VelocityLimit(lower, upper):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, lower):     Velocity(fixed=lower),
        (lower, upper): Pass(),
        (upper, 0):     Velocity(fixed=upper),
    })


@_unit_repr
def CtrlMap(ctrl_in, ctrl_out):
    return _Unit(_mididings.CtrlMap(
        _util.ctrl_number(ctrl_in),
        _util.ctrl_number(ctrl_out)
    ))


@_unit_repr
def CtrlRange(ctrl, out_min, out_max, in_min=0, in_max=127):
    if not in_min < in_max:
        raise ValueError("in_min must be less than in_max")
    return _Unit(_mididings.CtrlRange(
        _util.ctrl_number(ctrl),
        out_min, out_max, in_min, in_max
    ))
