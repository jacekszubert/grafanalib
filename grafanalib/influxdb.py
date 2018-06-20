"""Helpers to create InfluxDB-specific Grafana queries."""

import attr
import itertools
from attr.validators import instance_of

TIME_SERIES_TARGET_FORMAT = "time_series"

DEFAULT_STEP = 10


@attr.s
class InfluxdbTarget(object):
    """Generates InfluxDB target JSON structure.

    :param query: query
    """

    alias = attr.ib(default='')
    dsType = attr.ib(default='influxdb')
    measurement = attr.ib(default='')
    orderByTime = attr.ib(default='ASC')
    policy = attr.ib(default='default')
    refId = attr.ib(default='A')
    resultFormat = attr.ib(default='time_series')
    select_param = attr.ib(default='')
    select_type = attr.ib(default='')
    tags = attr.ib(default='')
    query = attr.ib(default='')
    rawQuery = attr.ib(default=True)
    groupBy = attr.ib(default='')

    def to_json_data(self):

        tag_operator = self.tags[0]['operator']
        tag_value = self.tags[0]['value']
        tag_key = self.tags[0]['key']

        if tag_operator != '=~':
            tag_value = '\'{}\''.format(tag_value)

        query = self.query or 'SELECT {select_type}({select_param}) \
                                FROM {measurement} \
                                WHERE ("{tag_key}" {tag_operator} {tag_value}) AND $timeFilter \
                                GROUP BY time($__interval) fill(null)'.format(
                                    select_type=self.select_type,
                                    select_param=self.select_param,
                                    measurement=self.measurement,
                                    tag_key=tag_key,
                                    tag_operator=tag_operator,
                                    tag_value=tag_value
                                )
        query = ' '.join(query.split())

        groupBy = self.groupBy or [
            {
                "params": [
                    "$__interval"
                ],
                "type": "time"
            },
            {
                "params": [
                    "null"
                ],
                "type": "fill"
            }
        ]

        return {
            'alias': self.alias,
            'dsType': self.dsType,
            'measurement': self.measurement,
            'orderByTime': self.orderByTime,
            'policy': self.policy,
            'refId': self.refId,
            'resultFormat': self.resultFormat,
            'select': [[
                {
                    'params': [self.select_param],
                    'type': 'field'
                },
                {
                    'params': [],
                    'type': self.select_type
                }
            ]],
            'tags': self.tags,
            'query': query,
            'rawQuery': self.rawQuery,
            'groupBy': self.groupBy
        }
