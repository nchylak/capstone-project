import json
import re
from bs4 import BeautifulSoup
import requests

print('Running script...')

f = open("/project/0_cleaning/output_cleaning/ecom_wapps_per_domain.json","r")
domain_wapps = json.load(f)
f.close()

# Patterns in URL of "mentions légales" or "conditions générales de vente" pages
patterns = {
    'PrestaShop': ['/content/2-mentions-legales',
                   '/content/3-conditions-generales-de-vente'],
    'Magento': [], # standard - moved to all
    'WooCommerce': [], # mostly bigger brands
    'OpenCart': [], # no pattern, most websites already closed or very fishy - check again later
    'eZPublish': [], # mostly public inst (towns, museums, etc.)
    'osCommerce': [], # no pattern
    'SalesforceCommerceCloud': ['/mentions-legales/legalnotice.html',
                                '/mentions-legales/legal-notice.html',
                                '/site/mentions-legales',
                                '/site/legal'], # big brands
    'EPages': [],
    'IBMWebSphereCommerce': [], # blogs
    'Shopify': ['/pages/mentions-legales',
                '/pages/conditions-generales-de-vente'],
    'All': ['/mentions-legales/',
            '/conditions-generales-de-vente/',
            '/cgv/']}

# Get web page
def get_ml_page(domain, pattern):
    url = 'http://' + domain + pattern
    try:
        response = requests.get(url, timeout=15)
        parsed_html = BeautifulSoup(response.content, "html.parser")
        content = parsed_html.get_text(separator=' ').replace('\n', ' ').replace('\xa0', ' ').replace('\t', ' ')
    except:
        content = ''
    return url, content

# Search page for candiate sirens
def extract_candidate_siren(string_page):    
    regex = re.compile("[ :]{1}[03-9]{1}\d{2}[-. ]?\d{3}[-. ]?\d{3}[ .,;<]{1}") # ? zero or one, {3} exactly 3
    siren = re.findall(regex, string_page)
    exclude = ['000000000'] # explicitely exclude hosting companies
    
    siren_clean = []
    for x in siren:
        x = x.strip(' :.,;<') # strip beginning and ending punctuation so that not counted
        if (x.count('.') == 1) | (x.count('-') == 1): # after stripping, points and dashes should either come in pair or be absent altogether
            pass
        else:
            x_keep = x.replace(' ','').replace('-','').replace('.','')
            if x_keep not in exclude: 
                siren_clean.append(x_keep)

    return siren_clean

# Search page for candiate sirets
def extract_candidate_siret(string_page):
    regex = re.compile("[ :]{1}[03-9]{1}\d{2}[-. ]?\d{3}[-. ]?\d{3}[-. ]?[0]{3}[1-9]{1}\d{1}")
    siret = re.findall(regex, string_page)
    exclude = ['00000000000000']
    
    siret_clean = []
    for x in siret:
        x = x.replace(' ','').replace('-','').replace('.','').strip(' :')
        if x not in exclude:
            siret_clean.append(x)
    
    return siret_clean

# Validate structure of sirens resp. sirets
def validate_siren_siret(potential_id):
    check_sum = 0
    
    # Compute check sum
    for i, ciph in enumerate(reversed(potential_id)): # reverse as even and odd should be assessed from the right as per doc
        if i%2 == 0: # odd rank (even in python as starts from 0)
            to_add = int(ciph)
            check_sum += to_add
        else:
            to_add_temp = str(int(ciph)*2)
            to_add = 0
            for c in to_add_temp:
                to_add += int(c)
            check_sum += to_add
    
    # validate that check_sum is a multiple of 10
    if check_sum%10 == 0:
        return True
    else:
        return False

# Summary function encompassing all above (for multiprocessing purposes)
def find_siret_siren(domain, pattern):
    siren_in_warc = []
    siret_in_warc = []
    
    # Get ML page
    url, content_text = get_ml_page(domain, pattern)

    # Get SIREN
    candidate_siren = extract_candidate_siren(content_text)
    for candidate in candidate_siren:
        check = validate_siren_siret(candidate)
        if check:
            siren_in_warc.append(candidate)

    # Get SIRET
    candidate_siret = extract_candidate_siret(content_text)
    for candidate in candidate_siret:
        check = validate_siren_siret(candidate)
        if check:
            siret_in_warc.append(candidate)
            
    return siren_in_warc, siret_in_warc, url, content_text

# Clean output of multiprocessed search
def handle_results(siren_in_warc, siret_in_warc):
    
    # siren:
    if len(siren_in_warc)>0:
        siren_final = list(dict.fromkeys(siren_in_warc))
    else: 
        siren_final = []

    # siret:
    if len(siret_in_warc)>0:
        siret_final = list(dict.fromkeys(siret_in_warc))
    else: 
        siret_final = []
    
    return siren_final, siret_final

# Function to save output as JSON
def json_save(obj, name):
    json_content = json.dumps(obj)
    f = open(f"/project/0_cleaning/output_cleaning/{name}.json","w")
    f.write(json_content)
    f.close()   

############################################################
############# EXTRACT AND SAVE #############################

siren_per_domain = {}
siret_per_domain = {}
content_sir = []

for i, (domain, wapps) in enumerate(domain_wapps.items()):
    print(f'{i} domains processed.')
    
    sirens_raw_1 = []
    sirets_raw_1 = []
    for wapp in wapps:
        if wapp in patterns:
            patterns_wapp = patterns[wapp]
            for pattern in patterns_wapp:
                sirens_raw_iter, sirets_raw_iter, url, content_text = find_siret_siren(domain, pattern)
                sirens_raw_1 += sirens_raw_iter
                sirets_raw_1 += sirets_raw_iter
                if (len(sirens_raw_iter)>0) | (len(sirets_raw_iter)>0):
                    content_sir.append({
                        'url': url,
                        'siren': sirens_raw_iter,
                        'siret': sirets_raw_iter,
                        'content_url': content_text})
    
    sirens_raw_2 = []
    sirets_raw_2 = []    
    for pattern in patterns['All']:
        sirens_raw_iter, sirets_raw_iter, url, content_text = find_siret_siren(domain, pattern)
        sirens_raw_2 += sirens_raw_iter
        sirets_raw_2 += sirets_raw_iter
        if (len(sirens_raw_iter)>0) | (len(sirets_raw_iter)>0):
            content_sir.append({
                'url': url,
                'siren': sirens_raw_iter,
                'siret': sirets_raw_iter,
                'content_url': content_text})
        
    sirens_raw = sirens_raw_1 + sirens_raw_2
    sirets_raw = sirets_raw_1 + sirets_raw_2
    sirens, sirets = handle_results(sirens_raw, sirets_raw)
    
    siren_per_domain[domain] = sirens
    siret_per_domain[domain] = sirets
    

json_save(siren_per_domain,'sirens_in_web')
json_save(siret_per_domain,'sirets_in_web')
json_save(content_sir,'web_pages_where_sir')