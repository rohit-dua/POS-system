#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com


import sys
from flask import Flask, jsonify
import json
from flask import make_response, request, url_for, abort

from flask_sqlalchemy import sqlalchemy

from app import app, db, models

VALID_ITEM_PARAMETERS = ['code', 'name', 'size', 'color', 'quality']
VALID_VARIANT_PARAMETERS = ['cost_price', 'selling_price', 'quantity', 'code']



def invalid_requeset(code=400, message='Invalid Request'):
    return make_response(jsonify({'error': message}), code)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def log(action, table, parameters, user):
	u = models.Log(action=action, table=table, parameters=json.dumps(parameters), user=user)
	db.session.add(u)
	db.session.commit()


@app.route('/api/v1.0/item/<int:item_code>', methods=['GET'])
def get_item(item_code):
    """Display information about item"""
    u = models.Items.query.filter_by(code=item_code).first()
    valid_dict = dict()
    if u is not None:
        for p in u.__dict__:
            if p in VALID_ITEM_PARAMETERS:
                valid_dict[p] = u.__dict__[p]
    u = models.Variants.query.filter_by(code=item_code).first()
    if u is not None:
        for p in u.__dict__:
            if p in VALID_VARIANT_PARAMETERS:
                valid_dict[p] = u.__dict__[p]
    return make_response(jsonify(valid_dict))


@app.route('/api/v1.0/notifications/', methods=['GET'])
@app.route('/api/v1.0/notifications/<int:limit>', methods=['GET'])
@app.route('/api/v1.0/notifications/user/<user>', methods=['GET'])
def get_notification(limit=10, user=None):
	"""Display notifications globally or user specific"""
	if user is not None:
		u = models.Log.query.filter_by(user=user).order_by(models.Log.timestamp.desc()).limit(limit).all()
	else:
		u = models.Log.query.order_by(models.Log.timestamp.desc()).limit(limit).all()
	notifications = []
	for i in u:
		parameters = json.loads(i.parameters)
		item_code = parameters['code']
		del parameters['code']
		if i.action == 'updated':
			notifications.append("%s: %s %s %s of item %s on table %s" %(i.timestamp, i.user, i.action, ','.join(parameters.keys()), item_code, i.table))
		elif i.action == 'deleted':
			notifications.append("%s: %s %s %s of item %s." %(i.timestamp, i.user, i.action, "entry", item_code))
		else:
			notifications.append("%s: %s %s %s of item %s on table %s" %(i.timestamp, i.user, i.action, "new entry", item_code, i.table))
	return make_response(jsonify(notifications))



@app.route('/api/v1.0/item', methods=['POST'])
def create_item():
    """Create Item with unique code"""
    if not request.json:
        abort(400)
    for param in VALID_ITEM_PARAMETERS:
        if param not in request.json:
            return invalid_requeset()
    if not isinstance(request.json,dict):
        return invalid_requeset()
    data = request.json
    valid_dict = dict()
    if 'user' not in data:
    	return invalid_requeset(message="user missing")
    for p in VALID_ITEM_PARAMETERS:
        valid_dict[p] = data[p]
    try:
        u = models.Items(**valid_dict)
        db.session.add(u)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError, e:
        return make_response(jsonify({'error': 'item code already exists.'}), 400)
    log(action='created', table='items', parameters=valid_dict, user=request.json['user'])
    return make_response(jsonify({'success': True}))


@app.route('/api/v1.0/variant', methods=['POST'])
def create_item_variant():
    """Create item variant with unique code"""
    if not request.json:
        abort(400)
    for param in VALID_VARIANT_PARAMETERS:
        if param not in request.json:
            return invalid_requeset()
    if not isinstance(request.json,dict):
        return invalid_requeset()
    data = request.json
    if 'user' not in data:
    	return invalid_requeset(message="user missing")
    valid_dict = dict()
    for p in VALID_VARIANT_PARAMETERS:
        valid_dict[p] = data[p]
    try:
        u = models.Variants(**valid_dict)
        db.session.add(u)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError, e:
        return make_response(jsonify({'error': 'item code already exists.'}), 400)
    log(action='created', table='variants', parameters=valid_dict, user=request.json['user'])
    return make_response(jsonify({'success': True}))



@app.route('/api/v1.0/item/<int:item_code>', methods=['PUT'])
def update_item(item_code):
    """Update item properties"""
    if not request.json:
        abort(400)
    valid_dict = dict()
    if not isinstance(request.json,dict):
        return invalid_requeset()
    if 'user' not in request.json:
    	return invalid_requeset(message="user missing")
    for param in request.json:
        if param in VALID_ITEM_PARAMETERS and param != 'code':
            valid_dict[param] = request.json[param]
    if valid_dict == {}:
        return invalid_requeset()
    u = models.Items.query.filter_by(code=item_code).first()
    if u is None:
        return invalid_requeset(message='Item code does not exists')
    for param in valid_dict:
        setattr(u, param, valid_dict[param]) 
    db.session.commit()
    valid_dict['code'] = item_code
    log(action='updated', table='items', parameters=valid_dict, user=request.json['user'])
    return make_response(jsonify({'success': True}))


@app.route('/api/v1.0/variant/<int:item_code>', methods=['PUT'])
def update_variant(item_code):
    """Update item variant options"""
    if not request.json:
        abort(400)
    valid_dict = dict()
    if not isinstance(request.json,dict):
        return invalid_requeset()
    if 'user' not in request.json:
    	return invalid_requeset(message="user missing")
    for param in request.json:
        if param in VALID_VARIANT_PARAMETERS and param != 'code':
            valid_dict[param] = request.json[param]
    if valid_dict == {}:
        return invalid_requeset()
    u = models.variants.query.filter_by(code=item_code).first()
    if u is None:
        return invalid_requeset(message='Item code does not exists')
    for param in valid_dict:
        setattr(u, param, valid_dict[param]) 
    db.session.commit()
    valid_dict['code'] = item_code
    log(action='updated', table='items', parameters=valid_dict, user=request.json['user'])
    return make_response(jsonify({'success': True}))




@app.route('/api/v1.0/item/<int:item_code>', methods=['DELETE'])
def delete_item(item_code):
    """Delete item"""
    if not request.json:
        abort(400)
    valid_dict = dict()
    if not isinstance(request.json,dict):
        return invalid_requeset()
    if 'user' not in request.json:
    	return invalid_requeset(message="user missing")
    models.Items.query.filter_by(code=item_code).delete()
    models.Variants.query.filter_by(code=item_code).delete()
    db.session.commit()
    log(action='deleted', table=None, parameters=dict(code=item_code), user=request.json['user'])
    return make_response(jsonify({'success': True}))



if __name__ == '__main__':
    app.run(debug=True)
