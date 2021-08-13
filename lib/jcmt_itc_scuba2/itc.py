# Copyright (C) 2013 Science and Technology Facilities Council.
# Copyright (C) 2015-2021 East Asian Observatory
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
from math import ceil, cos, exp, radians, sqrt

from .data import scuba2_modes, scuba2_tau_relations
from .version import version


SCUBA2ModeSummary = namedtuple(
    'SCUBA2ModeSummary', ('description', 'pix_850', 'pix_450', 'match_filt'))


class SCUBA2ITCError(Exception):
    pass


class SCUBA2ITC(object):
    def __init__(self, mode_data=None, tau_data=None, overhead=90.0):
        """
        Construct ITC object.

        ITC parameters can be given via the "mode_data" argument as a
        dictionary of SCUBA2Mode objects by mode name.  Otherwise the
        default data are used.

        Similarly the tau relations can be given as a dictionary of
        TauRelation objects by (integer) wavelength.
        """

        if mode_data is None:
            self.data = scuba2_modes
        else:
            self.data = mode_data

        if tau_data is None:
            self.tau_relations = scuba2_tau_relations
        else:
            self.tau_relations = tau_data

        self.overhead = overhead

    def get_version(self):
        """
        Get the module version.
        """

        return version

    def calculate_total_time(
            self, mode, filter_, tau_225, airmass, sampling_factors, rms,
            with_extra_output=False):
        """
        Calculate the total observing time.

        (This is the time on source plus overheads.)
        """

        try:
            (tau, transmission, extra) = \
                self._calculate_opacity_and_transmission(tau_225, airmass)

            time_src = self._calculate_time_on_source(
                mode, filter_, transmission[filter_],
                sampling_factors[filter_], rms)

            time_tot = time_src + self._estimate_overhead(mode, time_src)

            if not with_extra_output:
                return time_tot

            extra['time_src'] = time_src

            # Ignore errors calculating the alternate filter RMS.
            try:
                filter_alt = 850 if filter_ == 450 else 450

                extra['wl_alt'] = filter_alt
                extra['rms_alt'] = self._calculate_rms_for_time_on_source(
                    mode, filter_alt, transmission[filter_alt],
                    sampling_factors[filter_alt], time_src)

            except:
                pass

            return (time_tot, extra)

        except ZeroDivisionError:
            raise SCUBA2ITCError(
                'Division by zero error occurred during calculation.')

        except ValueError as e:
            if e.args[0] == 'math domain error':
                raise SCUBA2ITCError(
                    'Negative square root error occurred during calculation.')
            raise

    def calculate_rms_for_total_time(
            self, mode, filter_, tau_225, airmass, sampling_factors, time_tot,
            with_extra_output=False):
        """
        Calculate the RMS for the given total observing time.
        """

        time_src = time_tot - self._estimate_overhead(
            mode, time_tot, from_total=True)

        result = self.calculate_rms_for_time_on_source(
            mode, filter_, tau_225, airmass, sampling_factors, time_src,
            with_extra_output=with_extra_output)

        if with_extra_output:
            (rms, extra) = result

            extra['time_src'] = time_src

        return result

    def calculate_rms_for_time_on_source(
            self, mode, filter_, tau_225, airmass, sampling_factors, time_src,
            with_extra_output=False):
        """
        Calculate the RMS for the given on-source observing time.
        """

        try:
            (tau, transmission, extra) = \
                self._calculate_opacity_and_transmission(tau_225, airmass)

            rms = self._calculate_rms_for_time_on_source(
                mode, filter_, transmission[filter_],
                sampling_factors[filter_], time_src)

            if not with_extra_output:
                return rms

            # Ignore errors calculating the alternate filter RMS.
            try:
                filter_alt = 850 if filter_ == 450 else 450

                extra['wl_alt'] = filter_alt
                extra['rms_alt'] = self._calculate_rms_for_time_on_source(
                    mode, filter_alt, transmission[filter_alt],
                    sampling_factors[filter_alt], time_src)

            except:
                pass

            return (rms, extra)

        except ZeroDivisionError:
            raise SCUBA2ITCError(
                'Division by zero error occurred during calculation.')

        except ValueError as e:
            if e.args[0] == 'math domain error':
                raise SCUBA2ITCError(
                    'Negative square root error occurred during calculation.')
            raise

    def _calculate_opacity_and_transmission(self, tau_225, airmass):
        """
        Determine tau and transmission at each wavelength.
        """

        tau = {}
        transmission = {}
        extra = {}

        for filter_ in (850, 450):
            tau_wl = self._calculate_opacity(filter_, tau_225)
            tau[filter_] = tau_wl
            extra['tau_{}'.format(filter_)] = tau_wl

            transmission_wl = self._calculate_transmission(airmass, tau_wl)
            transmission[filter_] = transmission_wl
            extra['trans_{}'.format(filter_)] = transmission_wl

        return (tau, transmission, extra)

    def _calculate_time_on_source(
            self, mode, filter_, transmission, factor, rms):
        """
        Calculate the on-source observing time.

        Parameters are observing type, wavelength (450/850), transmission,
        factor, target RMS (mJy/beam).
        """

        param = self._get_param(mode, filter_)

        sqrttime = (param.tA / transmission + param.tB) / rms

        return sqrttime * sqrttime / factor

    def _calculate_rms_for_time_on_source(
            self, mode, filter_, transmission, factor, time):
        """
        Calculate the RMS for the given time on source.

        Parameters are observing type, wavelength (450/850), transmission,
        factor, on-source observing time.
        """

        param = self._get_param(mode, filter_)

        return ((param.tA / transmission) + param.tB) / sqrt(factor * time)

    def _calculate_opacity(self, filter_, tau_225):
        """
        Calculate the opacity for the given filter.
        """

        try:
            tau_relation = self.tau_relations[filter_]
        except KeyError:
            raise SCUBA2ITCError(
                'Unknown SCUBA-2 filter: "{0}"'.format(filter_))

        return tau_relation.a * (tau_225 + tau_relation.b + tau_relation.c * sqrt(tau_225))

    def _calculate_transmission(self, airmass, tau):
        """
        Calculate the atmospheric transmission given the airmass
        and the tau at the wavelength of interest.
        """

        return exp(-1.0 * airmass * tau)

    def estimate_airmass(self, declination_deg):
        """
        Estimate average airmass for a source at a given declination.
        """

        return 1.0 / (0.9 * cos(radians(declination_deg - 19.823)))

    def _estimate_overhead(self, mode, time, from_total=False):
        """
        Get the typical observing overhead in seconds based on a time
        in seconds.

        If the "from_total" keyword argument is true then the time is assumed
        to be a total time (including overheads).
        """

        mode_info = self.data.get(mode)

        if mode_info is None:
            raise SCUBA2ITCError(
                'Unknown SCUBA-2 observing mode: "{0}"'.format(mode))

        block_sec = mode_info.block_min * 60.0

        if from_total:
            block_sec += self.overhead

        return self.overhead * ceil(time / block_sec)

    def get_modes(self):
        """
        Get an ordered dictionary of observing modes.

        The keys are the mode names, as required by the calculate_time
        and calculate_rms methods.  The values are the mode descriptions.
        """

        return OrderedDict((
            (mode, SCUBA2ModeSummary(
                info.description, info.pix_850, info.pix_450, info.match_filt))
            for (mode, info) in self.data.items()
        ))

    def _get_param(self, mode, filter_):
        mode_info = self.data.get(mode)

        if mode_info is None:
            raise SCUBA2ITCError(
                'Unknown SCUBA-2 observing mode: "{0}"'.format(mode))

        if filter_ == 850:
            param = mode_info.param_850

        elif filter_ == 450:
            param = mode_info.param_450

        else:
            raise SCUBA2ITCError(
                'Unknown SCUBA-2 filter: "{0}"'.format(filter_))

        if param is None:
            raise SCUBA2ITCError(
                'Timing parameters are not available '
                'for this observing mode and wavelength.')

        return param
