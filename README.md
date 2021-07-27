## Usage

### Querying metadata of data files
1. The `Files` object represents a GDC Files query.
```
import gdc

files_query = gdc.Files()
```
2. Add filters using `.add_filters` to obtain files of interest. Available filters can be found [here](https://docs.gdc.cancer.gov/API/Users_Guide/Appendix_A_Available_Fields/).
```
# To get all HTSeq counts of TCGA-STAD tumor samples

filters = {
  'cases.samples.sample_type': 'Primary Tumor',
  'cases.project.project_id': 'TCGA-STAD',
  'analysis.workflow_type': 'HTSeq - Counts'
}

files_query.add_filters(filters)
```
3. Send the request using `.query`. If successful, the result is a `pandas.DataFrame` object of the metadata.
```
metadata = files_query.query()
```
<br>

Putting it together, the whole process is designed to work in a single line
```
import gdc

metadata = gdc.Files().add_filters({
  'cases.samples.sample_type': 'Primary Tumor',
  'cases.project.project_id': 'TCGA-STAD',
  'analysis.workflow_type': 'HTSeq - Counts'
}).query()
```

### Downloading files using file ids from the query above
When done exactly as above, the DataFrame result should look something like this
```
>> metadata.shape
(375, 8)

>> metadata.columns
Index(['case_id', 'disease_type', 'project_id', 'sample_type', 'submitter_id',
       'file_id', 'file_name', 'id'],
      dtype='object')

>> metadata.file_id.head()
0    0ecd722f-1272-4503-ad89-e928ef80e070
1    8ce7dcbd-01a6-42d4-9641-2d3e793c7000
2    c82ca0d4-c350-4a0b-8f12-cd7d35fa4379
3    620abd9f-1f6e-4883-8084-584b0d77bb7d
4    1e579949-ff4f-4c2f-9fd2-98eccc8779e3
Name: file_id, dtype: object
```
You can obtain the list of file ids with `metadata.file_id`

1. The `Data` object represents a GDC Data query
```
# Create the Data object with the list of file ids from the query above
data = gdc.Data(metadata.file_id)
```
2. Download the files and provide the output directory path. Note that file ids that are already found within the 
provided directory will be assumed as files downloaded before, and will be skipped by default due to caching. 
This behaviour can be changed by passing in `cached=False` in `.download(path, cached=False)`.
```
data.download('downloads/')
```
<br>

Likewise, the process is designed to be one-lined.
```
gdc.Data(metadata.file_id).download('downloads/')
```

### Useful filters
To obtain RNA-Seq BAM files of TCGA-STAD tumor samples
```
filters = {
  'cases.samples.sample_type': 'Primary Tumor',
  'cases.project.project_id': 'TCGA-STAD',
  'data_type': 'Aligned Reads',
  'experimental_strategy': 'RNA-Seq',
  'data_format': 'BAM'
}
```

## TODO
The GDC API is much more extensive than these two objects. This is a quick dirty way to query and download files required.
More features will be added in the future.
