#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from logging import info
from subprocess import Popen, PIPE, STDOUT
from media.base import MediaBase
from util.global_def import warning, error

"""
  following information is from 'aws s3 help'
  s3 terminology:
      bucket: the unique s3 identifier
      prefix: the directory name
      object: the file basename
      s3://bucket/....prefix.../object

  The path argument must begin with s3:// in order to denote that the path argument refers to a S3 object
"""

S3_HEAD = "s3://"
S3_DELIM = "/"


def pp_popen_out(out_str):
    return str(out_str).replace("b'", '').replace("\\n'", '')


def locate_abs_exec(program):  # 'program' can be an absolute path name, or just a basename
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    # try 'type' (note: mac os may need this)
    type_cmd = Popen(["type", program], stdout=PIPE, stderr=STDOUT)
    stdout_data, _ = type_cmd.communicate()
    out = pp_popen_out(stdout_data).replace("%s is " % program, '')
    if is_exe(out):
        return out
    return None


def get_aws_path():
    return locate_abs_exec("aws")


class S3(MediaBase):
    def __init__(self, dst_root, setting, args):
        assert 0 == dst_root.find(S3_HEAD)
        super(S3, self).__init__("s3", dst_root, setting, args)
        if self._dst_root[-1] != S3_DELIM:
            self._dst_root += S3_DELIM
        aws_path = get_aws_path()
        if not aws_path:
            error("[s3] cannot locate aws")
            self.okay = False
            return
        self.aws = aws_path
        self.cp_cmd = self.aws + " s3 cp "  # use for logging
        wo_head_path = self._dst_root[len(S3_HEAD):]
        end_bucket = wo_head_path.find(S3_DELIM)
        bucket = wo_head_path if -1 == end_bucket else wo_head_path[:end_bucket]
        check_bucket_cmd = "%(aws)s s3 ls %(bucket)s" % {'aws': self.aws, 'bucket': bucket}
        info("[s3] checking bucket '%s' existence..." % bucket)
        res = os.system("bash -c \"" + check_bucket_cmd + " >& /dev/null\"")
        self.okay = 0 == res
        if not self.okay:
            warning("[s3] fail to locate bucket '%s' (err: %s)" % (bucket, res))

    def create_path(self):
        pass

    def get_file_info_not_dry(self, filename):
        if self.dry:
            return -1, "NA"
        cmd_list = [self.aws, "s3", "ls", filename]
        stdout_data, _ = Popen(cmd_list, stdout=PIPE, stderr=STDOUT).communicate()
        ls_out_list = pp_popen_out(stdout_data).split()
        if not 4 == len(ls_out_list):
            warning("[s3] ls %s gives unexpected result" % filename)
            return -1, "NA"
        [day, time, size, _] = ls_out_list
        return int(size), day + " " + time

    def copyfile(self, src, dst):
        cmd_list = [self.aws, "s3", "cp", src, dst]
        if not self.dry:
            stdout_data, _ = Popen(cmd_list, stdout=PIPE, stderr=STDOUT).communicate()
        size, _ = self.get_file_info_not_dry(dst)  # do not use the value 'timestamp'
        valid = -1 != size
        return valid, size if valid else 0

    def backup_uncompress(self, sources):
        return MediaBase.backup_uncompress(self, sources, S3_DELIM)

    def back_up(self, sources):
        if not self.okay:
            warning("[s3] skip to back up to destination '%s'" % self._dst_root)
            return
        return MediaBase.back_up(self, sources)
