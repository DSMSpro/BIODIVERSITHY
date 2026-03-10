# RL Action Space
ACTIONS = [
    "Normal Monitoring",
    "Increase Habitat Protection",
    "Deploy Anti-Poaching Patrols",
    "Urgent Conservation Intervention"
]

# Q-values learned (demo RL policy)
Q_TABLE = {
    "LOW":    [10, 2, 0, 0],
    "MEDIUM": [3, 8, 5, 2],
    "HIGH":   [0, 4, 8, 12]
}


def rl_recommendation(risk_level: str):
    """
    RL Agent chooses best conservation action
    based on maximum Q-value.
    """
    q_values = Q_TABLE[risk_level]
    best_index = q_values.index(max(q_values))
    return ACTIONS[best_index]
# Simple RL Agent for Biodiversity Action Recommendation

def get_action(risk_level: str):

    risk_level = str(risk_level).upper()

    if risk_level == "HIGH":
        return "Immediate Conservation Action Required"

    elif risk_level == "MEDIUM":
        return "Habitat Monitoring and Protection"

    else:
        return "Normal Monitoring"