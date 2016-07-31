#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import collections
from logging import info
from util.global_def import DIR_DELIM


TMP_DIR = "%(delim)stmp%(delim)sBUFFY%(delim)s" % {'delim': DIR_DELIM}  # TODO: support Windows


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        import errno
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def disk_write(filename, content, dry_run=False):
    if dry_run:
        return
    dirname, _ = os.path.split(filename)
    if not os.path.exists(dirname):
        mkdir_p(dirname)
    with open(filename, 'w') as fd:
        fd.write(content)


class MediaBase(object):
    def __init__(self, media_name, dst_root, setting, args):
        self.media_name = media_name
        self._dst_root = dst_root
        self.root = setting.src.root
        self.name = setting.name
        self.compress = setting.compress
        self.encoding_str = MediaBase.get_encoding(setting.encoding)
        self.dry = args.dry
        self.report_path = setting.rpt.path
        self.detail_report = setting.rpt.detail

    def exist(self):
        return False

    def create_path(self):
        info("[media] '%s' not support create path: %s" % (self.media_name, self._dst_root))

    def report(self, basename, content):
        if not self.report_path or not self.detail_report:
            return
        disk_write(self.report_path + basename, content, self.dry)

    def backup_compress(self, sources):
        is_disk = "disk" == self.media_name
        backup_name = (self.name if "" != self.name else "BUFFY") + \
                      ("_" + self.encoding_str if len(self.encoding_str) > 0 else "")
        dst_base = self._dst_root + backup_name
        non_disk_dst_base = (self.report_path if self.report_path else TMP_DIR) + backup_name
        tar_input_file = non_disk_dst_base + ".list"
        src_list_content = ""
        for src in sources:
            src_list_content += (src.replace(self.root, "") + "\n")
        disk_write(tar_input_file, src_list_content, self.dry)
        targz_file = "%s.tar.gz" % (dst_base if is_disk else non_disk_dst_base)
        compress_cmd = "tar zcvf %(dst)s -T %(src_list_file)s" \
                       % {'dst': targz_file, 'src_list_file': tar_input_file}
        os.chdir(self.root)
        if not self.dry:
            os.system("bash -c \"" + compress_cmd + " >& /dev/null\"")
            if not self.detail_report:
                os.remove(tar_input_file)
        if not is_disk:
            self.copyfile(targz_file, "%s.tar.gz" % dst_base)
            if not self.dry:
                os.remove(targz_file)
        reproduce_str = "cd %s\n%s\n" % (self.root, compress_cmd) + \
                        ("" if is_disk else "%s%s %s\n" % (self.cp_cmd, targz_file, "%s.tar.gz" % dst_base))
        size, timestamp = self.get_file_info_not_dry("%s.tar.gz" % dst_base)
        return "%s.tar.gz, size: %i, timestamp: %s" % (backup_name, size, timestamp), \
               backup_name + "_" + self.media_name + ".cmd", reproduce_str

    def backup_uncompress(self, sources, delim):
        backup_map = collections.OrderedDict()
        backup_name = self.encoding_str if not self.name else \
            self.name + ("_" + self.encoding_str if len(self.encoding_str) > 0 else "")
        dst_base = self._dst_root + backup_name + (delim if len(backup_name) > 0 else "")
        backuped_count = 0
        backuped_size = 0
        for src in sources:
            dirname, _ = os.path.split(src)
            dst_dir = (dirname + delim).replace(self.root, '')
            dst = dst_base + dst_dir + os.path.basename(src)
            backup_map[src] = dst
            assert not os.path.isdir(src)
            backuped, size = self.copyfile(src, dst)
            backuped_count += backuped
            backuped_size += size
        reproduce_file = ("BUFFY" if "" == backup_name else backup_name) + "_" + self.media_name + ".cmd"
        return "file count: %i, size: %i" % (backuped_count, backuped_size), \
               reproduce_file, self.get_reproduce_str(backup_map)

    def back_up(self, sources):
        info("[%s] back up to dst: %s" % (self.media_name, self._dst_root))
        backup_ftor = self.backup_compress if self.compress else self.backup_uncompress
        backup_report, reproduce_file, reproduce_str = backup_ftor(sources)
        reproduce_str_max_length = 1024 * 1024  # 1MB
        if len(reproduce_str) > reproduce_str_max_length:
            message = "skip dump subsequent report for the total size (%s) is too large" % len(reproduce_str)
            info("[info] %s" % message)
            reproduce_str = reproduce_str[:reproduce_str_max_length] + "\n...\n" + message
        self.report(reproduce_file, reproduce_str)
        return backup_report

    @staticmethod
    def get_encoding(enable):
        if not enable:
            return ""
        from datetime import date
        return str(date.today()).replace("-", "")

    def get_reproduce_str(self, mapping):
        reproduce_str = "cd %s\n" % self.root
        for src_to_dst in mapping:
            reproduce_str += (self.cp_cmd + src_to_dst.replace(self.root, "") + " " + mapping[src_to_dst] + "\n")
        return reproduce_str
