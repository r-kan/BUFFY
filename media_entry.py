#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from media.disk import Disk
from media.s3 import S3, S3_HEAD


def create_media(media_path, setting, args):
    assert media_path and type(media_path) is str and "" != media_path
    if 0 == media_path.find(S3_HEAD):
        return S3(media_path, setting, args)
    return Disk(media_path, setting, args)
