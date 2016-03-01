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
from unittest import TestCase

from jcmt_itc_scuba2 import SCUBA2ITC


class ITCTestCase(TestCase):
    def test_get_modes(self):
        itc = SCUBA2ITC()
        modes = itc.get_modes()

        self.assertIsInstance(modes, OrderedDict)

        self.assertEqual(
            list(modes.keys()),
            ['daisy', 'pong900', 'pong1800', 'pong3600', 'pong7200',
             'poldaisy'])

        for value in modes.values():
            self.assertTrue(value.startswith('Pong') or
                            value.startswith('Daisy') or
                            value.startswith('POL-2'))

    def test_calculate_rms(self):
        itc = SCUBA2ITC()

        test_data = [
            ('daisy 1', (['daisy', 450, 0.184, 4.0, 810], 63.73)),
            ('daisy 2', (['daisy', 850, 0.710, 4.0, 810], 3.83)),
        ]

        for (name, test) in test_data:
            (args, expected_result) = test

            self.assertAlmostEqual(itc.calculate_rms(*args), expected_result,
                                   delta=0.02)

    def test_calculate_time(self):
        itc = SCUBA2ITC()

        test_data = [
            ('daisy 1', (['daisy', 450, 0.184, 4.0, 45.0], 1624)),
            ('daisy 2', (['daisy', 850, 0.710, 4.0, 2.0], 2975)),
        ]

        for (name, test) in test_data:
            (args, expected_result) = test

            self.assertAlmostEqual(itc.calculate_time(*args), expected_result,
                                   delta=2)
