#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import logging
import os
import errno
from shutil import copyfile
from media.base import MediaBase
from util.config import DIR_DELIM


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


class Disk(MediaBase):
    def __init__(self, dst_root, setting):
        super(Disk, self).__init__(dst_root, setting)
        if self._dst_root[-1] != DIR_DELIM:
            self._dst_root += DIR_DELIM

    def exist(self):
        return os.path.exists(self._dst_root)

    def create_path(self):
        logging.info("[disk] create path: %s" % self._dst_root)
        os.mkdir(self._dst_root)

    @staticmethod
    def write(filename, content):
        with open(filename, 'w') as fd:
            fd.write(content)

    def backup_compress(self, sources):
        out_basename = self.name if "" != self.name else "BUFFY"
        encoding_str = "_" + self.encoding_str if len(self.encoding_str) > 0 else ""
        dst_base = self._dst_root + out_basename + encoding_str
        tar_input_file = dst_base + ".list"
        with open(tar_input_file, 'w') as fd:
            for src in sources:
                fd.write(src.replace(self.root, "") + "\n")
        compress_cmd = "tar zcvf %(dst)s -T %(src_list_file)s" \
                       % {'dst': "%s.tar.gz" % dst_base, 'src_list_file': tar_input_file}
        os.chdir(self.root)
        os.system("bash -c \"" + compress_cmd + " >& /dev/null\"")
        return dst_base + ".txt", ("cd %s\n" % self.root) + compress_cmd

    def backup_uncompress(self, sources):
        backup_map = collections.OrderedDict()
        backup_name = self.encoding_str if not self.name else \
            self.name + ("_" + self.encoding_str if len(self.encoding_str) > 0 else "")
        dst_base = self._dst_root + backup_name + (DIR_DELIM if len(backup_name) > 0 else "")
        for src in sources:
            dirname, _ = os.path.split(src)
            need_dir = dst_base + (dirname + DIR_DELIM).replace(self.root, '')
            if not os.path.exists(need_dir):
                mkdir_p(need_dir)
            dst = need_dir + os.path.basename(src)
            backup_map[src] = dst
            assert not os.path.isdir(src)
            copyfile(src, dst)
        report_str = ""
        for src_to_dst in backup_map:
            report_str += (src_to_dst + " => " + backup_map[src_to_dst] + "\n")
        report_file = self._dst_root + ("BUFFY" if "" == backup_name else backup_name) + ".txt"
        return report_file, report_str

    def back_up(self, sources):
        logging.info("[disk] back up to dst: %s" % self._dst_root)
        backup_ftor = self.backup_compress if self.compress else self.backup_uncompress
        report_file, report_str = backup_ftor(sources)
        report_str_max_length = 1024 * 1024  # 1MB
        if len(report_str) > report_str_max_length:
            message = "skip dump subsequent report str for the total size (%s) is too large" % len(report_str)
            logging.info("[info] %s" % message)
            report_str = report_str[:report_str_max_length] + "\n...\n" + message
        Disk.write(report_file, report_str)
