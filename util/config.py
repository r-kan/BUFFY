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
DYNAMIC_KEY = "dyn"
EXCLUDE_KEY = "exclude"

DIR_DELIM = "/"


class Source(object):
    def __init__(self, data, root="", is_exclude=False):
        self.is_exclude = is_exclude
        if not type(data) in [str, dict]:
            logging.error("[config] entry 'src' shall contain 'str' or 'dict' value instead of %s, program exit..." %
                          type(data))
            sys.exit()
        simple_spec = type(data) is str

        self.root = data[ROOT_KEY] if not simple_spec and ROOT_KEY in data else root
        assert type(self.root) is str
        if "" is not self.root and not self.is_exclude:
            logging.debug("root: %s" % self.root)

        # file: specify files by give accurate filename/dirname
        file_or_dir = data if simple_spec else data[FILE_KEY] if FILE_KEY in data else None
        assert not file_or_dir or type(file_or_dir) in [str, list]
        self.file_or_dir = file_or_dir if not file_or_dir or type(file_or_dir) is list else [file_or_dir]
        # ext: specify files by extension name
        ext = data[EXT_KEY] if not simple_spec and EXT_KEY in data else None
        assert not ext or type(ext) in [str, list]
        self.ext = ext if not ext or type(ext) is list else [ext]
        # re: specify files by regular expression matching
        re_data = data[RE_KEY] if not simple_spec and RE_KEY in data else None
        assert not re_data or type(re_data) in [str, list]
        self.re = re_data if not re_data or type(re_data) is list else [re_data]
        # dyn: specify files by re + custom code snippets
        dynamic = data[DYNAMIC_KEY] if not simple_spec and DYNAMIC_KEY in data else None
        assert not dynamic or type(dynamic) is list
        # dynamic shall be either a dyn-item(re-str, import-str, eval-str) list, or a list of dyn-items
        assert not dynamic or 0 == len(dynamic) or \
            (type(dynamic[0]) is list or (type(dynamic[0]) is str and len(dynamic) == 3))
        self.dynamic = dynamic if not dynamic or type(dynamic[0]) is list else [dynamic]

        assert self.file_or_dir or self.ext or self.re or self.dynamic

        # exclude: sources that need not backup (kept by a child 'Source' instance)
        assert not self.is_exclude or EXCLUDE_KEY not in data  # nested 'exclude' entry is not supported
        self.exclude = Source(data[EXCLUDE_KEY], self.root, True) if EXCLUDE_KEY in data else None

        self.show_sources()
        if len(self.root) > 0 and self.root[-1] != DIR_DELIM:
            self.root += DIR_DELIM

    def show_sources(self):
        prefix = "exclude " if self.is_exclude else ""
        show_list(self.file_or_dir, prefix + "file")
        show_list(self.ext, prefix + "ext")
        show_list(self.re, prefix + "re")
        show_list(self.dynamic, prefix + "dyn")

    @staticmethod
    def get_dir_files(dirname):
        assert os.path.isdir(dirname)
        ret = []
        for root, _, files in os.walk(dirname):
            assert len(root) >= 1
            if root[-1] != DIR_DELIM:
                root += DIR_DELIM
            ret += [root + file for file in files]
        return ret

    @staticmethod
    def get_files(file_or_dir):
        return Source.get_dir_files(file_or_dir) if os.path.isdir(file_or_dir) else [file_or_dir]

    @staticmethod
    def get_re_files(root, raw_patterns):
        patterns = [re.compile(root + item) for item in raw_patterns]
        sources = []
        for root, dirs, files in os.walk(root):
            assert len(root) >= 1
            if root[-1] != DIR_DELIM:
                root += DIR_DELIM
            for src in (files + dirs):
                file_or_dir = root + src
                for pattern in patterns:
                    if re.match(pattern, file_or_dir):
                        sources += Source.get_files(file_or_dir)
        return sources

    def get_sources(self):
        sources = []
        if self.file_or_dir:
            for file_or_dir in self.file_or_dir:
                src = self.root + file_or_dir
                if not os.path.exists(src):
                    logging.warning("[config] the specified source '%s' does not exist" % src)
                    continue
                sources += Source.get_files(src)

        if self.ext or self.re or self.dynamic:
            assert "" != self.root

        if self.ext:
            for root, _, files in os.walk(self.root):
                assert len(root) >= 1
                if root[-1] != DIR_DELIM:
                    root += DIR_DELIM
                for file in files:
                    basename, ext = os.path.splitext(file)
                    if ext.replace(".", "") in self.ext:
                        sources.append(root + file)
        if self.re:
            sources += Source.get_re_files(self.root, self.re)

        if self.dynamic:
            patterns = []
            for dyn_item in self.dynamic:
                [re_str, import_str, eval_str] = dyn_item
                dynamic_alias = "$dyn$"
                if dynamic_alias not in re_str:
                    logging.warning("[config] '%s' does not appear in '%s', dynamic filename mechanism will not apply"
                                    % (dynamic_alias, re_str))
                exec("import %s" % import_str)
                dyn_str = eval(eval_str)
                patterns.append(re_str.replace(dynamic_alias, dyn_str))
            sources += Source.get_re_files(self.root, patterns)

        exclude_sources = self.exclude.get_sources() if self.exclude else []
        return sorted([src for src in list(set(sources)) if src not in exclude_sources])  # 'set' to remove duplication


NAME_KEY = "name"
DST_KEY = "dst"
SRC_KEY = "src"
COMPRESS_KEY = "compress"
ENCODING_KEY = "encoding"


DEFAULT_COMPRESS = False
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
