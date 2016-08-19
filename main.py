#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from argparse import ArgumentParser
from logging import info, INFO, DEBUG, WARNING
from media_entry import create_media
from media.base import MediaBase, disk_write
from util.config import Config, DEFAULT_COMPRESS, DEFAULT_ENCODING


class BUFFY(object):
    def __init__(self):
        args = ArgumentParser(description='BUFFY --- Back Up Files For You')
        # simple flow options
        args.add_argument("-src", dest="src", default=None, help="backup source")
        args.add_argument("-dst", dest="dst", action='append', default=None, help="backup destination")
        args.add_argument("-n", "--name", dest="name", default=None, help="backup name")
        args.add_argument("-e", "--encoding", dest="encoding", action="store_const", const=True,
                          help="name encoding with date (default: %s)" % DEFAULT_ENCODING)
        args.add_argument("-cmp", "--compress", dest="compress", action="store_const", const=True,
                          help="compress backup files (default: %s)" % DEFAULT_COMPRESS)
        args.add_argument("-r", "--report", dest="rpt", default=None, help="report path")
        simple_flow_args = ["src", "dst", "name", "compress", "encoding", "rpt"]
        # general options
        args.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=DEBUG, help="verbose mode")
        args.add_argument("-s", "--silent", dest="silent", action="store_const", const=WARNING, help="silent mode")
        args.add_argument("-d", "--dry_run", dest="dry", action="store_const", const=True, help="perform a dry run")
        # normal flow option
        args.add_argument("-c", "--config", dest="config_file", default=None,
                          help="config file (this option overwrites others)")
        self.args = args.parse_args()
        if not self.args.config_file and (not self.args.src or not self.args.dst):
            args.print_help()
            BUFFY.print_information()
            sys.exit()
        log_level = self.args.verbose if self.args.verbose else self.args.silent if self.args.silent else INFO
        logging.basicConfig(format='', level=log_level)
        if self.args.config_file:
            for arg in vars(self.args):
                value = getattr(self.args, arg)
                if None is not value and arg in simple_flow_args:
                    info("option value '%s = %s' has no effect" % (arg, value))
            self.config = Config(self.args.config_file)
        else:
            compress = DEFAULT_COMPRESS if None is self.args.compress else self.args.compress
            encoding = DEFAULT_ENCODING if None is self.args.encoding else self.args.encoding
            self.config = Config(src=self.args.src, dst=self.args.dst, name=self.args.name,
                                 compress=compress, encoding=encoding, rpt=self.args.rpt)

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
        if not self.args.dry:
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
    def print_information():
        print("\nexample:")
        print("  buffy -src /data_dir -dst /backup_dir -dst s3://backup_bucket")
        print("  buffy -c example.json")
        print("\ncheck https://github.com/r-kan/BUFFY for updates and more information!")

    @staticmethod
    def get_source_digest(root, sources):
        import os
        total_size = sum([os.stat(src).st_size for src in sources])
        return "source : %s\n\tfile count: %i, size: %i\n" % (root, len(sources), total_size)


if __name__ == '__main__':
    BUFFY().run()
