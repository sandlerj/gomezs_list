ca_prov_abbrev = {
    "Newfoundland":"NL",
    "Labrador":"NL",
    "Prince Edward Island":"PE",
    "Nova Scotia": "NS",
    "New Brunswick":"NB",
    "Quebec":"QC",
    "Ontario":"ON",
    "Manitoba":"MB",
    "Saskatchewan":"SK",
    "Alberta":"AB",
    "British Columbia":"BC",
    "Yukon":"YT",
    "Northwest Territories":"NT",
    "Nunavut":"NU"
}

abbrev_ca_prov = dict(map(reversed, ca_prov_abbrev.items()))

if __name__ == "__main__":
    print(abbrev_ca_prov[ca_prov_abbrev["Newfoundland"]])
    