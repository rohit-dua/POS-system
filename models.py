#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com


from app import db
import datetime


class Items(db.Model):
	code = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	size = db.Column(db.String(50))  
	color = db.Column(db.String(200))
	quality = db.Column(db.String(10))

class Variants(db.Model):
	code = db.Column(db.Integer, primary_key = True)
	cost_price = db.Column(db.Float())
	selling_price = db.Column(db.Float())
	quantity = db.Column(db.Integer)

class Log(db.Model):
	sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
	action = db.Column(db.String(50)) #created Update Delete
	user = db.Column(db.String(50))
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	table = db.Column(db.String(50))
	parameters = db.Column(db.String(50))
	#read = db.Column(db.Boolean(), default=False)