from warcio.archiveiterator import ArchiveIterator
import os
from urllib.parse import urlparse
import json
import numpy as np

def write(str_to_write):
    file = open('progress.txt','a+')
    file.write(str_to_write + '\n')
    file.close()
    print(str_to_write)

path = '/mnt/bigdata/s3/'
unique_domains = np.load('/project/0_cleaning/output_cleaning/unique_domains_ecom.npy')
warc_per_dom = {}
write('Running script...')

for i, warc in enumerate(os.listdir(path)):

    if i%100000 == 0:
        write(f'{i} warcs processed.\n')
        
    file_path = path + warc
    stream = open(file_path, 'rb')
    try:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
    except:
        pass
    else:
        parsed_domain = urlparse(url).netloc
        if parsed_domain in unique_domains:
            if parsed_domain in warc_per_dom:
                warc_per_dom[parsed_domain].append(warc)
            else:
                warc_per_dom[parsed_domain] = [warc]        
    finally:
        stream.close()
            
json_content = json.dumps(warc_per_dom)
f = open("/project/0_cleaning/output_cleaning/warc_per_dom.json","w")
f.write(json_content)
f.close()
