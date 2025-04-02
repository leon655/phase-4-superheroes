from flask import Blueprint, jsonify, request
from models import db, Hero, Power, HeroPower

api_bp = Blueprint('api', __name__)


@api_bp.route('/', methods=['GET'])
def welcome():
    return jsonify({"message": "Welcome to the Heroes API!"})


@api_bp.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{"id": h.id, "name": h.name, "super_name": h.super_name} for h in heroes])


@api_bp.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    
    hero_data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [
            {
                "id": hp.id,
                "hero_id": hp.hero_id,
                "power_id": hp.power_id,
                "strength": hp.strength,
                "power": {"id": hp.power.id, "name": hp.power.name, "description": hp.power.description}
            } for hp in hero.hero_powers
        ]
    }
    return jsonify(hero_data)


@api_bp.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description} for p in powers])


@api_bp.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify({"id": power.id, "name": power.name, "description": power.description})


@api_bp.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    description = data.get('description', '').strip()

    if len(description) < 20:
        return jsonify({"errors": ["Description must be at least 20 characters."]}), 400

    power.description = description
    db.session.commit()
    return jsonify({"id": power.id, "name": power.name, "description": power.description})


@api_bp.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    hero_id, power_id, strength = data.get('hero_id'), data.get('power_id'), data.get('strength')

    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({"errors": ["Invalid strength value"]}), 400

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({"errors": ["Hero or Power not found"]}), 404

    hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify({
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {"id": hero.id, "name": hero.name, "super_name": hero.super_name},
        "power": {"id": power.id, "name": power.name, "description": power.description}
    }), 201
