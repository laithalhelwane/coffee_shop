import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    try:
        '''
        retrive all the drinks in the database
        '''
        drinks = Drink.query.all()
        '''
        prepare the list of drink in drink.short() data representation
        '''
        drinks_formated = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_formated
        })
    except Exception:
        abort(422)  # unprocessable


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detailed(token):
    try:
        '''
        retrive all the drinks in the database
        '''
        drinks = Drink.query.all()
        '''
        prepare the list of drink in drink.short() data representation
        '''
        drinks_formated = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_formated
        })
    except Exception:
        abort(422)  # unprocessable


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    body = request.get_json()
    try:
        '''
        Check if title and recipe are included in request
        '''
        if (body.get('title') is None or body.get('recipe') is None):
            abort(400)
        '''
        Create a new drink
        '''
        new_drink = Drink(title=body['title'],
                          recipe=json.dumps(body['recipe']))
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        }
        )
    except Exception:
        abort(422)  # unprocessable


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(token, id=id):
    '''
    Check if the drink is exist
    '''
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)  # Not found
    try:
        body = request.get_json()
        if body.get('title') is not None:
            drink.title = body['title']
        if body.get('recipe') is not None:
            drink.recipe = json.dumps(body['recipe'])
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)  # unprocessable


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id=id):
    '''
    Check if the drink is exist
    '''
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)  # Not found
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception:
        abort(422)  # unprocessable


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'not found',
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Bad request',
    }), 401


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': error.error['description'],
    }), 401
