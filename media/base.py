#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import collections
from logging import info
from util.config import DIR_DELIM


TMP_DIR = "%(delim)stmp%(delim)sBUFFY%(delim)s" % {'delim': DIR_DELIM}  # TODO: support Windows


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        import errno
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def disk_write(filename, content, dry_run):
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

    def exist(self):
        return False

    def create_path(self):
        info("[media] '%s' not support create path: %s" % (self.media_name, self._dst_root))

    def backup_compress(self, sources, is_disk=False):
        out_basename = self.name if "" != self.name else "BUFFY"
        encoding_str = "_" + self.encoding_str if len(self.encoding_str) > 0 else ""
        dst_base = self._dst_root + out_basename + encoding_str
        tmp_dst_base = TMP_DIR + out_basename + encoding_str
        out_base = dst_base if is_disk else tmp_dst_base
        tar_input_file = out_base + ".list"
        src_list_content = ""
        for src in sources:
            src_list_content += (src.replace(self.root, "") + "\n")
        disk_write(tar_input_file, src_list_content, self.dry)
        targz_file = "%s.tar.gz" % out_base
        compress_cmd = "tar zcvf %(dst)s -T %(src_list_file)s" \
                       % {'dst': targz_file, 'src_list_file': tar_input_file}
        os.chdir(self.root)
        if not self.dry:
            os.system("bash -c \"" + compress_cmd + " >& /dev/null\"")
        if not is_disk:
            cp_cmd = self.copyfile("%s.tar.gz" % tmp_dst_base, "%s.tar.gz" % dst_base)
            if not self.dry:
                os.remove(targz_file)
        report_str = ("cd %s\n" % self.root) + compress_cmd + "\n" if is_disk else \
            "cd %(src_dir)s\n%(cmp_cmd)s\n%(cp_cmd)s\n" \
            % {'src_dir': self.root, 'cmp_cmd': compress_cmd, 'cp_cmd': cp_cmd}
        return out_base + ".txt", report_str

    def backup_uncompress(self, sources, delim, report_dir):
        backup_map = collections.OrderedDict()
        backup_name = self.encoding_str if not self.name else \
            self.name + ("_" + self.encoding_str if len(self.encoding_str) > 0 else "")
        dst_base = self._dst_root + backup_name + (delim if len(backup_name) > 0 else "")
        for src in sources:
            dirname, _ = os.path.split(src)
            dst_dir = (dirname + delim).replace(self.root, '')
            dst = dst_base + dst_dir + os.path.basename(src)
            backup_map[src] = dst
            assert not os.path.isdir(src)
            self.copyfile(src, dst)
        report_file = report_dir + ("BUFFY" if "" == backup_name else backup_name) + ".txt"
        return report_file, MediaBase.get_mapping_str(backup_map)

    def back_up(self, sources):
        info("[%s] back up to dst: %s" % (self.media_name, self._dst_root))
        backup_ftor = self.backup_compress if self.compress else self.backup_uncompress
        report_file, report_str = backup_ftor(sources)
        report_str_max_length = 1024 * 1024  # 1MB
        if len(report_str) > report_str_max_length:
            message = "skip dump subsequent report for the total size (%s) is too large" % len(report_str)
            info("[info] %s" % message)
            report_str = report_str[:report_str_max_length] + "\n...\n" + message
        # TODO: we might need a notification scheme, instead of simply report to file
        disk_write(report_file, report_str, self.dry)

    @staticmethod
    def get_encoding(enable):
        if not enable:
            return ""
        from datetime import date
        return str(date.today()).replace("-", "")

    @staticmethod
    def get_mapping_str(mapping):
        mapping_str = ""
        for src_to_dst in mapping:
            mapping_str += (src_to_dst + " => " + mapping[src_to_dst] + "\n")
        return mapping_str
