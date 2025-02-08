import requests


def get_domain_info(domain):
    url = f'https://networkcalc.com/api/dns/lookup/{domain}'
    response = requests.get(url)
    if response.status_code == 200:
        decoded_response = response.json()
        records = decoded_response.get('records', {})
        record_info_list = []
        for record_type, record_entries in records.items():
            if record_type == 'TXT':
                continue
            for entry in record_entries:
                if isinstance(entry, dict):
                    entry_info = ', '.join([f"{key}: {value}" for key, value in entry.items() if key not in ['priority', 'ttl']])
                    record_info_list.append(f"{record_type}: {entry_info}")
                else:
                    record_info_list.append(f"{record_type}: {entry}")
        record_info = '; '.join(record_info_list)
        return record_info if record_info else "No records found"
    else:
        return "Error fetching data"

def get_abuse_info(ip_address, api_key):
    url = 'https://api.abuseipdb.com/api/v2/check'
    querystring = {
        'ipAddress': ip_address,
        'maxAgeInDays': '90'
    }
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        decoded_response = response.json()
        abuse_confidence_score = decoded_response.get('data', {}).get('abuseConfidenceScore', 'N/A')
        country = decoded_response.get('data', {}).get('countryCode', 'N/A')
        isp = decoded_response.get('data', {}).get('isp', 'N/A')
        usage_type = decoded_response.get('data', {}).get('usageType', 'N/A')
        domain = decoded_response.get('data', {}).get('domain', 'N/A')
        isTor = decoded_response.get('data', {}).get('isTor', 'N/A')
        return f"Abuse Confidence Score: {abuse_confidence_score}, Country: {country}, ISP: {isp}, Usage Type: {usage_type}, Domain: {domain}, Is Tor Entry/Exit Node: {isTor}"
    else:
        return "Error fetching data"

def get_hash_info(hash_value, api_key):
    url = f"https://www.virustotal.com/api/v3/files/{hash_value}"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        decoded_response = response.json()
        data = decoded_response.get('data', {})
        attributes = data.get('attributes', {})
        relevant_fields = {
            "meaningful_name": attributes.get("meaningful_name", "N/A"),
            "popular_threat_classification": attributes.get("popular_threat_classification", {}).get("suggested_threat_label", "N/A"),
            "suggested_threat_label": attributes.get("suggested_threat_label", "N/A"),
            "reputation": attributes.get("reputation", "N/A"),
            "sandbox_verdicts": attributes.get("sandbox_verdicts", "N/A"),
            "total_votes": attributes.get("total_votes", "N/A")
        }
        hash_info = (
            f"\nURL: https://www.virustotal.com/gui/file/{hash_value}\n"
            f"Meaningful Name: {relevant_fields['meaningful_name']}\n"
            f"Popular Threat Classification: {relevant_fields['popular_threat_classification']}\n"
            f"Suggested Threat Label: {relevant_fields['suggested_threat_label']}\n"
            f"Reputation: {relevant_fields['reputation']}\n"
            f"Sandbox Verdicts: {relevant_fields['sandbox_verdicts']}\n"
            f"Total Votes: {relevant_fields['total_votes']}\n"
        )
        return hash_info if hash_info else "No information found"
    else:
        return f"Error fetching data: {response.status_code} - {response.reason}"