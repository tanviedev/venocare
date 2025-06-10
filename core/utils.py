# core/utils.py

def get_default_plan_for_stage(stage):
   plans = {
    "cvi1": "Daily walking, avoid prolonged standing, hydrate well.",
    "cvi2": "Compression socks, leg elevation above heart level, avoid salty food, engage in mild calf exercises.",
    "cvi3": "Low-sodium diet, daily leg massage, wear medical stockings, increase antioxidant-rich foods.",
    "cvi4": "Doctor consultation, monitor wounds, use prescribed ointments, avoid excessive heat exposure.",
    "cvi5": "Wound care with sterile dressings, advanced venous ulcer management, potential laser or surgical interventions.",
    "cvi6": "Intensive medical intervention, vascular surgery consultation, skin grafting if necessary, strict wound monitoring."
   }
   return plans.get(stage.lower(), "Maintain a healthy lifestyle and consult a doctor.")
