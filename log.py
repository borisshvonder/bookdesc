# -*- coding: UTF-8 -*-
"Thin layer over std python logging"

import logging

class _Config:
    def __init__(self):
        self.warnings_as_errors = False

_CONFIG = _Config()

def config(werror = False, log_level = "INFO"):
    _CONFIG.warnings_as_errors = werror
    logging.basicConfig(level=getattr(logging, log_level))


class WarningsInterceptor:
    def __init__(self, reallog):
        self._reallog = reallog

    def warning(self, msg, *args, **kwargs):
        self._reallog.warning(msg, *args, **kwargs)
        if _CONFIG.warnings_as_errors: raise RuntimeError(msg)

    def exception(self, msg, *args, **kwargs):
        self._reallog.exception(msg, *args, **kwargs)
        if _CONFIG.warnings_as_errors: raise RuntimeError(msg)

    def error(self, msg, *args, **kwargs): 
        self._reallog.error(msg, *args, **kwargs)
        if _CONFIG.warnings_as_errors: raise RuntimeError(msg)

    def critical(self, msg, *args, **kwargs):
        self._reallog.critical(msg, *args, **kwargs)
        if _CONFIG.warnings_as_errors: raise RuntimeError(msg)

    def __getattr__(self, attr):
        return getattr(self._reallog, attr)

def get(name): return WarningsInterceptor(logging.getLogger(name))
