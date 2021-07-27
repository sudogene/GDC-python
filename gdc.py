from io import StringIO
import os
import time
import re
import json
import tarfile
import requests
import pandas as pd


class Files:
    def __init__(self, token=''):
        self.filters = {}
        self.fields = self._generate_fields()
        self.size = 2000
        self.token = token
    
    def add_filters(self, filters: dict):
        self.filters.update(filters)
        return self

    def _generate_fields(self):
        """ https://docs.gdc.cancer.gov/API/Users_Guide/Appendix_A_Available_Fields/ """

        fields = [
            'file_name',
            'file_id',
            'cases.case_id',
            'cases.submitter_id',
            'cases.samples.sample_type',
            'cases.disease_type',
            'cases.project.project_id'
        ]
        return ','.join(fields)

    def _generate_query_filters(self, op='and'):
        content = []
        for field, value in self.filters.items():
            valist = value if isinstance(value, list) else [value]
            content.append({'op': 'in', 'content': {'field': field, 'value': valist}})
        filters = {'op': op, 'content': content}
        return filters
        
    def _get_tsv(self):
        files_endpt = 'https://api.gdc.cancer.gov/files'
        filters = self._generate_query_filters()
        params = {
            'filters': filters,
            'fields': self.fields,
            'size': self.size,
            'format': 'TSV'
        }
        response = requests.post(files_endpt,
            headers={'Content-Type': 'application/json', 'X-Auth-Token': self.token},
            data=json.dumps(params))
        
        while not response.ok:
            time.sleep(1)
            response = self.get()

        return response
        
    def query(self):
        """ Submits the search query and returns the result in a DataFrame """

        r = self._get_tsv()
        sio = StringIO(r.text)
        df = pd.read_csv(sio, sep='\t')
        df.columns = list(map(lambda c: c.split('.')[-1], df.columns))
        return df


class Data:
    def __init__(self, file_ids: list = [], token=''):
        self.file_ids = file_ids
        self.token = token
    
    def _preprocess_list(self, directory):
        existing = os.listdir(directory)
        return [fid for fid in self.file_ids if fid not in existing]


    def download(self, directory='./', unzip=True, cached=True):
        """ Downloads files from list of file ids """

        fids = self._preprocess_list(directory) if cached else list(self.file_ids)
        
        if len(fids) == 0:
            print('No new files to download')
            return
        else:
            print('Downloading', len(fids), 'files')

        data_endpt = 'https://api.gdc.cancer.gov/data'
        params = {'ids': fids}

        response = requests.post(data_endpt, data=json.dumps(params),
            headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.token})
        
        response_head_cd = response.headers['Content-Disposition']
        filename = re.findall('filename=(.+)', response_head_cd)[0]

        dlpath = os.path.join(directory, filename)

        # download files
        with open(dlpath, 'wb') as outfile:
            outfile.write(response.content)
        
        # extract files
        if unzip:
            print('Extracting files')
            tar = tarfile.open(dlpath, 'r:gz')
            tar.extractall(directory)
            tar.close()
