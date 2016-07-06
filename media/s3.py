#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from media.base import MediaBase


class S3(MediaBase):
    def __init__(self, dst_root, setting):
        super(S3, self).__init__(dst_root, setting)
