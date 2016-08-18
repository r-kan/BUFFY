#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


def is_windows():
    import platform
    system_name = platform.system()
    return "Windows" in system_name


def get_delim():
    import platform
    system_name = platform.system()
    if "Darwin" in system_name:
        return "/"
    elif "Linux" in system_name:
        return "/"
    elif "Windows" in system_name:
        return "\\"
    return "/"  # default treats it an unix-like system

DIR_DELIM = get_delim()

RPT_WARN_ERR = ""


def warning(msg):
    logging.warning(msg)
    global RPT_WARN_ERR
    RPT_WARN_ERR += (msg + "\n")


def error(msg):
    logging.error(msg)
    global RPT_WARN_ERR
    RPT_WARN_ERR += (msg + "\n")
