#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def adjust_path():
    pre_path_list = []
    import sys
    for path in sys.path:
        if "BUFFY" in path:
            pre_path_list.append(path)
    for path in pre_path_list:
        sys.path.insert(0, path)
