#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

DIR_DELIM = "/"

RPT_WARN_ERR = ""


def warning(msg):
    logging.warning(msg)
    global RPT_WARN_ERR
    RPT_WARN_ERR += (msg + "\n")


def error(msg):
    logging.error(msg)
    global RPT_WARN_ERR
    RPT_WARN_ERR += (msg + "\n")
