"""
Parses the foil data from the NY Department of Corrections and Community Supervision
"""
import re
import pandas as pd

from courtscraper.data_utils.consts import DOCCS_FOIL_TXT_PATH, DOCCS_FOIL_XLSX, \
    IGNORE, ETHNICITIES, CRIMES, COUNTIES


DOB_RE = r"\d{8}"
DIN_RE = r"\d{2}[A-Za-z]\d{4}"

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
    """Get aggregated lines from file
    
    The file has lots of broken up lines, so
    this function groups them together when they
    are part of the same record, breaking into new 
    lines on the DIN"""
    with open(fname, 'r', encoding="utf-8") as file:
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
    """Get minimum sentence in months
    
    It's formatted YYYMM, so we need to convert to months"""
    line = line.replace('LIFE', '')
    last_token = line.split()[-1]
    if last_token.isnumeric():
        min_sentence_months = int(last_token[-2:])
        min_sentence_years = int(last_token[:-2])
        return 12 * min_sentence_years + min_sentence_months

def txt_to_xlsx():
    """Main function"""
    agg_lines = get_agg_lines(DOCCS_FOIL_TXT_PATH)

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
    out_df = pd.DataFrame(data, columns=[
        'DIN', 
        'Name', 'Date of Birth', 'Ethnicity', 
        'Most Serious Crime', 'Second Crime', 'Third Crime', 
        'County of Indictment 1', 'County of Indictment 2', 'County of Indictment 3',
        'Min Prison Term in Months',
        'Aggregate Max Sentence'
    ])

    out_df.to_excel(DOCCS_FOIL_XLSX, index=False)

    convictions = []
    crimes = ['Most Serious Crime', 'Second Crime', 'Third Crime']
    counties = ['County of Indictment 1', 'County of Indictment 2', 'County of Indictment 3']
    for idx, fieldname in crimes:
        for _, line in out_df.iterrows():
            if line[fieldname] == 'MURDER 2ND':
                convictions.append([
                    line['DIN'],
                    line['Name'],
                    line['Date of Birth'],
                    line['Ethnicity'],
                    line[fieldname],
                    line[counties[idx]]
                ])
