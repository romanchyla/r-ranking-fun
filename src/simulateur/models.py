# -*- coding: utf-8 -*-
"""
    solr.models
    ~~~~~~~~~~~~~~~~~~~~~

    Models for the users (users) of AdsWS
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from adsmutils import get_date
import json

Base = declarative_base()

from sqlalchemy import types
from dateutil.tz import tzutc
from datetime import datetime

class UTCDateTime(types.TypeDecorator):
    impl = TIMESTAMP
    def process_bind_param(self, value, engine):
        if isinstance(value, basestring):
            return get_date(value).astimezone(tzutc())
        elif value is not None:
            return value.astimezone(tzutc()) # will raise Error is not datetime

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=tzutc())
            
class Experiment(Base):
    __tablename__ = 'experiments'
    eid = Column(Integer, primary_key=True)
    query = Column(String(1024)) # this serves as a title
    experiment_params = Column(Text)
    query_results = Column(Text)
    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime)
    started = Column(UTCDateTime)
    finished = Column(UTCDateTime)
    reporter = Column(String(1024))
    relevant = Column(Text)
    progress = Column(Integer)
    experiment_results = Column(Text)
    
    def toJSON(self):
        """Returns value formatted as python dict."""
        return {
            'eid': self.eid,
            'reporter': self.reporter,
            'query': self.query or None,
            'experiment_params': json.loads(self.experiment_params or '{}'),
            'query_results': json.loads(self.query_results or '{}'),
            'created': self.created and get_date(self.created).isoformat() or None,
            'updated': self.updated and get_date(self.updated).isoformat() or None,
            'started': self.updated and get_date(self.started).isoformat() or None,
            'finished': self.updated and get_date(self.finished).isoformat() or None,
            'relevant': self.relevant and json.loads(self.relevant) or [],
            'progress': self.progress,
            'experiment_results': self.experiment_results and json.loads(self.experiment_results) or {}
        }