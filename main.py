#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from argparse import ArgumentParser
from logging import info, INFO, DEBUG, ERROR
from media_entry import create_media


class BUFFY(object):
    def __init__(self):
        args = ArgumentParser(description='BUFFY --- Back Up Files For You')
        args.add_argument("-c", "--config", dest="config_file", default=None, help="config file name")
        args.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=DEBUG, help="verbose mode")
        args.add_argument("-s", "--silent", dest="silent", action="store_const", const=ERROR, help="silent mode")
        args.add_argument("-d", "--dry_run", dest="dry", action="store_const", const=True, help="perform a dry run")
        self.args = args.parse_args()
        if not self.args.config_file:
            args.print_help()
            sys.exit()
        log_level = self.args.verbose if self.args.verbose else self.args.silent if self.args.silent else INFO
        logging.basicConfig(format='', level=log_level)
        from util.config import Config
        self.config = Config(self.args.config_file)

    def run(self):
        info("[BUFFY] start back up...")
        sources = self.config.src.get_sources()
        if not len(sources) > 0:
            info("[BUFFY] no sources to back up")
            return
        for dst in self.config.dst:
            media = create_media(dst, self.config, self.args)
            if not media.exist():
                media.create_path()
            media.back_up(sources)


if __name__ == '__main__':
    BUFFY().run()
