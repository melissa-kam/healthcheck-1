from flask import jsonify, request, render_template
from .. import db
from ..models import Canary, Results
from . import api
from .errors import bad_request
from app.worker.tasks import process_trend
import pygal


@api.route('/projects/<int:project_id>/canary/<int:canary_id>/trend', methods=['GET'])
def get_trend(project_id, canary_id):
    interval = request.args.get('interval')
    resolution = request.args.get('resolution')
    threshold = request.args.get('threshold')
    analysis_call = process_trend.delay(project_id=project_id, canary_id=canary_id, interval=interval,
                                        resolution=resolution,
                                        threshold=threshold)
    # results_list, values = analysis_call.wait()
    # line = pygal.Line()
    # line.title = "my awesome graph"
    # line.x_labels = values
    # line.add("status", [1 if x == "green"  else 0 for x in results_list])
    # return line.render()
    return jsonify(msg="trending done")


@api.route('/projects/<int:project_id>/canary', methods=['POST'])
def new_canary(project_id):
    post_request = request.get_json()
    post_request['project_id'] = project_id
    new_canary = Canary(**post_request)
    db.session.add(new_canary)
    db.session.commit()
    post_response = jsonify(**new_canary.canary_to_json())
    post_response.status_code = 201
    return post_response


@api.route('/projects/<int:project_id>/canary', methods=['GET'])
def get_canaries(project_id):
    all_canaries = Canary.query.filter_by(project_id=project_id).filter_by(status="ACTIVE")
    canary_list = []
    for obj in all_canaries:
        canary_list.append(obj.canary_to_json())
    get_response = jsonify(canaries=canary_list)
    get_response.status_code = 200
    return get_response


@api.route('/projects/<int:project_id>/canary/<int:canary_id>', methods=['GET'])
def get_canary(project_id, canary_id):
    canary = Canary.query.get(canary_id)
    if canary is None or canary.project_id != project_id:
        return bad_request('canary not found')
    get_response = jsonify(**canary.canary_to_json())
    get_response.status_code = 200
    return get_response


@api.route('/projects/<int:project_id>/canary/<int:canary_id>', methods=['PUT'])
def edit_canary(project_id, canary_id):
    canary = Canary.query.get(canary_id)
    if canary is None or canary.project_id != project_id:
        return bad_request('canary not found')
    data = request.get_json()
    canary.name = data.get('name') or canary.name
    canary.description = data.get('description') or canary.description
    canary.meta_data = data.get('meta_data') or canary.meta_data
    canary.criteria = data.get('criteria') or canary.criteria
    canary.health = data.get('health') or canary.health
    db.session.commit()
    put_response = jsonify(**canary.canary_to_json())
    put_response.status_code = 200
    return put_response


@api.route('/projects/<int:project_id>/canary/<int:canary_id>', methods=['DELETE'])
def delete_canary(canary_id, project_id):
    canary = Canary.query.get(canary_id)
    if canary is None or canary.project_id != project_id:
        return bad_request('canary not found')
    name = canary.name
    if canary.status == "DISABLED":
        db.session.delete(canary)
        canary_results = Results.query.filter_by(canary_id=canary_id).all()
        for result in canary_results:
            db.session.delete(result)
        db.session.commit()
        return '', 204
    canary.status = "DISABLED"
    db.session.commit()
    response = jsonify("Disabled '%s' " % name)
    response.status_code = 200
    return response
