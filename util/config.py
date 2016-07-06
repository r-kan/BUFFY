#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
import os
import sys


def show_list(list_entry, name):
    if not list_entry:
        return
    if 1 == len(list_entry):
        logging.debug("%s: %s" % (name, list_entry[0]))
    else:
        logging.debug("%s:" % name)
        for item in list_entry:
            logging.debug("\t%s" % item)


ROOT_KEY = "root"
FILE_KEY = "file"
EXT_KEY = "ext"
RE_KEY = "re"

DIR_DELIM = "/"


class Source(object):
    def __init__(self, data):
        if not type(data) in [str, dict]:
            logging.error("[config] entry 'src' shall contain 'str' or 'dict' value instead of %s, program exit..." %
                          type(data))
            sys.exit()
        simple_spec = type(data) is str

        file_or_dir = data if simple_spec else data[FILE_KEY] if FILE_KEY in data else None
        assert not file_or_dir or type(file_or_dir) in [str, list]
        self.file_or_dir = file_or_dir if not file_or_dir or type(file_or_dir) is list else [file_or_dir]

        self.root = data[ROOT_KEY] if not simple_spec and ROOT_KEY in data else ""
        assert type(self.root) is str

        ext = data[EXT_KEY] if not simple_spec and EXT_KEY in data else None
        assert not ext or type(ext) in [str, list]
        self.ext = ext if not ext or type(ext) is list else [ext]

        re = data[RE_KEY] if not simple_spec and RE_KEY in data else None
        assert not re or type(re) in [str, list]
        self.re = re if not re or type(re) is list else [re]

        assert self.file_or_dir or self.ext or self.re

        self.show_setting()
        if len(self.root) > 0 and self.root[-1] != DIR_DELIM:
            self.root += DIR_DELIM

    def show_setting(self):
        if "" is not self.root:
            logging.debug("root: %s" % self.root)
        show_list(self.file_or_dir, "file")
        show_list(self.ext, "ext")
        show_list(self.re, "re")

    @staticmethod
    def get_dir_files(dirname):
        assert os.path.isdir(dirname)
        ret = []
        for root, _, files in os.walk(dirname):
            ret += [root + "/" + file for file in files]
        return ret

    @staticmethod
    def get_files(file_or_dir):
        return Source.get_dir_files(file_or_dir) if os.path.isdir(file_or_dir) else [file_or_dir]

    def get_sources(self):
        sources = []
        if self.file_or_dir:
            for file_or_dir in self.file_or_dir:
                src = self.root + file_or_dir
                if not os.path.exists(src):
                    logging.warning("[config] the specified source '%s' does not exist" % src)
                    continue
                sources += Source.get_files(src)
        if self.ext:
            assert "" != self.root
            for root, _, files in os.walk(self.root):
                for file in files:
                    basename, ext = os.path.splitext(file)
                    if ext.replace(".", "") in self.ext:
                        sources.append(root + "/" + file)
        if self.re:
            assert "" != self.root
            patterns = [re.compile(".*/" + item) for item in self.re]
            for root, dirs, files in os.walk(self.root):
                for src in (files + dirs):
                    file_or_dir = root + "/" + src
                    for pattern in patterns:
                        if re.match(pattern, file_or_dir):
                            sources += Source.get_files(file_or_dir)
        return list(set(sources))  # 'set' to remove duplication


NAME_KEY = "name"
DST_KEY = "dst"
SRC_KEY = "src"
COMPRESS_KEY = "compress"
ENCODING_KEY = "encoding"


DEFAULT_COMPRESS = False
DEFAULT_PRESERVE_HIER = True
DEFAULT_ENCODING = False


class Config(object):

    @staticmethod
    def get_bool_value(data, key, default_value):
        return True if key in data and data[key] in ["yes", "y"] else default_value

    def __init__(self, config_file):
        if not config_file or not os.path.exists(config_file):
            logging.error("[BUFFY] config file \"%s\" does not exist, program exit..." % config_file)
            sys.exit()
        logging.info("[BUFFY] reading config file \"%s\"..." % config_file)
        with open(config_file) as config_fp:
            import json
            data = json.load(config_fp)

        if DST_KEY not in data:
            logging.error("[config] no \'dst\' specified, program exit...")
            sys.exit()
        dst = data[DST_KEY]
        if not type(dst) in [str, list]:
            logging.error("[config] entry 'src' shall contain 'str' or 'list' value instead of %s, program exit..." %
                          type(dst))
            sys.exit()

        if SRC_KEY not in data:
            logging.error("[config] no \'src\' specified, program exit...")
            sys.exit()

        self.dst = [dst] if type(dst) is str else dst
        self.name = data[NAME_KEY] if NAME_KEY in data else ""
        assert type(self.name) is str
        self.compress = Config.get_bool_value(data, COMPRESS_KEY, DEFAULT_COMPRESS)
        self.encoding = Config.get_bool_value(data, ENCODING_KEY, DEFAULT_ENCODING)

        logging.debug("------------------------")
        if "" != self.name:
            logging.debug("name: %s" % self.name)
        show_list(self.dst, "dst")
        self.src = Source(data[SRC_KEY])
        logging.debug("compress: %s" % ("yes" if self.compress else "no"))
        logging.debug("encoding: %s" % ("yes" if self.encoding else "no"))
        logging.debug("------------------------")
