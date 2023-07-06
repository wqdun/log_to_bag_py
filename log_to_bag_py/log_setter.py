#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging


def get_logger(moduleName):
    fmt = '[%(levelname)s]%(thread)d %(asctime)s %(name)s:%(lineno)d %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt, stream=sys.stdout)
    return logging.getLogger(moduleName)


if __name__ == '__main__':
    logTester = get_logger('TEST')

    logTester.debug('debug')
    logTester.info('info')
    logTester.warning('warning')
    logTester.error('error')
    logTester.critical('critical')
