import json

PYTHON_PROFILE_PATH = "data/output/vessel_profile.json"
LLM_PROFILE_PATH = "data/output/llm_vessel_profile.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


python_profile = load_json(PYTHON_PROFILE_PATH)
llm_profile = load_json(LLM_PROFILE_PATH)

print("\n=== PROFILE COMPARISON ===\n")

for field in python_profile:
    python_value = python_profile.get(field)
    llm_value = llm_profile.get(field)

    if python_value == llm_value:
        status = "SAME"
    elif python_value is None and llm_value is not None:
        status = "LLM FOUND"
    elif python_value is not None and llm_value is None:
        status = "PYTHON FOUND"
    else:
        status = "DIFFERENT"

    print(f"{field}")
    print(f"  Python : {python_value}")
    print(f"  LLM    : {llm_value}")
    print(f"  Status : {status}")
    print()