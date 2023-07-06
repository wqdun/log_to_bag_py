#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from sensor_msgs.msg import PointCloud2, PointField
import rosbag2_py


class Log2BagWriter(Node):
    def __init__(self):
        super().__init__('log2bag_writer')
        self.writer = rosbag2_py.SequentialWriter()

        storage_options = rosbag2_py._storage.StorageOptions(
            uri='log_bag',
            storage_id='mcap')
        converter_options = rosbag2_py._storage.ConverterOptions('', '')
        self.writer.open(storage_options, converter_options)

        topic_info = rosbag2_py._storage.TopicMetadata(
            name='log_radar',
            type='sensor_msgs/msg/PointCloud2',
            serialization_format='cdr')
        self.writer.create_topic(topic_info)
        return

    # reference: https://blog.csdn.net/qq_44992157/article/details/130662947
    def write_points_to_bag(self):
        self.get_logger().info('write_points_to_bag')
        msg = PointCloud2()
        POINTS_COUNT = 10000

        msg.header.frame_id = 'map'
        msg.height = 1
        msg.width = POINTS_COUNT
        msg.is_dense = True
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1)
        ]
        msg.point_step = 16
        msg.fields = fields

        import random
        import numpy as np
        import time
        pub = self.create_publisher(PointCloud2, 'colored_point_cloud', 10)
        while True:
            time.sleep(1)

            point_data = []
            for i in range(POINTS_COUNT):
                x, y, z = 10 * random.random(), 10 * random.random(), 10 * random.random()
                r, g, b = 255 * random.random(), 255 * random.random(), 255 * random.random()
                rgb = (int(r) << 16) | (int(g) << 8) | int(b)
                point_data.append([x, y, z, rgb])
            msg.data = np.asarray(point_data, dtype=np.float32).tobytes()
            msg.header.stamp = self.get_clock().now().to_msg()

            pub.publish(msg)
            self.writer.write(
                'log_radar',
                serialize_message(msg),
                self.get_clock().now().nanoseconds)
        return


def main(args=None):
    rclpy.init(args=args)
    log2bag = Log2BagWriter()
    log2bag.write_points_to_bag()

    rclpy.spin(log2bag)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
