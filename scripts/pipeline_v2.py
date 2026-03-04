import json
import os
import sys
import urllib.request
import urllib.error

def query_ollama(prompt):
    url = "http://ollama:11434/api/generate"
    data = {
        "model": "llama3.2",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            return json.loads(result["response"])
    except Exception as e:
        print(json.dumps({"error": f"Ollama API Error or Timeout: {str(e)}"}))
        return None

def extract_onboarding_data(onboarding_text, account_id):
    prompt = f"""Extract operational rules from the transcript into this exact JSON schema:
    {{
        "company_name": "string",
        "business_hours": {{"days": "string", "start": "string", "end": "string", "timezone": "string"}},
        "office_address": "string",
        "services_supported": ["string"],
        "emergency_definition": ["string"],
        "emergency_routing_rules": "string",
        "non_emergency_routing_rules": "string",
        "call_transfer_rules": {{"timeouts": "string", "retries": "string", "fallback_message": "string"}},
        "integration_constraints": ["string"],
        "after_hours_flow_summary": "string",
        "office_hours_flow_summary": "string"
    }}
    If a field is not explicitly mentioned, use "Unknown" or an empty list. Do not invent details.
    
    Transcript: {onboarding_text}"""

    extracted_data = query_ollama(prompt)
    
    if not extracted_data:
        sys.exit(1)
        
    extracted_data["account_id"] = account_id
    return extracted_data

def merge_memos(v1_memo, new_data):
    merged = json.loads(json.dumps(v1_memo))
    
    for key, new_val in new_data.items():
        if key == "account_id":
            continue
            
        old_val = merged.get(key)
        
        if isinstance(new_val, list):
            if not isinstance(old_val, list):
                merged[key] = []
            for item in new_val:
                if item and str(item).strip().lower() != "unknown" and item not in merged[key]:
                    merged[key].append(item)
                    
        elif isinstance(new_val, dict):
            if not isinstance(old_val, dict):
                merged[key] = {}
            for sub_key, sub_val in new_val.items():
                if sub_val and str(sub_val).strip().lower() != "unknown" and str(sub_val).strip() != "":
                    merged[key][sub_key] = sub_val
                    
        else:
            if new_val and str(new_val).strip().lower() != "unknown" and str(new_val).strip() != "":
                merged[key] = new_val
                
    merged["notes"] = "v2 updated after onboarding call via LLM extraction and Python merge."
    return merged

def populate_unknowns(memo):
    unknowns = []
    
    for key, value in memo.items():
        if key in ["account_id", "notes", "questions_or_unknowns"]:
            continue
            
        if isinstance(value, str) and (value.strip().lower() == "unknown" or value.strip() == ""):
            unknowns.append(f"Missing {key}")
            
        elif isinstance(value, list) and len(value) == 0:
            unknowns.append(f"Missing {key}")
            
        elif isinstance(value, dict):
            missing_nested = [k for k, v in value.items() if isinstance(v, str) and (v.strip().lower() == "unknown" or v.strip() == "")]
            if missing_nested:
                unknowns.append(f"Missing details in {key}: {', '.join(missing_nested)}")
                
    memo["questions_or_unknowns"] = unknowns
    return memo

def generate_v2_spec(memo):
    bh = memo.get("business_hours", {})
    hours_str = f"{bh.get('days', 'Unknown')} from {bh.get('start', 'Unknown')} to {bh.get('end', 'Unknown')} {bh.get('timezone', '').strip()}"
    
    routing_rule = memo.get("emergency_routing_rules", "Unknown")
    non_emergency_rule = memo.get("non_emergency_routing_rules", "Unknown")
    
    services = ", ".join(memo.get("services_supported", [])) or "None specified"
    emergencies = ", ".join(memo.get("emergency_definition", [])) or "None specified"
    constraints = ", ".join(memo.get("integration_constraints", [])) or "None specified"
    
    office_flow = memo.get("office_hours_flow_summary", "Standard routing.")
    after_hours_flow = memo.get("after_hours_flow_summary", "Standard after-hours routing.")

    system_prompt = f"""## Identity
You are Clara, the automated assistant for {memo.get('company_name', 'Unknown')}. You are professional and empathetic.

## Context & Operational Variables
- Business Hours: {hours_str}
- Services Provided: {services}
- Emergency Definitions: {emergencies}
- Emergency Routing Protocol: {routing_rule}
- Non-Emergency Protocol: {non_emergency_rule}
- Software Constraints: {constraints}
- Office Hours Context: {office_flow}
- After Hours Context: {after_hours_flow}

## Task
Follow these workflows strictly based on the time of day:

BUSINESS HOURS FLOW:
1. Greet the caller and ask the purpose of their call.
2. Collect their name and phone number.
3. Determine if their request matches our supported services ({services}).
4. Attempt to route or transfer the call using the transfer_call tool.
5. If transfer fails, apologize, assure follow-up, and ask if they need anything else.
6. Close call using end_call if they need nothing else.

AFTER HOURS FLOW:
1. Greet and ask purpose.
2. Confirm if it is an emergency based on this definition: {emergencies}.
3. If emergency: immediately collect name, number, and address. Use the transfer_call tool to route appropriately.
4. If transfer fails: apologize and assure follow-up.
5. If non-emergency: collect details and confirm follow-up ({non_emergency_rule}).
6. Ask if they need anything else and use end_call to close.

## Style Guardrails
- Do not ask unnecessary questions.
- Do not mention function calls, AI constraints, or system tools to the caller."""

    spec = {
        "agent_name": f"{memo.get('company_name', 'Unknown')} Clara Assistant (v2)",
        "channel": "voice",
        "language": "en-US",
        "voice_id": "retell-Cimo",
        "response_engine": {
            "type": "retell-llm"
        },
        "retellLlmData": {
            "model": "gpt-4o",
            "general_prompt": system_prompt,
            "general_tools": [
                {
                    "type": "transfer_call",
                    "name": "transfer_call",
                    "description": "Transfer the call to a human agent or emergency contact.",
                    "transfer_destination": {
                        "type": "predefined",
                        "number": routing_rule 
                    },
                    "transfer_option": {
                        "type": "cold_transfer"
                    }
                },
                {
                    "type": "end_call",
                    "name": "end_call",
                    "description": "Hang up the call when the conversation is finished or fallback is needed."
                }
            ],
            "start_speaker": "agent"
        },
        "metadata": {
            "timezone": bh.get("timezone", "Unknown"),
            "business_hours_raw": bh,
            "services_supported": memo.get("services_supported", []),
            "emergency_definition": memo.get("emergency_definition", []),
            "emergency_routing_raw": routing_rule,
            "non_emergency_routing_raw": non_emergency_rule,
            "call_transfer_rules": memo.get("call_transfer_rules", {}),
            "integration_constraints": memo.get("integration_constraints", []),
            "version": "v2"
        }
    }
    
    return spec

def generate_changelog(v1_memo, v2_memo, v1_spec, v2_spec, account_id):
    changes = []
    
    for key in v1_memo:
        if json.dumps(v1_memo.get(key), sort_keys=True) != json.dumps(v2_memo.get(key), sort_keys=True):
            changes.append({
                "file": "memo.json",
                "field": key,
                "old_value": v1_memo.get(key),
                "new_value": v2_memo.get(key),
                "reason": "Updated based on operational logic confirmed during onboarding."
            })
            
    for key in v1_spec:
        if json.dumps(v1_spec.get(key), sort_keys=True) != json.dumps(v2_spec.get(key), sort_keys=True):
            changes.append({
                "file": "agent_spec.json",
                "field": key,
                "old_value": v1_spec.get(key),
                "new_value": v2_spec.get(key),
                "reason": "Regenerated to reflect new operational context."
            })
    
    changelog_dir = f"/data/changelog/{account_id}"
    os.makedirs(changelog_dir, exist_ok=True)
    
    with open(os.path.join(changelog_dir, "changes.json"), "w") as f:
        json.dump(changes, f, indent=4)

    with open(os.path.join(changelog_dir, "changes.md"), "w") as f:
        f.write(f"# Changelog for {account_id}\n\n")
        for change in changes:
            f.write(f"- **[{change['file']}] {change['field']}**: `{change['old_value']}` -> `{change['new_value']}`\n")
            f.write(f"  - *Reason*: {change['reason']}\n\n")
    
    return changes

def main():
    filepath = sys.argv[1]
    filename = os.path.basename(filepath)
    account_id = filename.split('_onboarding')[0]
    
    with open(filepath, "r", encoding="utf-8") as f:
        onboarding_text = f.read()
        
    v1_memo_path = f"/data/outputs/accounts/{account_id}/v1/memo.json"
    v1_spec_path = f"/data/outputs/accounts/{account_id}/v1/agent_spec.json"
    
    if not os.path.exists(v1_memo_path) or not os.path.exists(v1_spec_path):
        error_msg = f"Error: v1 files not found for {account_id}. Pipeline A must be run first."
        print(json.dumps({"account_id": account_id, "status": "error", "message": error_msg}))
        sys.exit(error_msg)
        
    with open(v1_memo_path, "r") as f:
        v1_memo = json.load(f)
        
    new_extracted_data = extract_onboarding_data(onboarding_text, account_id)
    v2_memo = merge_memos(v1_memo, new_extracted_data)
    v2_memo = populate_unknowns(v2_memo)
    v2_spec = generate_v2_spec(v2_memo)
    
    v2_dir = f"/data/outputs/accounts/{account_id}/v2"
    os.makedirs(v2_dir, exist_ok=True)

    with open(v1_spec_path, "r") as f:
        v1_spec = json.load(f)
    
    with open(os.path.join(v2_dir, "memo.json"), "w") as f:
        json.dump(v2_memo, f, indent=4)
        
    with open(os.path.join(v2_dir, "agent_spec.json"), "w") as f:
        json.dump(v2_spec, f, indent=4)
        
    changes = generate_changelog(v1_memo, v2_memo, v1_spec, v2_spec, account_id)

    print(json.dumps({"account_id": account_id, "status": "v2_complete", "memo": v2_memo, "agent_spec": v2_spec, "changes": changes}))

if __name__ == "__main__":
    main()