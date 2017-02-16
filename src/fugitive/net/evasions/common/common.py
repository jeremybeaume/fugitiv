#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Fugitive : Network evasion tester
# Copyright (C) 2017 Jérémy BEAUME (jeremy [dot] beaume (a) protonmail [dot] com)
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def reverse_frag_list(frag_list, pre_frag=False, post_frag=False):
    """
    Reverse a list.
    If pre_frag is true, first element stays the first element
    If post_frag is true, last element stays
    """

    pre  = int(pre_frag)
    if not post_frag:
        post = len(frag_list)
    else:
        post = -1

    l = frag_list[:pre]

    middle = frag_list[pre:post]
    middle.reverse()
    l += middle

    l += frag_list[post:]

    return l;
