import pandas as pd
import numpy as np

# See src folder for detail code
from scraper import get_indicator_input_values, convert_input_as_index, extract, INDICATOR_VALUES_FILEPATH
from input import input_dict_list


def transform(input_dict, result_dict):
    # Convert to DataFrame
    df = pd.DataFrame(
        result_dict['content'], 
        columns=result_dict['headers']
    )
    # Make tabular table
    df2 = df.drop(columns=['No'])
    df2 = df2.melt(
        id_vars=['Indikator', 'Satuan'],
        var_name="Tahun",
        value_name="Jumlah"
    )
    # Add subsektor, komoditi, provinsi, kabupaten
    columns_to_add = ['subsektor', 'komoditas', 'prov', 'kab']
    df_info = pd.DataFrame(
        np.eye(df2.shape[0], len(columns_to_add)),
        columns=columns_to_add
    )
    for col in columns_to_add:
        if (input_dict[col] == '') or (input_dict[col] == None):
            df_info[col] = np.nan
        else:
            df_info[col] = input_dict[col]
    # Final dataframe
    return pd.concat([df_info, df2], axis=1)        

def load(df, output_path, format='csv'):
    if format != 'csv':
        print('Temporarily only accept csv as output file format')
        return None
    
    df.to_csv(output_path, index=False)
    
def main(input_dict):
    # Scrapped indicator values
    indicator_dict = get_indicator_input_values(path=INDICATOR_VALUES_FILEPATH)
    
    # Get an index for each indicator for XPATH
    input_with_idx = convert_input_as_index(indicator_dict, input_dict)
    
    # Extract the table
    result_dict = extract(indicator_dict, input_with_idx)
    
    # Transform the table into tabular format
    df = transform(input_dict, result_dict)
    
    # Save it as csv
    subsektor = input_dict['subsektor'].replace(" ", "_").lower()
    komoditas = input_dict['komoditas'].replace(" ", "_").lower()
    level = input_dict['level'].replace(" ", "_").lower()
    # prov = input_dict['prov'].replace(" ", "_").lower()
    # kab = input_dict['kab'].replace(" ", "_").lower()
    tahun_awal = input_dict['tahunAwal'].replace(" ", "_").lower()
    tahun_akhir = input_dict['tahunAkhir'].replace(" ", "_").lower()
    
    output_path = f"data/DataKeluaranIndikator_{komoditas}_{level}_{tahun_awal}_{tahun_akhir}.csv"
    load(df, output_path, format='csv')

if __name__ == "__main__":
    main(input_dict=input_dict_list[0])