#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from argparse import ArgumentParser
from media_entry import create_media


class BUFFY(object):
    def __init__(self):
        args = ArgumentParser(description='BUFFY --- Back Up Files For You')
        args.add_argument("-c", "--config", dest="config_file", default=None,
                                help="config file name")
        args.add_argument("-v", "--verbose", dest="verbose", action="store_const",
                                const=logging.DEBUG, help="verbose mode")
        args.add_argument("-s", "--silent", dest="silent", action="store_const",
                                const=logging.ERROR, help="silent mode")
        self.args = args.parse_args()
        if not self.args.config_file:
            args.print_help()
            sys.exit()
        log_level = self.args.verbose if self.args.verbose else self.args.silent if self.args.silent else logging.INFO
        logging.basicConfig(format='', level=log_level)
        from util.config import Config
        self.config = Config(self.args.config_file)

    def run(self):
        logging.info("[BUFFY] start back up...")
        sources = self.config.src.get_sources()
        for dst in self.config.dst:
            media = create_media(dst, self.config)
            if not media.exist():
                media.create_path()
            media.back_up(sources)


if __name__ == '__main__':
    BUFFY().run()
