#!/usr/bin/python3

import configparser
import logging
from logging import debug,info,error,warning
from pathlib import Path
import re
from enum import Enum


class CFile(Enum):
    CONF_PATH = Path.home() / ".aws/config"
    CRED_PATH = Path.home() / ".aws/credentials"

class Backup(Enum):
    SKIP = 0
    UNLESS_TOKEN = 1
    ALWAYS = 2

class AWSConfParser:
    """Parse and Write to config duo (aka ~/.aws/{config,credentials}) """


    def __init__(self, profile, must_exist=True):

        self.profile = profile

        self.credentials = configparser.ConfigParser()
        self.credentials.read(CFile.CRED_PATH.value)
        debug(self.credentials.sections())

        self.config = configparser.ConfigParser()
        self.config.read(CFile.CONF_PATH.value)
        debug(self.config.sections())

        if must_exist and not self.profile_presens:
            raise LookupError("Cannot continue")


    @property
    def profile_presens(self):
        """Returns a list w CFile enum [0,1 or 2]
        dependent on profile presens in these INI files"""

        in_creds = CFile.CRED_PATH if self.profile in self.credentials.sections() else None
        in_config = CFile.CONF_PATH if self.__find_c_section_name() else None

        return list(filter(None,[in_creds,in_config]))


    def __find_c_section_name(self):
        """Since profile has 'profile ' prefix in config file """
        res = [s for s in self.config.sections() if re.search(self.profile,s)]
        return res[0] if len(res) else None

    # as dict
    def get_props_dict(self):
        """Combine result from both INI files
        and give credentials precedence"""

        #FIXME
        if self.profile_presens:
            conf_sect = self.config[self.__find_c_section_name()]
            creds_sect = self.credentials[self.profile]
            return dict(
                [(key, conf_sect[key]) for key in conf_sect] +
                [(key, creds_sect[key]) for key in creds_sect]
                )
        else:
            None


    def new_credentials(self, attributes, backup=Backup.ALWAYS):

        def __has_token():
            return self.get_props_dict().get('aws_session_token')

        if self.found_profile and backup==Backup.ALWAYS :
            self.__backup_profile(CFile.CRED_PATH)
        elif self.found_profile and backup==Backup.UNLESS_TOKEN :
            self.__backup_profile(CFile.CRED_PATH) if not __has_token() else None
        elif self.found_profile:
            # this is the old one that will be replaced
            debug([(key,self.credentials[self.profile][key]) for key in self.credentials[self.profile]])

        self.credentials[self.profile] = attributes


    def save(self):
        with open(CFile.CRED_PATH, 'w') as f:
            self.credentials.write(f)

        return [self.__class__.CRED_PATH]

    def __backup_profile(self, filepath):
        # some algo to makeup a name
        warning(f"__backup_profile() impl missing still missing. {filepath}")
        pass


if __name__ == "__main__":
   main()
