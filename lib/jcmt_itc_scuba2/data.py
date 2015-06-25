# Copyright (C) 2013 Science and Technology Facilities Council.
# Copyright (C) 2015 East Asian Observatory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# This Python ITC is based on the original Perl Astro::ITC::SCUBA2 module.

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from collections import namedtuple, OrderedDict


# Observing parameters: timing parameters are for an equation like
#
#     T_elapse[sec] = [ (tA/transmission + tB) / rms[mJy/beam] ]**2
#
# Where c is defined as:
#
#     T_exposure = c * T_elapse

ITCParam = namedtuple(
    'ITCParam',
    ('tA', 'tB', 'c'))

# Information for an observing mode:
#
#     description:  description of the mode
#     param_850:    timing parameters for 850um calculations
#     param_450:    timing parameters for 450um calculations

SCUBA2Mode = namedtuple(
    'SCUBA2Mode',
    ('description', 'param_850', 'param_450'))

# Information for each observing mode.

scuba2_modes = OrderedDict((
    ('daisy',
     SCUBA2Mode(description='Daisy: ~3 arcmin map',
                param_850=ITCParam(tA=189, tB=-48, c=0.248312),
                param_450=ITCParam(tA=689, tB=-118, c=0.062124))),

    ('pong900',
     SCUBA2Mode(description='Pong 900: 15 arcmin map',
                param_850=ITCParam(tA=407, tB=-104, c=0.053870),
                param_450=ITCParam(tA=1483, tB=-254, c=0.013420))),

    ('pong1800',
     SCUBA2Mode(description='Pong 1800: 30 arcmin map',
                param_850=ITCParam(tA=795, tB=-203, c=0.014113),
                param_450=ITCParam(tA=2904, tB=-497, c=0.003500))),

    ('pong3600',
     SCUBA2Mode(description='Pong 3600: 1 degree map',
                param_850=ITCParam(tA=1675, tB=-428, c=0.003180),
                param_450=ITCParam(tA=6317, tB=-1082, c=0.000550))),

    ('pong7200',
     SCUBA2Mode(description='Pong 7200: 2 degree map',
                param_850=ITCParam(tA=3354, tB=-857, c=0.000794),
                param_450=ITCParam(tA=12837, tB=-2200, c=0.00017919))),
))
