import json
from tqdm import tqdm
from warcio.archiveiterator import ArchiveIterator
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool
print('Running script...')

# Extract decoded content of crawled page as string
def get_warc_content(warc):
    
    file_path = '/mnt/bigdata/s3/'+ warc

    with open(file_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                content_byte = record.content_stream().read()
                try:
                    content_decoded = content_byte.decode('utf-8')
                except:
                    content_decoded = ''
                    
    return content_decoded

# Ensure that the content makes it likely to extract a siren or siret
def validate_warc_content(content_text):
    if re.search(r'[ :>]{1}(r\.?c\.?s|s\.?i\.?r\.?e\.?[nt]{1}|immatric|registr)', content_text):
        return True
    else:
        return False

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
    exclude = ['00000000000000'] # explicitely exclude hosting companies
    
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
def find_siret_siren(warc):
    siren_in_warc = []
    siret_in_warc = []
    
    content_http = get_warc_content(warc)
    try:
        content_text = BeautifulSoup(content_http, "html.parser").find('body').get_text(separator=' ').replace('\n', ' ').replace('\xa0', ' ').replace('\t', ' ').lower()
    except:
        content_text = ''

    if validate_warc_content(content_text):
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
            
    return [siren_in_warc, siret_in_warc] 

# Clean output of multiprocessed search
def handle_results(results, siren_or_siret): # siren is 0 and siret is 1
    ids = [sublist[siren_or_siret] for sublist in results if len(sublist[siren_or_siret])>0]
    if len(ids)>0:
        ids_flat = [item for sublist in ids for item in sublist]
        ids_final = list(dict.fromkeys(ids_flat))
    else:
        ids_final = []
    return ids_final

# Function to save output as JSON
def json_save(obj, name):
    json_content = json.dumps(obj)
    f = open(f"/project/0_cleaning/output_cleaning/{name}.json","w")
    f.write(json_content)
    f.close()

###########################################################################
############### RUN AND SAVE EXTRACTION ###################################

f = open("/project/0_cleaning/output_cleaning/warc_per_dom.json","r")
domains_warcs = json.load(f)
f.close()

siren_per_domain = {}
siret_per_domain = {}

for i, (domain, warcs) in enumerate(domains_warcs.items()):
    pool = Pool(processes=20)
    results = pool.map(find_siret_siren, warcs)
    sirens = handle_results(results, 0)
    sirets = handle_results(results, 1)
    pool.close()
    
    siren_per_domain[domain] = sirens
    siret_per_domain[domain] = sirets
    
    print(f'{i+1} domains processed.')

json_save(siren_per_domain,'sirens_in_warcs')
json_save(siret_per_domain,'sirets_in_warcs')