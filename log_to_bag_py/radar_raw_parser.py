#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import struct

import log_setter
logger = log_setter.get_logger(__name__)


class RadarPoint(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        return


# reference:
# https://dev.sankuai.com/code/repo-detail/walle/mtuav-mendel-topics/file/detail?branch=dev&path=radar_u100.h
class RadarRawParser():
    # def __init__(self):
    #     return

    def parse(self, raw_file):
        logger.info('parse start, raw_file: {}.'.format(raw_file))
        size = os.path.getsize(raw_file)
        fp = open(raw_file, 'rb')

        ts2cloud = {}
        while True:
            # reference: struct data_header in:
            #     https://dev.sankuai.com/code/repo-detail/walle/mtuav-mendel/file/detail?
            #         path=src%2Fapps%2Fdata_acquisition_agent%2Ftools%2Fbag_creator%2Fsrc%2Fbag_creator.cpp
            #     struct timeval tv;
            #     unsigned int len;
            fmt = '2QI'
            # bytes_to_read: 20
            bytes_to_read = struct.calcsize(fmt)
            data = fp.read(bytes_to_read)
            if len(data) != bytes_to_read:
                logger.info('file: {} end, data: {}, bytes_to_read: {}.'.format(raw_file, data, bytes_to_read))
                break

            tv_sec, tv_usec, length = struct.unpack(fmt, data)
            tv = tv_sec + tv_usec / 1000000.
            # logger.info('tv: {}.'.format(tv))

            data = fp.read(length)
            if len(data) != length:
                logger.error('Failed to parse file: {}, data: {}, length: {}.'.format(raw_file, data, length))
                sys.exit(1)

            cloud = self.parse_radar_cloud(data)
            ts2cloud[tv] = cloud

        fp.close()
        # for ts, cloud in ts2cloud.items():
        #     print(ts, len(cloud))

        return

    def parse_radar_cloud(self, buf):
            # reference: struct _TOPIC_RADAR_POINTER_V1_TAG in radar_u100.h
            #     uint8_t func_type;
            #     uint8_t firmware_version;
            #     float radar_starttime;
            #     float chip_temp;
            #     float radar_endtime;
            #     uint16_t cloud_nums;
            #     uint32_t reserve_val;
            #     uint8_t point_type;
            #     float peakval[64];
            #     float speed[64];
            #     float range[64];
            #     float sin_azi[64];
            #     uint8_t feature1[64];
            #     uint8_t feature2[64];
            #     uint8_t feature3[64];
            #     uint8_t confid[64];
            #     struct timeval ts;
            #     uint32_t firmware_version;
            #     uint16_t frame_id;
            #     uint8_t work_state;
            fmt = '2B3fHIB256f256B2QIHBx'
            # fmt size: 1336
            # logger.info('fmt size: {}.'.format(struct.calcsize(fmt)))
            radarData = struct.unpack(fmt, buf)

            # radar_starttime = radarData[2]
            # radar_endtime = radarData[4]
            cloud_nums = radarData[5]
            # peakval0 = radarData[8]
            # range0 = radarData[8 + 64 + 64]
            # sin_azi0 = radarData[8 + 64 + 64 + 64]
            # ts_sec = radarData[520]
            # ts_nsec = radarData[521]
            # ts = ts_sec + ts_nsec / 1000000.

            # print('radarData length: %d' % len(radarData))
            # print('radar_starttime: %.6f' % radar_starttime)
            # print('radar_endtime: %.6f' % radar_endtime)
            # print('cloud_nums: %d' % cloud_nums)
            # print('peakval0: %f' % peakval0)
            # print('range0: %f' % range0)
            # print('sin_azi0: %f' % sin_azi0)

            if cloud_nums < 0 or cloud_nums > 64:
                logger.error('Failed to parse_radar_cloud, cloud_nums: {}.'.format(cloud_nums))
                sys.exit(1)

            cloud = []
            for point_index in range(cloud_nums):
                _range = radarData[8 + 64 + 64 + point_index]
                _sin_azi = radarData[8 + 64 + 64 + 64 + point_index]
                cloud.append(RadarPoint(range_=_range, sin_azi_=_sin_azi))

            if not cloud:
                logger.warning('Got an empty cloud: {}.'.format(cloud))
                return []

            # for point in cloud:
            #     print('point.sin_azi_: ', point.sin_azi_)
            return cloud


if __name__ == '__main__':
    raw_parser = RadarRawParser()
    raw_parser.parse('/share/Documents/radar/radar.raw')
