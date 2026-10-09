from flask import jsonify, request

from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import (
    service_ticket_schema,
    service_tickets_schema,
)
from app.extensions import cache, db
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket


@service_tickets_bp.post("/")
def create_service_ticket():
    payload = request.get_json() or {}
    required_fields = ["customer_id", "vin", "issue_description"]
    missing = [field for field in required_fields if field not in payload]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    customer = db.session.get(Customer, payload["customer_id"])
    if customer is None:
        return jsonify({"error": "customer_id does not exist"}), 404

    ticket = ServiceTicket(
        customer_id=payload["customer_id"],
        vin=payload["vin"],
        issue_description=payload["issue_description"],
        status=payload.get("status", "open"),
    )

    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201


@service_tickets_bp.put("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>")
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.put("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic was not assigned to this ticket"}), 404

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.put("/<int:ticket_id>/edit")
def edit_service_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    payload = request.get_json() or {}

    add_ids = payload.get("add_ids", [])
    remove_ids = payload.get("remove_ids", [])

    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.post("/<int:ticket_id>/parts")
def add_inventory_part_to_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    payload = request.get_json() or {}

    inventory_id = payload.get("inventory_id")
    if inventory_id is None:
        return jsonify({"error": "inventory_id is required"}), 400

    inventory_item = Inventory.query.get_or_404(inventory_id)
    if inventory_item not in ticket.inventory_items:
        ticket.inventory_items.append(inventory_item)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.get("/")
@cache.cached(timeout=60)
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200
