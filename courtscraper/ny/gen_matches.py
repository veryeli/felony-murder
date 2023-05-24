"""Utilities to generate potential matches"""
import pandas as pd

from courtscraper.data_utils.consts import DOCCS_FOIL_XLSX, TRACKER_PATH, \
    GENERATED_MATCHES

def gen_convictions_df():
    """Generates a dataframe of convictions from the DOCCS list"""
    doccs_df = pd.read_excel(DOCCS_FOIL_XLSX)
    convictions = []
    crimes = ['Most Serious Crime', 'Second Crime', 'Third Crime']
    counties = ['County of Indictment 1', 'County of Indictment 2', 'County of Indictment 3']
    for idx, fieldname in enumerate(crimes):
        for _, line in doccs_df.iterrows():
            if line[fieldname] == 'MURDER 2ND':
                convictions.append([
                    line['DIN'],
                    line['Name'],
                    line['Date of Birth'],
                    line['Ethnicity'],
                    line[fieldname],
                    line[counties[idx]],
                    line['Min Prison Term in Months']
                ])
    convs = pd.DataFrame(convictions)
    convs.columns = ['DIN', 'Name', 'DOB', 'Race', 'Crime', 'County', 'Min Term (Months)']

    convs.Name = convs.Name.apply(lambda x: x.title())
    convs.Race = convs.Race.apply(lambda x: x.title())
    convs.County = convs.County.apply(lambda x: x.title())
    convs.County = convs.County.apply(lambda x: 'St. Lawrence' if x == 'St Lawrence' else x)
    convs['YOB'] = convs.DOB.apply(lambda x: int(str(x)[:4]))
    convs.Race = convs.Race.apply(lambda x: x if x in
                                  ['Black', 'White', 'Hispanic', 'Asian']
                                   else 'Other-Unknown')
    convs = convs.drop_duplicates()
    return convs

def gen_matches():
    """Generates exact matches between the tracker data - 
    skipping over the ones that have already been matched"""

    # Generate dataframe of convictions from the DIN liist
    convs = gen_convictions_df()
    tracker = pd.read_excel(TRACKER_PATH, sheet_name=1)
    tracker['AutoName'] = tracker['Name']

    with open(GENERATED_MATCHES, 'w', encoding='utf-8') as file:
        for _, row in tracker.iterrows():
            if row['AutoName'] and str(row['AutoName']) != 'nan':
                continue
            if row['Crime Year'] != 'Unknown' and row['Crime Year'] >= 2020:
                continue
            match_convs = convs[convs['County'].apply(lambda x: x == row['Disposition County'])]
            if str(row['Min Prison Term in Months']) in ['nan', 'Unknown']:
                match_convs = match_convs[
                    match_convs['Min Term (Months)'].apply(
                        lambda x: str(x) == 'nan')]
            else:
                match_convs = match_convs[
                    match_convs['Min Term (Months)'].apply(
                        lambda x: str(x) != 'nan' and int(x) ==
                            int(row['Min Prison Term in Months']))]

            if match_convs.empty:
                continue
            match_convs = match_convs[
                match_convs['Race'].apply(
                    lambda x: x == row['Race/Ethnicity of Arrestee'])]
            if match_convs.empty:
                continue
            if row['Crime Year'] != 'Unknown':
                potential_yobs = [(row['Crime Year'] - row['Age at Crime']),
                                (row['Crime Year'] - row['Age at Crime']) - 1]
                match_convs = match_convs[
                    match_convs['YOB'].apply(
                        lambda x: x in potential_yobs)]
            if match_convs.empty:
                continue
            match_convs = match_convs[match_convs['DIN'].apply(
                    lambda x: int(x[:2]) >= int(str(row['Arrest Year'])[2:])
                )]

            if not match_convs.empty:
                match_convs = match_convs.set_index('DIN')
                file.write(f"Original Number: {row['Original Number']} \n")
                file.write(f"Crime Year: {row['Crime Year']} Age at Arrest: {row['Age at Crime']}")
                file.write(f" Arrest Year: {row['Arrest Year']} ")
                file.write(f"Race: {row['Race/Ethnicity of Arrestee']} ")
                file.write(f"Disposition County: {row['Disposition County']} \n")
                file.write(str(match_convs[['Name', 'DOB', 'Race', 'County', 'Min Term (Months)']]))
                file.write('\n\n----------------------\n')
