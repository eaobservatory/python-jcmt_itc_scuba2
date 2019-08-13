SCUBA-2 Integration Time Calculator
===================================

Introduction
------------

This package contains the Python-based integration time calculator
for SCUBA-2.  It is based on the original Perl
`Astro::ITC::SCUBA2 <https://github.com/eaobservatory/perl-Astro-ITC-SCUBA2>`_
module.

Usage
-----

The integration time calculator (ITC) can be used in a Python program
via a `SCUBA2ITC` object.
The main calculation methods are
`calculate_total_time` and `calculate_rms_for_total_time`.
Each of these takes an optional `with_extra_output` argument.
If this is not specified, only the main answer is returned,
but if a true value is given, a `(result, extra)` pair is
returned, where `extra` is a dictionary of supplemental information.

Sampling factors are given relative to the default pixel sizes
of 4" and 2" at 850um and 450um respectively.
For more information, see
`the SCUBA-2 sensitivity page <https://www.eaobservatory.org/jcmt/instrumentation/continuum/scuba-2/time-and-sensitivity/#Sampling_factor_f>`_.

Here is an example time calculation for a 1800" pong observation:

.. code-block:: python

    from jcmt_itc_scuba2 import SCUBA2ITC, SCUBA2ITCError

    itc = SCUBA2ITC()

    try:
        airmass = itc.estimate_airmass(declination_deg=20.0)

        sampling_factors = {
            850: (6.5 / 4) ** 2,
            450: (4 / 2) ** 2 }

        (result, extra) = itc.calculate_total_time(
            mode='pong1800',
            filter_=850,
            tau_225=0.065,
            airmass=airmass,
            sampling_factors=sampling_factors,
            rms=5.0,  # Jy/beam
            with_extra_output=True)

        print('Main result: {}'.format(result))
        print('Extra information: {!r}'.format(extra))

    except SCUBA2ITCError as e:
        print('Error: {}'.format(e))

License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
