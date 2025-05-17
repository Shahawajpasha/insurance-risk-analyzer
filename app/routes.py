from flask import Blueprint, request, jsonify
from app.models import Policyholder, Claim
from app.storage import policyholders, claims

app_routes = Blueprint('app_routes', __name__)

@app_routes.route("/add-policyholder", methods=["POST"])
def add_policyholder():
    data = request.json
    pid = len(policyholders) + 1
    policyholder = Policyholder(pid, data["name"], data["age"], data["policy_type"], data["sum_insured"])
    policyholders[pid] = policyholder
    return jsonify({"message": "Policyholder added", "id": pid})
from datetime import datetime

@app_routes.route("/add-claim", methods=["POST"])
def add_claim():
    data = request.json
    claim_id = data["claim_id"]
    policyholder_id = data["policyholder_id"]

    # Check if policyholder exists
    if policyholder_id not in policyholders:
        return jsonify({"error": "Policyholder not found"}), 404

    # Validate the date format
    try:
        claim_date = datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Create the claim
    claim = Claim(
        claim_id=claim_id,
        policyholder_id=policyholder_id,
        amount=data["amount"],
        reason=data["reason"],
        status=data["status"],
        date=claim_date
    )

    # Save claim
    claims[claim_id] = claim
    policyholders[policyholder_id].claims.append(claim)

    return jsonify({"message": "Claim added", "claim_id": claim_id})
from datetime import datetime, timedelta

@app_routes.route("/high-risk", methods=["GET"])
def high_risk_policyholders():
    high_risk_list = []
    one_year_ago = datetime.now() - timedelta(days=365)

    for pid, policyholder in policyholders.items():
        claim_count = 0
        total_claim_amount = 0

        for claim in policyholder.claims:
            if claim.date >= one_year_ago:
                claim_count += 1
                total_claim_amount += claim.amount

        claim_ratio = total_claim_amount / policyholder.sum_insured if policyholder.sum_insured else 0

        if claim_count > 3 or claim_ratio > 0.8:
            high_risk_list.append({
                "id": pid,
                "name": policyholder.name,
                "claim_count": claim_count,
                "total_claimed": total_claim_amount,
                "claim_ratio": round(claim_ratio, 2)
            })

    return jsonify({"high_risk_policyholders": high_risk_list})
from collections import defaultdict

@app_routes.route("/reports", methods=["GET"])
def generate_reports():
    monthly_claims = defaultdict(int)
    policy_type_totals = defaultdict(list)
    highest_claim = None
    pending_policyholders = set()

    for claim in claims.values():
        # --- Total claims per month ---
        month = claim.date.strftime("%Y-%m")
        monthly_claims[month] += 1

        # --- Highest claim ---
        if highest_claim is None or claim.amount > highest_claim.amount:
            highest_claim = claim

        # --- Average by policy type ---
        policyholder = policyholders.get(claim.policyholder_id)
        if policyholder:
            policy_type_totals[policyholder.policy_type].append(claim.amount)

        # --- Pending claims ---
        if claim.status.lower() == "pending" and policyholder:
            pending_policyholders.add(policyholder.name)

    # Calculate averages
    avg_by_type = {
        policy_type: round(sum(amounts)/len(amounts), 2)
        for policy_type, amounts in policy_type_totals.items()
    }

    # Format the report
    report = {
        "total_claims_per_month": dict(monthly_claims),
        "average_claim_by_policy_type": avg_by_type,
        "highest_claim": {
            "claim_id": highest_claim.claim_id,
            "amount": highest_claim.amount,
            "reason": highest_claim.reason,
            "policyholder_id": highest_claim.policyholder_id
        } if highest_claim else {},
        "pending_claim_policyholders": list(pending_policyholders)
    }

    return jsonify(report)
