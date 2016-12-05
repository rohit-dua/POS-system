#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com

	
from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path
db.create_all()