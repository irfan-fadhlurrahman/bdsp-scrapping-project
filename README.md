# BDSP Scraper

## Dependencies
* Ubuntu 20.04 LTS
* Google Chrome & Chromedriver 111.0.5563.146
* Python 3.8
* Selenium
* Numpy
* Pandas
* Dill

## Python Script
1. [input.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/input.py): To store indicator input samples.
2. [indicator.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/indicator.py): To scrap all indicator values such as _Subsektor_, _Komoditas_, _Level_, _Provinsi_, _Kabupaten_, _Tahun Awal_, and _Tahun Akhir_
3. [scraper.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/scraper.py): To scrap a table based on indicator input in the [input.py]()
4. [etl.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/etl.py): To run all scripts that extract indicator values and tables, transform the table into tabular format dan save it as csv.

## Tasks
The main tasks of this project as follows:
1. Extract all indicator values such as _Subsektor_, _Komoditas_, _Level_, _Provinsi_, _Kabupaten_, _Tahun Awal_, and _Tahun Akhir_ from [BDSP dynamic website](https://bdsp2.pertanian.go.id/bdsp/id/indikator) using Selenium.
2. Extract a table based on specific indicators using Selenium and transform it into tabular format.

### Workflow for Scrapping all Indicator values
Please refer to [indicator.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/indicator.py) for the code.

1. Inspect all indicator input page source to gather the input we need to scrap. In this case, the following are the indicators to be scraped.
```python
INDICATOR_ID_LIST = [
    'subsektor',
    'komoditas',
    'level',
    'prov',
    'kab',
    'tahunAwal',
    'tahunAkhir',
]
```
2. Collect all XPATH from each indicator input. All indicator input has same XPATH format as follows:
```python
'//*[@id="{indicator_id}"]/option[{indicator_idx}]'
```
3. Find the elements for each indicator input by using Selenium and XPATH then use click() to open all html elements for indicator values. The order of find and click the elements based on `INDICATOR_ID_LIST`.

4. Once click() has opened all related html elements for all indicator values, extract all those values then return it as python dictionary / JSON format. In example:
```python
# Non-nested
{'subsektor': ['Tanaman Pangan', 'Perkebunan', 'Peternakan', 'Hortikultura']}

# Nested
{'komoditas': {
    'Tanaman Pangan': [
        'JAGUNG',
        'KACANG HIJAU',
        'KACANG TANAH',
        'KEDELAI',
        'PADI',
        'PADI LADANG',
        'PADI SAWAH',
        'UBIJALAR',
        'UBIKAYU / KETELA POHON'
    ],
    'Perkebunan': [
        'AREN',
        'ASAM JAWA',
        'CENGKEH',
        'JAMBU METE',
        'JARAK',
        'KAKAO'
    ]
}}
```
5. Collect all extracted dictionary into one binary file [indicator_input_dict.bin](). The reason to save as binary in order to avoid JSON parsing problem.

### Workflow for Scrapping table based on indicator input
Please refer to [etl.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/etl.py) and [scraper.py](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/src/scraper.py) for the code.

1. Prepare the indicator input. As example:
```python
{
    'subsektor': 'Tanaman Pangan',
    'komoditas': 'JAGUNG',
    'level': 'Kabupaten',
    'prov': 'Aceh',
    'kab': 'Kab. Simeulue',
    'tahunAwal': '1970',
    'tahunAkhir': '2023',
}
```
2. Get an index from the indicator value in the input for XPATH to find the elements.
An output example:
```python
{'subsektor': {'Tanaman Pangan': 2}}
```
3. Fill all the index to XPATH then begin to find and click the elements.
4. Find the 'search' button then wait to proceed to new page that contains table.
5. Scrap the table headers and its content then return it as python dictionary as follows:
```python
{
    "headers": ['No', 'Indikator', 'Satuan', '2021', '2022', '2023'],
    "content": [
        ['1', 'LUAS PANEN', 'Ha', '0,00', '0,00', '0,00'],
        ['2', 'PRODUKSI', 'Ton', '0,00', '0,00', '0,00'],
        ['3', 'PRODUKTIVITAS', 'Kuintal/Ha', '0,00', '0,00', '0,00']
    ]
}
```
6. Transform those dictionary into pandas dataframe. The result as follows:

 **No** | **Indikator** | **Satuan** | **2020** | **2021** | **2022** | **2023** 
--------|---------------|------------|----------|----------|----------|----------
 1      | LUAS PANEN    | Ha         | "0,00"   | "0,00"   | "0,00"   | "0,00"   
 2      | PRODUKSI      | Ton        | "0,00"   | "0,00"   | "0,00"   | "0,00"   
 3      | PRODUKTIVITAS | Kuintal/Ha | "0,00"   | "0,00"   | "0,00"   | "0,00"   

7. Convert this dataframe into tabular format like below.

 **subsektor**  | **komoditas** | **prov** | **kab**        | **Indikator** | **Satuan** | **Tahun** | **Jumlah** 
----------------|---------------|----------|----------------|---------------|------------|-----------|------------
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | LUAS PANEN    | Ha         | 1970      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | PRODUKSI      | Ton        | 1970      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | PRODUKTIVITAS | Kuintal/Ha | 1970      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | LUAS PANEN    | Ha         | 1971      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | PRODUKSI      | Ton        | 1971      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | PRODUKTIVITAS | Kuintal/Ha | 1971      | "0,00"     
 Tanaman Pangan | JAGUNG        | Aceh     | Kab\. Simeulue | LUAS PANEN    | Ha         | 1972      | "0,00"     


8. Save the table as csv. The saved file is [DataKeluaranIndikator_jagung_kabupaten_1970_2023.csv](https://github.com/irfan-fadhlurrahman/bdsp-scrapping-project/blob/main/data/DataKeluaranIndikator_jagung_kabupaten_1970_2023.csv)
