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

def extract_memo(transcript_text, account_id):
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
    
    Transcript: {transcript_text}"""

    extracted_data = query_ollama(prompt)
    
    if not extracted_data:
        sys.exit("Data extraction failed.")

    extracted_data["account_id"] = account_id
    extracted_data["notes"] = "v1 generated from demo call via LLM."
    return extracted_data

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

def generate_agent_spec(memo):
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
        "agent_name": f"{memo.get('company_name', 'Unknown')} Clara Assistant (v1)",
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
            "version": "v1"
        }
    }
    
    return spec

def main():
    filepath = sys.argv[1]
    filename = os.path.basename(filepath)
    account_id = filename.split('_demo')[0]
    
    with open(filepath, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    memo = extract_memo(transcript, account_id)
    memo = populate_unknowns(memo)
    agent_spec = generate_agent_spec(memo)
    
    output_dir = f"/data/outputs/accounts/{account_id}/v1"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "memo.json"), "w") as f:
        json.dump(memo, f, indent=4)
        
    with open(os.path.join(output_dir, "agent_spec.json"), "w") as f:
        json.dump(agent_spec, f, indent=4)
        
    print(json.dumps({"account_id": account_id, "status": "v1_complete", "memo": memo, "agent_spec": agent_spec}))

if __name__ == "__main__":
    main()