class Policyholder:
    def __init__(self, id, name, age, policy_type, sum_insured):
        self.id = id
        self.name = name
        self.age = age
        self.policy_type = policy_type
        self.sum_insured = sum_insured
        self.claims = []

class Claim:
    def __init__(self, claim_id, policyholder_id, amount, reason, status, date):
        self.claim_id = claim_id
        self.policyholder_id = policyholder_id
        self.amount = amount
        self.reason = reason
        self.status = status
        self.date = date
