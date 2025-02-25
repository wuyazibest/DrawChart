#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : single_logging.py
# @Time   : 2023/7/27 11:57
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging
import os
import sys

from logging.handlers import RotatingFileHandler
from flask import Flask, has_request_context, request, json

from main import config

try:
    import fcntl
except:
    pass


def setup_log(level_name):
    formatter_simple = logging.Formatter("%(levelname)-8s %(asctime)s %(filename)s:%(lineno)d %(message)s")
    formatter_long = UnwrapFormatter(
        "%(levelname)-8s %(asctime)s %(name)s %(filename)s:%(lineno)d:%(funcName)s "
        "%(request_method)s %(request_path)s %(request_addr)s %(message)s")
    
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter_simple)
    handler_console.setLevel(logging.DEBUG)
    
    handler_file = FlockRotatingFileHandler(os.path.join(config.BASE_DIR, f"log/log.log"),
                                            maxBytes=1024 * 1024 * 400, backupCount=0, encoding="utf-8")
    handler_file.setFormatter(formatter_long)
    handler_file.setLevel(logging.DEBUG)
    
    handler_err = FlockRotatingFileHandler(os.path.join(config.BASE_DIR, f"log/err.log"),
                                           maxBytes=1024 * 1024 * 400, backupCount=0, encoding="utf-8")
    handler_err.setFormatter(formatter_long)
    handler_err.setLevel(logging.ERROR)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level_name.upper()))
    logger.addHandler(handler_console)
    logger.addHandler(handler_file)
    logger.addHandler(handler_err)
    
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").propagate = False


class FlockRotatingFileHandler(RotatingFileHandler):
    log_flag_path = os.path.join(config.BASE_DIR, f"log/keepgit")
    
    def reload(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        
        if not self.delay:
            self.stream = self._open()
    
    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                if sys.platform.startswith('linux'):
                    with open(self.log_flag_path, 'w') as f:
                        fcntl.lockf(f.fileno(), fcntl.LOCK_EX)
                        try:
                            self.reload()
                            if self.shouldRollover(record):
                                self.doRollover()
                        except Exception as e:
                            print(f"日志轮转错误pid[{os.getpid()}] err:{e}")
                        finally:
                            fcntl.lockf(f.fileno(), fcntl.LOCK_UN)
                else:
                    self.doRollover()
            
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)


class UnwrapFormatter(logging.Formatter):
    """强制日志不换行
    """
    
    def format(self, record):
        if has_request_context():
            record.request_method = request.method.upper()
            record.request_path = request.path
            record.request_addr = request.remote_addr
        else:
            record.request_method = ""
            record.request_path = ""
            record.request_addr = ""
        
        s = super(UnwrapFormatter, self).format(record)
        s = s.strip().replace("\r", " ").replace("\n", " ")
        return s
