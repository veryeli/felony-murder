"""
Parses the foil data from the NY Department of Corrections and Community Supervision
"""
import re
import pandas as pd

from courtscraper.data_utils.consts import DOCCS_FOIL_TXT_PATH, DOCCS_FOIL_XLSX, \
    ETHNICITIES, CRIMES, COUNTIES

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

def extract_fields(text, fields, length=3):
    """Extracts the fields from the text"""
    original = text
    tokens = []
    for _ in range(length):
        for field in fields:
            if field in text:
                tokens.append(field)
                text = text.replace(field, '', 1)
    return order_by_string_order(original, tokens, length)

def get_min_sentence(line):
    """Returns the minimum sentence in months"""
    line = line.replace('LIFE', '')
    last_token = line.split()[-1]
    if last_token.isnumeric():
        min_sentence_months = int(last_token[-2:])
        min_sentence_years = int(last_token[:-2])
        return 12 * min_sentence_years + min_sentence_months

def gen_xlsx(line_to_examine=None):
    """Generates the xlsx file from the text file"""
    lines = [_.strip() for _ in open(DOCCS_FOIL_TXT_PATH, 'r', encoding='utf-8')]
    data = []

    for line in lines:
        din = din_in_line(line)
        if din == line_to_examine:
            print(line)
        dob = dob_in_line(line)
        name = line.split(din)[-1].split(dob)[0].strip()
        crimes = extract_fields(line, CRIMES)
        if din == line_to_examine:
            print(crimes)
        counties = extract_fields(line, COUNTIES)
        if din == line_to_examine:
            print(counties)
        ethnicity = extract_fields(line, ETHNICITIES)[0]
        min_sentence = get_min_sentence(line)

        data_line = [
            din, name, dob, ethnicity,
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
