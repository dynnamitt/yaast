#!/usr/bin/python3

import configparser
import logging
import collections
from logging import debug,info,error,warning
from pathlib import Path
import re
from enum import Enum


class CFile(Enum):
    CONFIG = (Path.home() / ".aws/config", "profile ")
    CREDS = (Path.home() / ".aws/credentials", "")

    def __init__(self, path: Path, header_prefix: str ):
        self.path = path
        self.header_prefix = header_prefix


class AWSConfParser:
    """Parse and Write to config duo (aka ~/.aws/{config,credentials}) """


    def __init__(self, profile:str , cfile: CFile):

        self._profile = profile
        self._cfile = cfile

        self._profile_header = f"{self._cfile.header_prefix}{self._profile}" 
        self._parser = configparser.ConfigParser()
        self._parser.read(cfile.path)

        debug(self._parser.sections())


    @property
    def exists(self):
        return self._profile_header in [s.strip() for s in self._parser.sections()]

    @property
    # realy helpful since configparser::ConfigParser is weirdo
    def __dict__(self):
        if self.exists:
            return self._parser._sections[self._profile_header]
        else:
            return {}
 

    def set_new_attrs(self, backup: bool, **kwargs):

        def __has_token():
            return self._parser

        if self.exists and backup :
            self.__backup_profile(self._profile_header)
        elif self.exists:
            warning("Skipped backup of existing profile!")

        self._parser[self._profile_header] = kwargs

    def save(self):

        with open(self._cfile.path, 'w') as f:
            self._parser.write(f)

        return [self._cfile]

    def __backup_profile(self, filepath):
        # some algo to makeup a name
        warning(f"__backup_profile() impl missing still missing. {filepath}")
        pass


import unittest
import os

def file_contents(path):
    with open(path) as f:
        for line in f:
            info(line.strip())

class TestStringMethods(unittest.TestCase):
    TestCFileEnum = collections.namedtuple('_Cfile',("path header_prefix"))


    def test_non_existing_profile(self):
        sut = AWSConfParser("yyy", CFile.CONFIG)
        self.assertEqual(sut.exists, False)
        info(vars(sut))

    def test_existing_profile(self):

        sut = AWSConfParser("default", CFile.CONFIG)
        self.assertEqual(sut.exists, True)
        info(vars(sut))

    def test_insert(self):
        testcase = self.__class__.TestCFileEnum("/tmp/py-testfile.ini","")
        sut = AWSConfParser("unittest-profile", testcase)
        #self.assertEqual(sut.exists, False)
        sut.set_new_attrs(backup=False, x=1, y="2")
        sut.save()
        file_contents(testcase.path)
        # cleanup
        os.remove(testcase.path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

