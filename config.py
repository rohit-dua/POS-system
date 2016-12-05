#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')