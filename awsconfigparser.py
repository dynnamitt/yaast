#!/usr/bin/python3

import configparser
import logging
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

    # as dict
    # def get_props_dict(self):
    #     """Combine result from both INI files
    #     and give credentials precedence"""

    #     #FIXME
    #     if self.profile_presens:
    #         conf_sect = self.config[self.__find_c_section_name()]
    #         creds_sect = self.credentials[self.profile]
    #         return dict(
    #             [(key, conf_sect[key]) for key in conf_sect] +
    #             [(key, creds_sect[key]) for key in creds_sect]
    #             )
    #     else:
    #         None


    def write_new_attrs(self, attributes, backup=False):

        def __has_token():
            return self._parser

        if self.exists and backup :
            self.__backup_profile(self._profile_header)
        else:
            warning("No bakcup!")
       
        self._parser.section[self.profile] = attributes

        with open(CFile.CRED_PATH, 'w') as f:
            self.credentials.write(f)

        return [self.__class__.CRED_PATH]

    def __backup_profile(self, filepath):
        # some algo to makeup a name
        warning(f"__backup_profile() impl missing still missing. {filepath}")
        pass


import unittest

class TestStringMethods(unittest.TestCase):

    def test_non_existing_profile(self):
        sut = AWSConfParser("yyy", CFile.CONFIG)
        
        self.assertEqual(sut.exists, False)

if __name__ == "__main__":
    unittest.main()

