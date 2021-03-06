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

evasion_catalog = {}
"""
NODE = dict{name:(NODE|evasion)}
"""

"""
To make an evasion :
herit from baseevasion.BaseEvasion
have 2 static attributes :
    - evasion_folder = str
    - evasion_list   = list[evasions]
"""


def _list_evasion_modules():
    """
    Imports all submodules, amd list the evasions modules
    """
    global evasion_list

    import pkgutil
    import os
    import sys
    import importlib
    import inspect
    import baseevasion

    evasion_mother_class = baseevasion.BaseEvasion

    def search_for_evasions_class(module):
        #print "searching :", module
        clsmembers = inspect.getmembers(sys.modules[module],
                                        lambda x: inspect.isclass(x) and x.__module__ == module)
        for class_member in clsmembers:
            class_obj = class_member[1]
            if (class_obj != evasion_mother_class
                    and issubclass(class_obj, evasion_mother_class)):
                evasion_folder = getattr(class_obj, "evasion_folder", None)
                evasion_list = getattr(class_obj, "evasion_list", None)
                if evasion_list is not None and evasion_folder is not None:
                    for ev in evasion_list:
                        evasion_catalog[
                            evasion_folder + "/" + ev.get_id()] = ev

    def import_submodules_rec(path, name):
        for _loader, _modulename, _is_pkg in pkgutil.iter_modules(path=[path]):
            full_name = name + "." + _modulename
            importlib.import_module(full_name)
            if _is_pkg:
                import_submodules_rec(path + "/" + _modulename, name=full_name)
            else:
                search_for_evasions_class(full_name)

    import_submodules_rec(sys.modules[__name__].__path__[0], __name__)


_list_evasion_modules()
del(_list_evasion_modules)
