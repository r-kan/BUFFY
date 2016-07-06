#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class MediaBase(object):
    def __init__(self, dst_root, setting):
        self._dst_root = dst_root
        self.root = setting.src.root
        self.name = setting.name
        self.compress = setting.compress
        self.encoding_str = MediaBase.get_encoding(setting.encoding)

    def exist(self):
        return False

    def backup_compress(self, sources):
        assert False

    def backup_uncompress(self, sources):
        assert False

    def create_path(self):
        logging.info("[media] not support create path: %s" % self._dst_root)

    def back_up(self, sources):
        logging.info("[media] not support back up: %s" % self._dst_root)

    @staticmethod
    def get_encoding(enable):
        if not enable:
            return ""
        from datetime import date
        return str(date.today()).replace("-", "")
