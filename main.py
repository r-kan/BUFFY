#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from argparse import ArgumentParser
from logging import info, INFO, DEBUG, WARNING
from media_entry import create_media
from media.base import MediaBase, disk_write


class BUFFY(object):
    def __init__(self):
        args = ArgumentParser(description='BUFFY --- Back Up Files For You')
        args.add_argument("-c", "--config", dest="config_file", default=None, help="config file name")
        args.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=DEBUG, help="verbose mode")
        args.add_argument("-s", "--silent", dest="silent", action="store_const", const=WARNING, help="silent mode")
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
        if self.args.dry:
            info("[BUFFY] perform a dry run")
        info("[BUFFY] start back up...")
        sources = self.config.src.get_sources()
        if not sources:
            info("[BUFFY] no sources to back up")
            return
        rpt_content = ""
        for dst in self.config.dst:
            media = create_media(dst, self.config, self.args)
            if not media.exist():
                media.create_path()
            backup_report = media.back_up(sources)
            rpt_content += "destination: %s\n\t%s\n" % (dst, backup_report)
        self.report(BUFFY.get_source_digest(self.config.src.root, sources) + rpt_content[0: len(rpt_content) - 1])

    def report(self, content):
        info(content)
        if self.config.rpt.path:
            encoding_str = MediaBase.get_encoding(self.config.encoding)
            name = self.config.name
            backup_name = encoding_str if not name else name + ("_" + encoding_str if len(encoding_str) > 0 else "")
            report_file = self.config.rpt.path + ("BUFFY" if "" == backup_name else backup_name) + ".log"
            from util.global_def import RPT_WARN_ERR
            disk_write(report_file, RPT_WARN_ERR + content + "\n")

    @staticmethod
    def get_source_digest(root, sources):
        import os
        total_size = sum([os.stat(src).st_size for src in sources])
        return "source : %s\n\tfile count: %i, size: %i\n" % (root, len(sources), total_size)


if __name__ == '__main__':
    BUFFY().run()
