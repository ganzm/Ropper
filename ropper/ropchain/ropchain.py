# coding=utf-8
#
# Copyright 2014 Sascha Schirra
#
# This file is part of Ropper.
#
# Ropper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ropper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from ropper.common.abstract import *
from ropper.common.error import *

class RopChain(Abstract):

    def __init__(self, binaries, gadgets, printer, badbytes=''):
        self._binaries = binaries
        self._usedBinaries = []
        self._printer = printer
        self._gadgets = gadgets
        self.__badbytes = badbytes

    @property
    def badbytes(self):
        return self.__badbytes

    @abstractmethod
    def create(self):
        pass

    @classmethod
    def name(cls):
        return None

    @classmethod
    def availableGenerators(cls):
        return []

    @classmethod
    def archs(self):
        return []

    @classmethod
    def get(cls, binaries, gadgets, name, printer, badbytes=''):
        for subclass in cls.__subclasses__():
            if binaries[0].arch in subclass.archs():
                gens = subclass.availableGenerators()
                for gen in gens:
                    if gen.name() == name:
                        return gen(binaries, gadgets, printer, badbytes)
        

    def containsBadbytes(self, value, bytecount=4):
        for b in self.badbytes:
            tmp = value


            if type(b) == str:
                b = ord(b)

            for i in range(bytecount):
                if (tmp & 0xff) == b:
                    return True

                tmp >>= 8 
        return False
