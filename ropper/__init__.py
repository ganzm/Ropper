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
from filebytes.pe import ImageDirectoryEntry
from .console import Console
from .options import Options
from .common.error import *
from binascii import unhexlify
from ropper.rop import Ropper, FORMAT
from ropper.loaders import elf
from ropper.loaders import pe
from ropper.loaders import mach_o
from ropper.loaders import raw
from ropper.loaders.loader import Loader, Type
from ropper.gadget import Gadget, GadgetType
from ropper.arch import ARM,ARM64, ARMTHUMB,  x86, x86_64, PPC, PPC64, MIPS, MIPS64

app_options = None
VERSION=[1,9,5]

def start(args):
    try:
        global app_options
        app_options = Options(args)
        Console(app_options).start()
    except RopperError as e:
        print(e)


def deleteDuplicates(gadgets, callback=None):
    toReturn = []
    inst = set()
    count = 0
    for i,gadget in enumerate(gadgets):
        inst.add(gadget._gadget)
        if len(inst) > count:
            count = len(inst)
            toReturn.append(gadget)
        if callback:
            callback(gadget, i, len(gadgets))
    if callback:
        callback(None, -1, len(gadgets))
    return toReturn


def filterBadBytes(gadgets, badbytes):

    def formatBadBytes(badbytes):
        if len(badbytes) % 2 > 0:
            raise RopperError('The length of badbytes has to be a multiple of two')

        try:
            badbytes = unhexlify(badbytes)
        except:
            raise RopperError('Invalid characters in badbytes string')
        return badbytes


    if not badbytes:
        return gadgets

    toReturn = []

    badbytes = formatBadBytes(badbytes)

    for gadget in gadgets:
        if not badbytes or not gadget.addressesContainsBytes(badbytes):
            toReturn.append(gadget)

    return toReturn

def search(gadgets, searchString):
    if not gadgets:
        return []

    searcher = gadgets[0].binary.arch.searcher
    return searcher.search(gadgets, searchString)


def cfgFilterGadgets(gadgets, callback=None):
    result = []
    gadgetLen = float(len(gadgets))
    i = 0
    for gadget in gadgets:
        # calculate relative address of the gadget when loaded to memory
        gadgetRVA = gadget.address - gadget.binary.imageBase

        # consider Microsoft CFG implementation imprecision - chop off 3 lsbits
        gadgetRVA8ByteAligend = gadgetRVA - (gadgetRVA % 8)
        loadConfig = gadget.binary._binary.dataDirectory[ImageDirectoryEntry.LOAD_CONFIG]
        inList = gadgetRVA8ByteAligend in loadConfig.cfGuardedFunctions

        if inList:
            # this is a gadget which passes CFG checks
            result.append(gadget)

        if callback and i % 0x100 == 0:
            # occasional progress reporting
            callback(i/gadgetLen)

        i += 1

    if callback:
        callback(1.0)

    return result