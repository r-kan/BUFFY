#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from logging import info
from media.base import MediaBase, mkdir_p
from util.global_def import DIR_DELIM


class Disk(MediaBase):
    def __init__(self, dst_root, setting, dry):
        super(Disk, self).__init__("disk", dst_root, setting, dry)
        self.cp_cmd = "cp "
        if self._dst_root[-1] != DIR_DELIM:
            self._dst_root += DIR_DELIM

    def exist(self):
        return os.path.exists(self._dst_root)

    def create_path(self):
        info("[disk] create path: %s" % self._dst_root)
        if not self.dry:
            os.mkdir(self._dst_root)

    def get_file_info_not_dry(self, filename):
        if self.dry or not os.path.exists(filename):
            return -1, "NA"
        from datetime import datetime
        timestamp = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
        return os.stat(filename).st_size, timestamp

    def copyfile(self, src, dst):
        if not self.dry:
            dirname, _ = os.path.split(dst)
            if not os.path.exists(dirname):
                mkdir_p(dirname)
            from shutil import copyfile
            copyfile(src, dst)
        size, _ = self.get_file_info_not_dry(dst)  # do not return the value 'timestamp'
        valid = -1 != size
        return valid, size if valid else 0

    def backup_compress(self, sources):
        return MediaBase.backup_compress(self, sources)

    def backup_uncompress(self, sources):
        return MediaBase.backup_uncompress(self, sources, DIR_DELIM)
