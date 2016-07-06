#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from media.disk import Disk
from media.s3 import S3


def create_media(media_path, setting):
    assert media_path and type(media_path) is str and "" != media_path
    if "s3" in media_path:
        return S3(media_path, setting)
    return Disk(media_path, setting)
