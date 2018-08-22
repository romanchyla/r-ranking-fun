# -*- coding: utf-8 -*-
"""
    solr.models
    ~~~~~~~~~~~~~~~~~~~~~

    Models for the users (users) of AdsWS
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Experiment(Base):
    __tablename__ = 'experiments'
    eid = Column(Integer, primary_key=True)
    query = Column(String(1024))
    query_params = Column(String(1024))
    description = Column(Text)
    experiment_params = Column(Text)
    
    def toJSON(self):
        """Returns value formatted as python dict."""
        return {
            'eid': self.eid,
            'description': self.description or None
        }