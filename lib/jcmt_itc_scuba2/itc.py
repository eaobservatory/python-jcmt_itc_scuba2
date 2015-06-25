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

from collections import OrderedDict
from math import sqrt

from .data import scuba2_modes


class SCUBA2ITC(object):
    def __init__(self, mode_data=None):
        """
        Construct ITC object.

        ITC parameters can be given via the "mode_data" argument as a
        dictionary of SCUBA2Mode objects by mode name.  Otherwise the
        default data are used.
        """

        if mode_data is None:
            self.data = scuba2_modes
        else:
            self.data = mode_data

    def calculate_time(self, mode, filter_, transmission, factor, rms):
        """
        Calculate the observing time.

        Parameters are observing type, wavelength (450/850), transmission,
        factor, target RMS (mJy/beam).
        """

        param = self._get_param(mode, filter_)

        sqrttime = (param.tA / transmission + param.tB) / rms

        return sqrttime * sqrttime / factor

    def calculate_rms(self, mode, filter_, transmission, factor, time):
        """
        Calculate the RMS.

        Parameters are observing type, wavelength (450/850), transmission,
        factor, observing time.
        """

        param = self._get_param(mode, filter_)

        return ((param.tA / transmission) + param.tB) / sqrt(factor * time)

    def get_modes(self):
        """
        Get an ordered dictionary of observing modes.

        The keys are the mode names, as required by the calculate_time
        and calculate_rms methods.  The values are the mode descriptions.
        """

        return OrderedDict(((mode, info.description)
                            for (mode, info) in self.data.items()))

    def _get_param(self, mode, filter_):
        mode_info = self.data.get(mode)

        if mode_info is None:
            raise Exception(
                'Unknown SCUBA-2 observing mode: "{0}"'.format(mode))

        if filter_ == 850:
            return mode_info.param_850

        elif filter_ == 450:
            return mode_info.param_450

        raise Exception('Unknown SCUBA-2 filter: "{0}"'.format(filter_))
