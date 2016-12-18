#!/usr/bin/python2
# -*- coding: utf-8 -*-
# By: <Rohit Dua>8ohit.dua AT gmail DOT  com


import sys
from flask import Flask, jsonify
import json
from flask import make_response, request, url_for, abort

from flask_sqlalchemy import sqlalchemy
from flask_restful import reqparse


from app import app, db, models, session


def invalid_requeset(code=400, message='Invalid Request'):
    return make_response(jsonify({'error': message}), code)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

"""
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)
"""


def get_user_code(username):
    u = models.Users.query.filter_by(username=username).first()
    if u is None:
        return None
    else:
        session['username'] = username
        session['user_code'] = u.user_code
        return u.user_code


@app.route('/api/v1.0/item/<int:item_code>', methods=['GET'])
def get_item(item_code):
    """Display information about item"""
    u = models.Items.query.filter_by(code=item_code).first()
    u_dict = u.__dict__
    item = dict(
        item_code = u_dict['item_code'],
        item_name = u_dict['item_name'],
        size_code = get_size_code( u_dict['size_code']),
        color_code = get_color_code( u_dict['color_code']),
        quality_code = get_quality_code( u_dict['quality_code']),
        cost_price = u_dict['variants']['cost_price'],
        selling_price = u_dict['variants']['selling_price'],
        quantity = u_dict['variants']['quantity']
        )
    return make_response(jsonify(item))



def extract_parameters(parameters):
    l=[]
    for p in parameters:
        l.append(p.parameter)
    return ', '.join(l)


def get_color_code(color):
    u = models.Color.query.filter_by(color_name=color).first()
    if u is not None:
        return u.color_code
    else:
        return u

def get_quality_code(quality):
    u = models.Quality.query.filter_by(quality_name=quality).first()
    if u is not None:
        return u.quality_code
    else:
        return u

def get_size_code(size):
    u = models.Size.query.filter_by(size_name=size).first()
    if u is not None:
        return u.size_code
    else:
        return u 

def get_item_name(item_code):
    u = models.Items.query.filter_by(item_code=item_code).first()
    if u is not None:
        return u.item_name
    else:
        u = models.DeletedItems.query.filter_by(item_code=item_code).first()
        if u:
            return u.item_name
        else:
            return u     

def get_username(user_code):
    u = models.Users.query.filter_by(user_code=user_code).first()
    if u is not None:
        return u.username
    else:
        return u        


@app.route('/api/v1.0/notifications/', methods=['GET'])
@app.route('/api/v1.0/notifications/<int:limit>', methods=['GET'])
@app.route('/api/v1.0/notifications/user/<username>', methods=['GET'])
def get_notification(limit=10, username=None):
    """Display notifications globally or user specific"""
    if username is not None:
        user_code = get_user_code(username)
        if user_code is None:
            return make_response(jsonify({'error': 'User does not exists'}), 400)
        u = models.Log.query.filter_by(user_code=user_code).order_by(models.Log.timestamp.desc()).limit(limit).all()
    else:
        u = models.Log.query.order_by(models.Log.timestamp.desc()).limit(limit).all()
    notifications = []
    for i in u:
        parameters = extract_parameters(i.parameters)
        item_name = get_item_name(i.item_code)
        username = get_username(i.user_code)
        if i.action == 'U':
            notifications.append("%s: %s %s %s of item %s(code:%s)" %(i.timestamp, username, "Updated", parameters, item_name, i.item_code))
        elif i.action == 'D':
            notifications.append("%s: %s %s %s of item %s(code:%s)" %(i.timestamp, username, "Deleted", "entry", item_name, i.item_code))
        elif i.action == 'IV':
            notifications.append("%s: %s %s %s of item %s(code:%s)" %(i.timestamp, username, "Inserted", "new variants", item_name, i.item_code))
        else:
            notifications.append("%s: %s %s %s of item %s(code:%s)" %(i.timestamp, username, "Inserted", "new entry", item_name, i.item_code))
    return make_response(jsonify(notifications))





@app.route('/api/v1.0/user', methods=['POST'])
def create_user():
    """Create New User"""
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="Username missing")
    parser.add_argument('name', type=str, required=True, help="Name missing")
    args = parser.parse_args(strict=True)
    user_code = get_user_code(args['username'])
    if user_code is not None:
        return make_response(jsonify({'error': 'Username taken'}), 400)
    new_user = dict(
        username = args['username'],
        name = args['name']
        )
    u = models.Users(**new_user)
    db.session.add(u)
    db.session.commit()    
    return make_response(jsonify({'success': True}))



@app.route('/api/v1.0/users/', methods=['GET'])
@app.route('/api/v1.0/users/<int:limit>', methods=['GET'])
def show_user(limit=10):
    if limit > 20:
        limit = 20
    u = models.Users.query.limit(limit).all()
    users = list()
    for i in u:
        users.append(dict(username=i.username, name=i.name, user_code=i.user_code))
    return make_response(jsonify(users))


@app.route('/api/v1.0/properties', methods=['POST'])
def add_properties():
    parser = reqparse.RequestParser()
    parser.add_argument('size', type=str, required=False)
    parser.add_argument('color', type=str, required=False)
    parser.add_argument('quality', type=str, required=False)   
    args = parser.parse_args(strict=True)
    if 'size' in args.keys() and args['size'] != None:
        u=models.Size(size_name=args['size'])
        db.session.add(u)
    if 'color' in args.keys() and args['color'] != None:
        u=models.Color(color_name=args['color'])
        db.session.add(u)
    if 'quality' in args.keys() and args['quality'] != None:
        u=models.Quality(quality_name=args['quality'])
        db.session.add(u)
    db.session.commit()
    return make_response(jsonify({'success': True}))


@app.route('/api/v1.0/properties', methods=['GET'])
def get_properties():
    """View available options in properties"""
    properties = dict()
    properties['size'] = list()
    properties['color'] = list()
    properties['quality'] = list()
    u = models.Size.query.all()
    for i in u:
        properties['size'].append(i.size_name)
    u = models.Color.query.all()
    for i in u:
        properties['color'].append(i.color_name)
    u = models.Quality.query.all()
    for i in u:
        properties['quality'].append(i.quality_name)
    return make_response(jsonify(properties))




@app.route('/api/v1.0/item', methods=['POST'])
def create_item():
    """Create Item with unique code"""
    #if not request.json:
    #    abort(400)
    parser = reqparse.RequestParser()
    parser.add_argument('item_code', type=int, required=False, help="Item code missing")
    parser.add_argument('item_name', type=str, required=True, help="Item name missing")
    parser.add_argument('size', type=str, required=True, help="Size missing")
    parser.add_argument('color', type=str, required=True, help="Color missing")
    parser.add_argument('quality', type=str, required=True, help="Quality missing")
    parser.add_argument('username', type=str, required=True, help="Username missing")
    args = parser.parse_args(strict=True)
    user_code = get_user_code(args['username'])
    if user_code is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)
    new_item = dict(
        item_code = args['item_code'],
        item_name = args['item_name'],
        size_code = get_size_code( args['size']),
        color_code = get_color_code( args['color']),
        quality_code = get_quality_code( args['quality'])
        )
    try:
        u = models.Items(**new_item)
        db.session.add(u)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError, e:
        return make_response(jsonify({'error': 'item code already exists.'}), 400)

    return make_response(jsonify({'success': True}))


@app.route('/api/v1.0/variant', methods=['POST'])
def create_item_variant():
    """Create item variant with unique code"""
    if not request.json:
        abort(400)
    parser = reqparse.RequestParser()
    parser.add_argument('item_code', type=int, required=True, location='json', help="Item code missing")
    parser.add_argument('cost_price', type=float, required=True, location='json', help="Cost Price missing")
    parser.add_argument('selling_price', type=float, required=True, location='json', help="Selling Price missing")
    parser.add_argument('quantity', type=int, required=True, location='json', help="Quantity missing")
    parser.add_argument('username', type=str, required=True, location='json', help="Username missing")
    args = parser.parse_args()
    user_code = get_user_code(args['username'])
    if user_code is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)
    new_variant = dict(
        cost_price = args['cost_price'],
        selling_price = args['selling_price'],
        quantity = args['quantity']
        )
    try:
        u = models.Items.query.filter_by(item_code=args['item_code']).first()
        if u is None:
            return make_response(jsonify({'error': 'Item does not exists'}), 400)
        v = models.Variants(**new_variant)
        u.variants = v
        db.session.add(u)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError, e:
        return make_response(jsonify({'error': 'Item code already exists.'}), 400)
    return make_response(jsonify({'success': True}))



@app.route('/api/v1.0/item/<int:item_code>', methods=['PUT'])
def update_item(item_code):
    """Update item properties"""
    if not request.json:
        abort(400)
    parser = reqparse.RequestParser()
    parser.add_argument('item_name', type=str, required=False, location='json')
    parser.add_argument('size', type=str, required=False, location='json')
    parser.add_argument('color', type=str, required=False, location='json')
    parser.add_argument('quality', type=str, required=False, location='json')
    parser.add_argument('username', type=str, required=True, location='json', help="Username missing")
    args = parser.parse_args()
    user_code = get_user_code(args['username'])
    if user_code is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)
    updated_item = dict(
        item_name = args['item_name'] if 'item_name' in args.keys() and args['item_name'] != None else None,
        size = get_size_code( args['size']) if 'size' in args.keys() and args['size'] != None else None,
        color = get_color_code( args['color']) if 'color' in args.keys() and args['color'] != None else None,
        quality = get_quality_code (args['quality']) if 'quality' in args.keys() and args['quality'] != None else None,
        )
    updated_item_new = {k: v for k, v in updated_item.items() if v}
    updated_item = updated_item_new
    if updated_item == {}:
        return make_response(jsonify({'error': 'Invalid entries'}), 400)
    u = models.Items.query.filter_by(item_code=item_code).first()
    if u is None:
        return invalid_requeset(message='Item code does not exists')
    for param in updated_item:
        setattr(u, param, updated_item[param]) 
    db.session.commit()
    return make_response(jsonify({'success': True}))


@app.route('/api/v1.0/variant/<int:item_code>', methods=['PUT'])
def update_variant(item_code):
    """Update item variant options"""
    if not request.json:
        abort(400)
    parser = reqparse.RequestParser()
    parser.add_argument('cost_price', type=float, required=False, location='json')
    parser.add_argument('selling_price', type=float, required=False, location='json')
    parser.add_argument('quantity', type=int, required=False, location='json')
    parser.add_argument('username', type=str, required=True, location='json', help="Username missing")
    args = parser.parse_args()
    user_code = get_user_code(args['username'])
    if user_code is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)
    updated_variant = dict(
        cost_price = args['cost_price'] if 'cost_price' in args.keys() and args['cost_price'] != None else None,
        selling_price = args['selling_price'] if 'selling_price' in args.keys() and args['selling_price'] != None  else None,
        quantity = args['quantity'] if 'quantity' in args.keys() and args['quantity'] != None  else None
        )
    updated_variant_new = {k: v for k, v in updated_variant.items() if v}
    updated_variant = updated_variant_new
    if updated_variant == {}:
        return make_response(jsonify({'error': 'Invalid entries'}), 400)
    u = models.Items.query.filter_by(item_code=item_code).first()
    if u is None:
        return make_response(jsonify({'error': 'Item does not exists'}), 400)
    v = u.variants
    if v is None:
        return invalid_requeset(message='Variant does not exists')
    for param in updated_variant:
        setattr(u.variants, param, updated_variant[param]) 
    db.session.commit()
    return make_response(jsonify({'success': True}))




@app.route('/api/v1.0/item/<int:item_code>', methods=['DELETE'])
def delete_item(item_code):
    """Delete item"""
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, location='json', help="Username missing")
    args = parser.parse_args()
    user_code = get_user_code(args['username'])
    if user_code is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)
    u=models.Items.query.filter_by(item_code=item_code).first()
    db.session.delete(u)
    db.session.commit()
    return make_response(jsonify({'success': True}))



if __name__ == '__main__':
    app.run(debug=True)
