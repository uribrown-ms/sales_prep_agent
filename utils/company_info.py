# utils/company_info.py

import re

def get_company_name(linkedin_url):
    """
    Extracts the company name from a LinkedIn URL.
    """
    pattern = r'linkedin\.com/company/([^/]+)/?'
    match = re.search(pattern, linkedin_url)
    if match:
        # Decode URL-encoded characters
        company_name = match.group(1).replace('-', ' ').title()
        return company_name
    else:
        return None
