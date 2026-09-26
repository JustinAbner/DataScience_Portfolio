#!/usr/bin/env python

import requests
import time
from datetime import datetime
import logging
import os
import sys
import pyarrow
import json
import sqljoin

os.makedirs('./business_logs', exist_ok=True)
os.makedirs('./parquet_files', exist_ok=True)

logging.basicConfig(
    filename=f'./business_logs/{datetime.now().strftime("%Y%m%d")}.log', 
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

business_licenses = 'https://data.cityofchicago.org/api/v3/views/r5kz-chrr/query.json' #soda3 
business_owners = 'https://data.cityofchicago.org/api/v3/views/ezma-pppn/query.json' #soda3

def staging_dataframe(json_list):
    ''' Purpose:
        Converting the json get response into a pyarrow table and
        replacing the special characters attached to the metadata columns
        Output:
        A modified table with columns appropriate for sql '''  

    stg_df1 = pyarrow.Table.from_pylist(json_list)
    mapping = str.maketrans({':': 'sys_', '@': ''})
    new_cols = [col.translate(mapping) for col in stg_df1.column_names]
    pa_df = stg_df1.rename_columns(new_cols) 
    logger.info(f'Rows: {pa_df.shape[0]} | Columns: {pa_df.shape[1]}\n')
    return pa_df

class Get_API:
    ''' Purpose:
        Storing like methods responsible for connecting and getting data from the API '''
    def __init__(self, url, tag):
        self.url = url
        self.tag = tag
        self.staged_data = []
        self.retry = 1

    def task_retry(self):
        ''' Purpose:
            Updating the retry counter, waiting, and then reattempting the get request '''
        self.retry += 1
        logging.info(f'..Up for retry - Attempt {self.retry}/4')
        time.sleep(60)
        self.config()

    def config(self):
        ''' Purpose:
            Check for environment token to determine page size. Per SODA3 API, performace may degrage with larger
            page sizes/limits without a token.
            Output:
            Returns the API token header and a larger page size (default is 1000 without token) '''
        try:
            header = {'X-APP-TOKEN' : os.environ['SODA_TOKEN']}
            pageSize = 50000
            return self.scrape(header, pageSize)
        except KeyError as ke:
            logger.warning(f'KeyError - {ke}..Missing environment variable, using SODA API defaults')
            return self.scrape()
    
    def scrape(self, header=None, pageSize=1000):
        ''' Purpose:
            Iterate through each of the API pages and storing the json responses in a list
            Output:
            List of key value pairs '''
        pageNum = 1
        
        while True:
            logger.info(f'..Parsing Page:{pageNum} - {self.tag}')
            response = requests.get(self.url, params={'pageNumber':pageNum, 'pageSize':pageSize}, headers=header) 

            # Grabbing all headers, populating so each incoming load has a key reference
            if response.status_code == 200 and pageNum == 1:
                fields = json.loads(response.headers['X-SODA2-Fields'])
                self.staged_data.append({fld:None for fld in fields})
            
            if response.status_code == 200 and len(response.json()) != 0: 
                self.staged_data.extend(response.json())
                pageNum += 1
                time.sleep(2.5)
            
            elif response.status_code != 200:
                logger.error(f'Status Code : {response.status_code}')
                if self.retry < 4:
                    self.task_retry()
                logger.critical(f'..Exiting with code 1')
                sys.exit(1)
            
            elif len(response.json()) == 0: 
                logger.info('all data retrieved')
                return staging_dataframe(self.staged_data)
         
def main():
    business_owner_padf = Get_API(business_owners, 'owners').config() 
    business_license_padf = Get_API(business_licenses, 'licenses').config() 
    
    joined_data = sqljoin.owner_license(business_owner_padf, business_license_padf)
    
    logger.info(f'..Creating parquete file: ./parquet_files/business_data_{datetime.now().strftime("%Y%m%d")}.parquet')
    joined_data.to_parquet(f'./parquet_files/business_data_{datetime.now().strftime("%Y%m%d")}.parquet')
    logger.info(f'Success')
    print('- Complete')
    sys.exit()

if __name__=='__main__':
    print(f'- Log location > ./business_logs/{datetime.now().strftime("%Y%m%d")}.log')
    print('- ...Fetching data from https://data.cityofchicago.org')
    main()

