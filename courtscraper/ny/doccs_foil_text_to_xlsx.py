"""
Parses the foil data from the NY Department of Corrections and Community Supervision
"""
import re

import pandas as pd

DATA_TXT_FILE = 'foil_data.txt'
OUTFILE_XLSX = 'foil_data.xlsx'
DOB_RE = r"\d{8}"
DIN_RE = r"\d{2}[A-Za-z]\d{4}"

IGNORE = [
    "DIN NAME DOB RACE / ETHNIC MOST SERIOUS CRIME of COMMITMENT SECOND CRIME OF COMMITMENT THIRD CRIME OF COMMITMENT COUNTY OF INDICTMENT-1 COUNTY OF INDICTMENT-2 COUNTY OF INDICTMENT-3 AGGREGATE MINIMUM SENTENCE (YYYMM) AGGREGATE MAXIMUM SENTENCE (YYMM)",
    'Incarcerated Individuals Admitted from 2008 to Present with Crime of 2nd Degree Murder (Data as of 3/13/23)',
    'NYS Department of Corrections and Community Supervision'
]
ETHNICITIES = ['HISPANIC', 'BLACK', 'WHITE', 'ASIAN', 'NATIVE AMERICAN', 'OTHER']

CRIMES = [ 'ATT RAPE 2ND 2007', 'RAPE 2ND 2007', 
            'ATT FALSE BUS RCDS 1ST', 'FALSE BUS RCDS 1ST', 
            'ATT BURGLARY 2ND, SUB 2', 
            'BURGLARY 2ND, SUB 2', 'CRIM MISCHIEF 2ND', 'LV SCENE OF ACC W/O REP','ATT PREDATORY SEXUAL ASLT', 'PREDATORY SEXUAL ASLT', 'ATT ASLT POLICE/FIRE/EMT', 'ASLT POLICE/FIRE/EMT',
            'ATT CPCS 2ND', 'CPCS 2ND', 'ATT CR POS WEAP 3 SUB1-3', 'CR POS WEAP 3 SUB1-3',
            'ATT VEHICULR MANSL 2ND', 'VEHICULR MANSL 2ND',
            'ATT C POS WEAP 2ND', 'C POS WEAP 2ND',
            'ATT GANG ASSAULT 1ST', 'GANG ASSAULT 1ST',
            'ATT GANG ASSAULT 2ND', 'GANG ASSAULT 2ND',
            'ATT ROBBERY 2ND, SUB 1', 'ROBBERY 2ND, SUB 1',
            'ATT POS FORGE INS 2ND', 'POS FORGE INS 2ND',
            'ATT ASSAULT 1ST B FELONY', 'ASSAULT 1ST B FELONY', 
            'ATT MURDER 2ND', 'MURDER 2ND', 
            'ATT MURDER 1ST', 'MURDER 1ST', 
            'ATT BURGLARY 2ND, SUB 1', 'BURGLARY 2ND, SUB 1',
            'ATT BURGLARY 3RD', 'BURGLARY 3RD',
            'ATT BURGLARY 2ND', 'BURGLARY 2ND',
            'ATT MANSLAUGHTER 1ST', 'MANSLAUGHTER 1ST',
            'ATT MANSLAUGHTER 2ND', 'MANSLAUGHTER 2ND',
            'ATT BURGLARY 2ND', 'BURGLARY 2ND',
            'ATT BURGLARY 1ST', 'BURGLARY 1ST',
            'ATT HINDER PROSEC 1ST', 'HINDER PROSEC 1ST',
            'ATT CRIM FACIL 2ND', 'CRIM FACIL 2ND',
            'ATT BURGLARY 3RD', 'BURGLARY 3RD',
            'ATT C POS WEAPON 2ND', 'C POS WEAPON 2ND',
            'ATT TAMPERING EVIDENCE', 'TAMPERING EVIDENCE',
            'ATT GRAND LARCEN 4TH', 'GRAND LARCEN 4TH',
            'ATT RECK ENDANGER 1ST', 'RECK ENDANGER 1ST'
            'ATT CR POS WEAP SUB1', 'CR POS WEAP SUB1',
            'ATT ROBBERY 1ST', 'ROBBERY 1ST',
            'ATT PRED SEXUAL ASLT/CHILD', 'PRED SEXUAL ASLT/CHILD',
            'ATT C POS WEAPON 2ND', 'C POS WEAPON 2ND',
            'ATT C POS WEAPON 3RD SUB4-8VFO', 'C POS WEAPON 3RD SUB4-8VFO', 
            'ATT C POS WEAPON 3RD SUB4', 'C POS WEAPON 3RD SUB4',
            'ATT C POS WEAPON 3RD', 'C POS WEAPON 3RD',
            'ATT ASSAULT 1ST BFELONY', 'ASSAULT 1ST B FELONY',
            'C POS WEAPON 3RDSUB4', 'ATT C POS WEAPON 3RDSUB4',
            'ATT AG SEX ABUSE 2ND', 'AG SEX ABUSE 2ND'
            'ATT KIDNAPPING 1ST', 'KIDNAPPING 1ST',
            'ATT ASSAULT 2ND', 'ASSAULT 2ND',
            'ATT CONCEALMENT HUMAN CORPSE' 'CONCEALMENT HUMAN CORPSE',
            'ATT RECK ENDANGER 1ST', 'RECK ENDANGER 1ST',
            'ATT KIDNAPPING 1ST', 'KIDNAPPING 1ST',
            'ATT AG SEX ABUSE 2ND', 'AG SEX ABUSE 2ND',
            'ATT ROBBERY 2ND', 'ROBBERY 2ND', 
            'ATT GRAND LAR 3RD', 'GRAND LAR 3RD',
            'ATT IDENTITY THEFT', 'IDENTITY THEFT',
            'ATT CRIM SOLI 2ND', 'CRIM SOLI 2ND',
            'ATT BRIBING WITNESS', 'BRIBING WITNESS',
            'ATT CSCS 4TH', 'CSCS 4TH',
            'ATT FORGERY 2ND', 'FORGERY 2ND',
            'ATT GRAND LARCEN 3RD', 'GRAND LARCEN 3RD',
            'ATT ROBBERY 3RD', 'ROBBERY 3RD',
            'ATT CSCS 3RD', 'CSCS 3RD',
            'VEHICULR MANSL 1ST', 'ATT VEHICULR MANSL 1ST',
            'ATT CPCS 4TH', 'CPCS 4TH',
            'ATT ARSON 3RD', 'ARSON 3RD',
            'ATT AGG.CRIMINAL CONTEMPT', 'AGG.CRIMINAL CONTEMPT',
            'ATT MENACING', 'MENACING',
            'ATT CONSPIRACY 2ND', 'CONSPIRACY 2ND',
            'ATT CR POS WEAP', 'CR POS WEAP',
            'ATT RAPE 1ST', 'RAPE 1ST',
            'ATT UNLAWFUL IMPRIS', 'UNLAWFUL IMPRIS',
            'ATT DRIVE IMPAIR 3 OFF', 'DRIVE IMPAIR 3 OFF',
            'ATT CONTRABAND 1ST', 'CONTRABAND 1ST',
            'ATT CONTEMPT 1ST', 'CONTEMPT 1ST',
            'ATT CRIM SEX ACT 1ST', 'CRIM SEX ACT 1ST',
            'ATT STOLEN PROP 4TH', 'STOLEN PROP 4TH',
            'ATT KIDNAPPING 2ND', 'KIDNAPPING 2ND',
            'ATT CPCS 3RD', 'CPCS 3RD',
            'ATT ARSON 2ND', 'ARSON 2ND',
            'ATT USE FIREAMS 1ST', 'USE FIREAMS 1ST',
            'ATT CONSPIRACY 1ST', 'CONSPIRACY 1ST',
            'ATT UNLICENSED DRIVER', 'UNLICENSED DRIVER',
            'ATT FALSE INSTRUMENT', 'FALSE INSTRUMENT',
            'ATT ARSON 1ST', 'ARSON 1ST',
            'ATT ASLT', 'ASLT',
            'ATT FLEE OFFICER MOTOR VEH', 'FLEE OFFICER MOTOR VEH',
            'ATT GR LAR 4TH AUTO', 'GR LAR 4TH AUTO',
            'ATT CRIM MISCHIEF 3RD', 'CRIM MISCHIEF 3RD',
            'ATT CPCS 5TH', 'CPCS 5TH', 
            'ATT REP', 'REP',
            'ATT CPCS 1ST', 'CPCS 1ST',
            'ATT STOLEN PROP 3RD', 'STOLEN PROP 3RD',
            'ATT POS FORGE INS 2ND', 'POS FORGE INS 2ND',
            'ATT SEXUAL ABUSE 1ST', 'SEXUAL ABUSE 1ST',
            'ATT USE FIREARMS 2ND', 'USE FIREARMS 2ND',
            'CONTEMPT', 'ATT CONTEMPT',
            'ATT ABORTION 2ND', 'ABORTION 2ND',
            'ATT C POS WEAPON 1ST', 'C POS WEAPON 1ST',
            'ATT CRIM POS MARI 2', 'CRIM POS MARI',
            'ATT CONSPIRACY 4TH', 'CONSPIRACY 4TH',
            'ATT AGG VEHICULAR HOMICD', 'AGG VEHICULAR HOMICD',
            'ATT AG ASSAULT POLICE', 'AG ASSAULT POLICE',
            'ATT INTIMIDATE WIT 3RD', 'INTIMIDATE WIT 3RD',
            'ATT CONCEALMENT HUMAN CORPSE', 'CONCEALMENT HUMAN CORPSE',
            'ATT STRANGULATION 1ST', 'STRANGULATION 1ST',
            'CRIM FACIL HINDER PROSEC 1ST',
            'ATT RAPE', 'RAPE',
            'OFF',
            'ATT ARSON 4TH', 'ARSON 4TH',
            'ATT AGGRAV MURDER', 'AGGRAVATED MURDER',
            'ATT FALSE BUS RCDS', 'FALSE BUS RCDS',
            'ATT PERJURY 1ST', 'PERJURY 1ST',
            'ATT GR LAR 3RD AUTO', 'GR LAR 3RD AUTO',
            'ATT UNLAW DISECT HUMAN BODY', 'UNLAW DISECT HUMAN BODY',
            'ATT BAIL JUMPING 2ND', 'BAIL JUMPING 2ND',
            'ATT ESCAPE 1ST', 'ESCAPE 1ST',
            'ATT POS FORGE 1ST', 'POS FORGE 1ST',
            'ATT INS FRAUD 2ND', 'INS FRAUD 2ND',
            'ATT OPER MAJOR DRUG TRFKR', 'OPER MAJOR DRUG TRFKR',
            'HUMAN CORPSE', 'CR POSS FIREARM',
         ]
COUNTIES = ['QUEENS','KINGS', 'NEW YORK', 'BRONX', 'WESTCHESTER', 'NASSAU', 'MONROE', 'DUTCHESS', 'ORANGE',
           'ALBANY', 'ERIE', 'SUFFOLK', 'SCHENECTADY', 'RICHMOND', 'COLUMBIA', 'ONONDAGA', 'BROOME', 'CHENANGO',
           'FULTON', 'ONEIDA', 'NIAGARA', 'STEUBEN', 'WARREN', 'WAYNE', 'GENESEE', 'WASHINGTON', 'GREENE', 'OSWEGO',
           'SULLIVAN', 'LIVINGSTON', 'FRANKLIN', 'ULSTER', 'JEFFERSON', 'CATTARAUGUS', 'MONTGOMERY', 'ONTARIO',
           'TOMPKINS', 'CHAUTAUQUA', 'RENSSELAER', 'CHEMUNG', 'TIOGA', 'CLINTON', 'ESSEX', 'CORTLAND', 'SENECA', 
           'PUTNAM', 'SCHOHARIE', 'ROCKLAND', 'CAYUGA', 'ST LAWRENCE', 'LEWIS', 'SARATOGA', 'YATES', 'HERKIMER',
           'ORLEANS', 'MADISON', 'OTSEGO', 'WYOMING', 'SCHUYLER']

def order_by_string_order(line, lst, length=0):
    """Orders a list of strings by the order of the string in the original string"""
    lst = sorted(lst, key=line.index)
    if length:
        for _ in range(length - len(lst)):
            lst.append(None)
    return lst

def din_in_line(text):
    """Returns the DIN if it exists in the line"""
    din_match = re.search(DIN_RE, text)
    if din_match:
        return din_match.group()
    
def dob_in_line(text):
    """Returns the DOB if it exists in the line"""
    dob_match = re.search(DOB_RE, text)
    if dob_match:
        return dob_match.group()
    
def extract_fields(text, fields):
    """Extracts the fields from the text"""
    original = text
    tokens = []
    for field in fields:
        if field in text:
            tokens.append(field)
            text = text.replace(field, '', 1)
    return order_by_string_order(original, tokens, length=3)




def get_agg_lines(fname):

    with open(fname, 'r') as file:
        lines = [line for line in file]

    # Extract data using regular expressions
    agg_lines = []
    current_line = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(_ in line for _ in IGNORE):
            continue
        if din_in_line(line):
            if current_line:
                agg_lines.append(current_line)
            current_line = line
        else:
            current_line += ' '
            current_line += line
    agg_lines.append(current_line)
    return agg_lines


def get_min_sentence(line):
    line = line.replace('LIFE', '')
    last_token = line.split()[-1]
    if last_token.isnumeric():
        min_sentence = last_token
        min_sentence_months = int(last_token[-2:])
        min_sentence_years = int(last_token[:-2])
        return 12 * min_sentence_years + min_sentence_months
        


def main():
    """Main function"""
    agg_lines = get_agg_lines(DATA_TXT_FILE)

    data = []

    for line in agg_lines:
        din = din_in_line(line)
        dob = dob_in_line(line)
        name = line.split(din)[-1].split(dob)[0].strip()
        crimes = extract_fields(line, CRIMES)
        counties = extract_fields(line, COUNTIES)
        ethnicity = extract_fields(line, ETHNICITIES)[0]
        min_sentence = get_min_sentence(line)

        data_line = [din, name, dob, ethnicity, 
            crimes[0], crimes[1], crimes[2],
            counties[0], counties[1], counties[2],
            min_sentence,
            'LIFE']
        data.append(data_line)

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'DIN', 
        'Name', 'Date of Birth', 'Ethnicity', 
        'Most Serious Crime', 'Second Crime', 'Third Crime', 
        'County of Indictment 1', 'County of Indictment 2', 'County of Indictment 3',
        'Min Prison Term in Months',
        'Aggregate Max Sentence'
    ])

    df.to_excel(OUTFILE_XLSX, index=False)

    convictions = []
    crimes = ['Most Serious Crime', 'Second Crime', 'Third Crime']
    counties = ['County of Indictment 1', 'County of Indictment 2', 'County of Indictment 3']
    for idx, fieldname in crimes:
        for _, line in df.iterrows():
            if line[fieldname] == 'MURDER 2ND':
                convictions.append([
                    line['DIN'],
                    line['Name'],
                    line['Date of Birth'],
                    line['Ethnicity'],
                    line[fieldname],
                    line[counties[idx]]
                ])
        

if __name__ == '__main__':
    main()
