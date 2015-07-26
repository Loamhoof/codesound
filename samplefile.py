"""
Provide generated routes to expose defined models
"""
from inspect import isclass
from operator import attrgetter

from flask import Blueprint, jsonify
from sqlalchemy import inspect

import model as model_module
from model.abc import db
from resource.parse_params import Argument, parse_params


def make_route(exposed_model):
    """ Return a route exposing `exposed_model` """
    @parse_params(*map(Argument, inspect(exposed_model).columns.keys()))
    def route(**columns):
        """ Return filtered models of type `exposed_model` """
        filtered_models = exposed_model.query.filter_by(**{
            column_name: column_value
            for column_name, column_value in columns.items() if column_value is not None
        })
        return jsonify(rows=list(map(attrgetter('json'), filtered_models)))
    route.__name__ = exposed_model.__tablename__
    return route


MODEL_BLUEPRINT = Blueprint('model', __name__)


models = []
for model in filter(lambda var: isclass(var) and issubclass(var, db.Model), vars(model_module).values()):
    MODEL_BLUEPRINT.route('/model/%s' % model.__tablename__)(make_route(model))
    models.append(model.__tablename__)
MODEL_BLUEPRINT.route('/model')(lambda: jsonify(models=models))
