# -*- coding: utf-8 -*-
__author__ = 'velocidad'

errors = dict(
    remote_404=dict(message='Remote address not found', code='001'),
    remote_timeout=dict(message='The request timed out', code='002'),
    id_error=dict(message='Unknown IMDb id format', code='003'),
)

messages = dict(
    exception_restart="exception occured, restart",
    non_controlled="Non controled error, migth be a time out or the "
                   "connection was reseted"
)