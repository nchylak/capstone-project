import json
import pandas as pd
import numpy as np
from warcio.archiveiterator import ArchiveIterator
import re
from urllib.parse import urlparse

# USEFUL FUNCTIONS

def load_json(path):
    f = open(path, "r")
    json_loaded = json.load(f)
    f.close()
    return json_loaded

def get_warc_content(warc):
    
    file_path = '/mnt/bigdata/s3/'+ warc

    with open(file_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                content_byte = record.content_stream().read()
                
                try:
                    content_decoded = content_byte.decode('utf-8').replace('<',' ').replace('>',' ').replace('"',' ').replace("'",' ').replace(':',' ')
                except:
                    content_decoded = ''
                    
    return url, content_decoded

def get_https(url):
    if urlparse(url).scheme=='https':
        return True
    else:
        False
        
def get_email_domains(content_decoded):
    regex = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    list_emails = re.findall(regex, content_decoded)
    
    list_domain = []
    if len(list_emails)>0:
        for email in list_emails:
            domain_ext = email.split('@')[1]
            domain = domain_ext.split('.')[0]
            list_domain.append(domain)
    
    return list_domain

def get_ts(content_decoded):
    regex = re.compile('trustedshops|trustbadge|tsbadge')
    if re.search(regex, content_decoded):
        return True
    else:
        return False
    
def get_avis_verifies(content_decoded):
    regex = re.compile('avis-verifies\.com')
    if re.search(regex, content_decoded):
        return True
    else:
        return False

def get_sag(content_decoded):
    regex = re.compile('societe-des-avis-garantis|ag.?.?Widget')
    if re.search(regex, content_decoded):
        return True
    else:
        return False
    
# SCRAPE WARCS

siren_warcs = load_json('/project/1_feature_extraction/extract_nb_domains/siren_warcs.json')
features_from_warcs = []

for i, (siren, warcs) in enumerate(siren_warcs.items()):

    flag_https = False
    email_domains = []
    flag_trusted_shop = False
    flag_avis_verifies = False
    flag_sag = False # société des avis garantis
    flag_trust = False

    for warc in warcs[:1000]:
        url, content_decoded = get_warc_content(warc)

        # find HTTPS
        if get_https(url):
            flag_https = True

        # find email domains
        list_email_domains_warc = get_email_domains(content_decoded)
        email_domains += list_email_domains_warc

        # find Trusted Shops
        if get_ts(content_decoded):
            flag_trusted_shop = True

        # find avis verifies
        if get_avis_verifies(content_decoded):
            flag_avis_verifies = True

        # find société des avis garantis
        if get_sag(content_decoded):
            flag_sag = True

    email_domains = list(dict.fromkeys(email_domains))
    flag_trust = any([flag_trusted_shop, flag_avis_verifies, flag_sag])
    
    features_from_warcs.append({
        'siren': siren,
        'https_flag': flag_https,
        'email_domains': email_domains,
        'trust_ts_flag': flag_trusted_shop,
        'trust_av_flag': flag_avis_verifies,
        'trust_sag_flag': flag_sag,
        'trust_flag': flag_trust,
    })
    
    print(f'{i+1} sirens processed.')

features_from_warcs_df = pd.DataFrame(features_from_warcs)

# SAVE OUTPUT

features_from_warcs_df.to_csv('features_from_warcs.csv', index=False)
