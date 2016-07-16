#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import info


class MediaBase(object):
    def __init__(self, dst_root, setting, args):
        self._dst_root = dst_root
        self.root = setting.src.root
        self.name = setting.name
        self.compress = setting.compress
        self.encoding_str = MediaBase.get_encoding(setting.encoding)
        self.dry = args.dry

    def exist(self):
        return False

    def backup_compress(self, sources):
        assert False

    def backup_uncompress(self, sources):
        assert False

    def create_path(self):
        info("[media] not support create path: %s" % self._dst_root)

    def back_up(self, sources):
        info("[media] not support back up: %s" % self._dst_root)

    @staticmethod
    def get_encoding(enable):
        if not enable:
            return ""
        from datetime import date
        return str(date.today()).replace("-", "")
