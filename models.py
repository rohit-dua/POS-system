#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com


from app import db
import datetime
from flask_sqlalchemy import sqlalchemy
from sqlalchemy_utils import observes
from sqlalchemy import orm, event
from flask import session
import enum
import random


from sqlalchemy.orm import scoped_session, sessionmaker, sessionmaker
ss1 = scoped_session(sessionmaker())

class Items(db.Model):
    __tablename__ = 'Items'

    item_code = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(100))
    size_code = db.Column(db.Integer, db.ForeignKey("Size.size_code"), nullable=False)
    color_code = db.Column(db.Integer, db.ForeignKey("Color.color_code"), nullable=False)
    quality_code = db.Column(db.Integer, db.ForeignKey("Quality.quality_code"), nullable=False)
    #alive = db.Column(db.Boolean, default=True)

    variants = orm.relationship("Variants", uselist=False, cascade="all, delete-orphan")


class DeletedItems(db.Model):
    __tablename__ = 'DeletedItems'

    item_code = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(100))


class Quality(db.Model):
    __tablename__ = 'Quality'

    quality_code = db.Column(db.Integer, primary_key = True, autoincrement=True)
    quality_name = db.Column(db.String(100))

class Color(db.Model):
    __tablename__ = 'Color'

    color_code = db.Column(db.Integer, primary_key = True, autoincrement=True)
    color_name = db.Column(db.String(100))

class Size(db.Model):
    __tablename__ = 'Size'

    size_code = db.Column(db.Integer, primary_key = True, autoincrement=True)
    size_name = db.Column(db.String(100))
    # Size in centimeters

class Variants(db.Model):
    __tablename__ = 'Variants'

    item_code = db.Column(db.Integer, db.ForeignKey("Items.item_code"), primary_key = True, autoincrement=True)
    cost_price = db.Column(db.Float())
    selling_price = db.Column(db.Float())
    quantity = db.Column(db.Integer)

    #item = orm.relationship("Items", back_populates="variants")

class Log(db.Model):
    __tablename__ = 'Log'

    log_code = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.Enum('I', 'U', 'D', 'IV', name='action_types'))
    user_code = db.Column(db.Integer, db.ForeignKey("Users.user_code"))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    item_code = db.Column(db.Integer, db.ForeignKey("Items.item_code"), nullable=False)

    parameters = orm.relationship("LoggedParameters", lazy='dynamic')
    #read = db.Column(db.Boolean(), default=False)
    

class LoggedParameters(db.Model):
    __tablename__ = 'LoggedParameters'

    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_code = db.Column(db.Integer, db.ForeignKey("Log.log_code"), nullable=False)
    parameter = db.Column(db.String(100))


class Users(db.Model):
    __tablename__ = 'Users'

    user_code = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))


        
############ITEMS##########
# After Update
@event.listens_for(Items, 'after_update')
def after_update_item(mapper, connection, target):
    state = db.inspect(target)
    u = Log(item_code=target.item_code, action='U')
    u.user_code = session['user_code']
    for attr in state.attrs:
        hist = state.get_history(attr.key, True)
        if not hist.has_changes():
            continue
        p = LoggedParameters(parameter=str(attr.key))
        u.parameters.append(p)
    state.session.add(u)


@event.listens_for(Items, 'before_insert')
def before_insert_item(mapper, connection, target):
    target.item_code = random.randint(0,10000000)

@event.listens_for(Items, 'after_insert')
def after_insert_item(mapper, connection, target):
    state = db.inspect(target)
    u = Log(item_code=target.item_code, action='I')
    u.user_code = session['user_code']
    state.session.add(u)


# After Delete
@event.listens_for(Items, 'after_delete')
def after_delete_item(mapper, connection, target):
    state = db.inspect(target)
    u = Log(item_code=target.item_code, action='D')
    d = DeletedItems(item_code=target.item_code, item_name=target.item_name)
    u.user_code = session['user_code']
    for attr in state.attrs:
        hist = state.get_history(attr.key, True)
    state.session.add(u)
    state.session.add(d)


############VARIANTS##########

@event.listens_for(Variants, 'after_update')
def after_udpate_vaiant(mapper, connection, target):
    state = db.inspect(target)
    changes = {}
    u = Log(item_code=target.item_code, action='U')
    u.user_code = session['user_code']
    for attr in state.attrs:
        hist = state.get_history(attr.key, True)
        if not hist.has_changes():
            continue
        p = LoggedParameters(parameter=str(attr.key))
        u.parameters.append(p)
    state.session.add(u)

# After Insert
@event.listens_for(Variants, 'after_insert')
def after_insert_variant(mapper, connection, target):
    state = db.inspect(target)
    changes = {}
    u = Log(item_code=target.item_code, action='IV')
    u.user_code = session['user_code']
    state.session.add(u)

"""
# After Delete
@event.listens_for(Variants, 'after_delete')
def after_delete_variant(mapper, connection, target):
    state = db.inspect(target)
    changes = {}
    u = Log(item_code=target.item_code, action='D')
    u.user_code = session['user_code']
    state.session.add(u)

"""