import os
import json
import requests # Potentially needed for your LLM SDK

# Placeholder for your company's LLM client
# llm_client = LLMClient(api_key=os.environ.get("YOUR_COMPANY_LLM_API_KEY"))

def handler(request, response):
    if request.method != 'POST':
        response.status_code = 405
        return {'status': 'error', 'message': 'Only POST requests are allowed'}

    try:
        data = request.json()
        clause_text = data.get('clause_text')

        if not clause_text:
            response.status_code = 400
            return {'status': 'error', 'message': '`clause_text` is required'}

        # --- THIS IS WHERE YOU INTEGRATE WITH YOUR COMPANY'S LLM API ---
        # Construct the prompt for entity extraction
        prompt = f"""
        From the following legal text, extract the following entities:
        - Dates
        - Party Names (e.g., "Company A", "Supplier Inc.")
        - Durations (e.g., "five (5) years", "90 days")
        Return ONLY a JSON object with a list of `extracted_entities`.
        If an entity type is not found, its list can be empty.

        Legal Text:
        ---
        {clause_text[:4000]}
        ---

        Expected JSON Output Format:
        {{
          "extracted_entities": [
            {{"type": "date", "value": "..."}},
            {{"type": "party_name", "value": "..."}},
            {{"type": "duration", "value": "..."}}
          ]
        }}
        """

        # Replace with your actual LLM API call
        # llm_api_response = llm_client.chat.completions.create(
        #     model="your_company_llm_model_for_entity_extraction",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.0 # Very low temperature for factual extraction
        # )
        # llm_output = llm_api_response.choices[0].message.content

        # --- MOCK LLM RESPONSE FOR INITIAL TESTING ---
        mock_llm_output = json.dumps({
            "extracted_entities": [
                {"type": "duration", "value": "five (5) years"},
                {"type": "date", "value": "Effective Date"},
                {"type": "party_name", "value": "Company A"},
                {"type": "party_name", "value": "Company B"}
            ]
        })
        llm_output = mock_llm_output
        # --- END MOCK LLM RESPONSE ---

        try:
            parsed_llm_output = json.loads(llm_output)
            extracted_entities = parsed_llm_output.get("extracted_entities", [])

            response.status_code = 200
            return {
                'status': 'success',
                'extracted_entities': extracted_entities
            }
        except json.JSONDecodeError:
            response.status_code = 500
            return {'status': 'error', 'message': f"LLM returned invalid JSON: {llm_output[:200]}"}

    except json.JSONDecodeError:
        response.status_code = 400
        return {'status': 'error', 'message': 'Invalid JSON in request body'}
    except Exception as e:
        response.status_code = 500
        return {'status': 'error', 'message': f"An unexpected error occurred: {e}"}