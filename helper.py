import binascii
import os
import re


LICENSES = {
    'Creative Commons Attribution': 'cc-by',
    'Creative Commons Attribution Share-Alike': 'cc-by-sa',
    'Creative Commons CCZero': 'cc-zero',
    'Creative Commons Non-Commercial (Any)': 'cc-nc',
    'GNU Free Documentation License': 'gfdl',
    'License Not Specified': 'notspecified',
    'Open Data Commons Attribution License': 'odc-by',
    'Open Data Commons Open Database License (ODbL)': 'odc-odbl',
    'Open Data Commons Public Domain Dedication and License (PDDL)': 'odc-pddl',
    'Other (Attribution)': 'other-at',
    'Other (Non-Commercial)': 'other-nc',
    'Other (Not Open)': 'other-closed',
    'Other (Open)': 'other-open',
    'Other (Public Domain)': 'other-pd',
    'UK Open Government Licence (OGL)': 'uk-ogl',
}

def get_readable_frequency(frequency):
    accrual_periodicity_dict = {
        'completely irregular': 'Irregular',
        'R/P10Y': 'Decennial',
        'R/P4Y': 'Quadrennial',
        'R/P1Y': 'Annual',
        'R/P2M': 'Bimonthly',
        'R/P3.5D': 'Semiweekly',
        'R/P1D': 'Daily',
        'R/P2W': 'Biweekly',
        'R/P6M': 'Semiannual',
        'R/P2Y': 'Biennial',
        'R/P3Y': 'Triennial',
        'R/P0.33W': 'Three times a week',
        'R/P0.33M': 'Three times a month',
        'R/PT1S': 'Continuously updated',
        'R/P1M': 'Monthly',
        'R/P3M': 'Quarterly',
        'R/P0.5M': 'Semimonthly',
        'R/P4M': 'Three times a year',
        'R/P1W': 'weekly',
    }
    return accrual_periodicity_dict.get(frequency, frequency)

def munge_name(name):
    '''Munges the package name field in case it is not to spec.
    '''
    # remove foreign accents
    if isinstance(name, unicode):
        name = substitute_ascii_equivalents(name)
    # separators become dashes
    name = re.sub('[ .:/]', '-', name)
    # take out not-allowed characters
    name = re.sub('[^a-zA-Z0-9-_]', '', name).lower()
    # keep it within the length spec
    name = _munge_to_length(name, 3, 90)
    return name

def re_munge_name(name):
    name = name[:90]
    name = name + '-' + binascii.b2a_hex(os.urandom(2))
    return name

def munge_title_to_name(name):
    '''Munge a package title into a package name.
    '''
    # remove foreign accents
    if isinstance(name, unicode):
        name = substitute_ascii_equivalents(name)
    # convert spaces and separators
    name = re.sub('[ .:/]', '-', name)
    # take out not-allowed characters
    name = re.sub('[^a-zA-Z0-9-_]', '', name).lower()
    # remove doubles
    name = re.sub('--', '-', name)
    # remove leading or trailing hyphens
    name = name.strip('-')
    # if longer than max_length, keep last word if a year
    max_length = 90 - 5
    # (make length less than max, in case we need a few for '_' chars
    # to de-clash names.)
    if len(name) > max_length:
        year_match = re.match(r'.*?[_-]((?:\d{2,4}[-/])?\d{2,4})$', name)
        if year_match:
            year = year_match.groups()[0]
            name = '%s-%s' % (name[:(max_length-len(year)-1)], year)
        else:
            name = name[:max_length]
    name = _munge_to_length(name, 3, 90)
    return name

def substitute_ascii_equivalents(text_unicode):
    # Method taken from: http://code.activestate.com/recipes/251871/
    """This takes a UNICODE string and replaces Latin-1 characters with
        something equivalent in 7-bit ASCII. It returns a plain ASCII string.
        This function makes a best effort to convert Latin-1 characters into
        ASCII equivalents. It does not just strip out the Latin-1 characters.
        All characters in the standard 7-bit ASCII range are preserved.
        In the 8th bit range all the Latin-1 accented letters are converted
        to unaccented equivalents. Most symbol characters are converted to
        something meaningful. Anything not converted is deleted.
    """
    char_mapping = {
        0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
        0xc6: 'Ae', 0xc7: 'C',
        0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
        0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
        0xd0: 'Th', 0xd1: 'N',
        0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O', 0xd8: 'O',
        0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
        0xdd: 'Y', 0xde: 'th', 0xdf: 'ss',
        0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
        0xe6: 'ae', 0xe7: 'c',
        0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
        0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
        0xf0: 'th', 0xf1: 'n',
        0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o', 0xf8: 'o',
        0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
        0xfd: 'y', 0xfe: 'th', 0xff: 'y',
        #0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        #0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        #0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        #0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        #0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        #0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        #0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
        #0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        #0xd7:'*', 0xf7:'/'
        }

    r = ''
    for char in text_unicode:
        if char_mapping.has_key(ord(char)):
            r += char_mapping[ord(char)]
        elif ord(char) >= 0x80:
            pass
        else:
            r += str(char)
    return r


def munge_tag(tag):
    tag = substitute_ascii_equivalents(tag)
    tag = tag.lower().strip()
    tag = re.sub(r'[^a-zA-Z0-9\- ]', '', tag)
    tag = _munge_to_length(tag, 2, 100)
    return tag

def _munge_to_length(string, min_length, max_length):
    '''Pad/truncates a string'''
    if len(string) < min_length:
        string += '_' * (min_length - len(string))
    if len(string) > max_length:
        string = string[:max_length]
    return string
