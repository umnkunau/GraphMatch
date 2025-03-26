#!/usr/bin/python3
##
## Ingest a file of unique alleles in the WMDA validation set and 
## create randome selections from those alleles to create arbitrary
## match sets.
## 
## BY: Timothy Kunau, kunau@umn.edu
## 

import re
import random

# Number of pairs to generate
#N = 10000001  #### DONORS
N = 1000001    #### PATIENTS


# Define regular expressions for each HLA allele type
hla_a_regex = r'^A\*\d+'
hla_b_regex = r'^B\*\d+'
hla_drb1_regex = r'^DRB1\*\d+'

# Initialize empty arrays for each allele type
hla_a = []
hla_b = []
hla_drb1 = []

# Open the file containing the HLA alleles
with open('./data/allele-all.csv', 'r') as f:
    # Iterate over each line in the file
    for line in f:
        # chop the RTN off of the line value
        allele = line.strip()

        # Use regular expressions to identify the allele type and extract the allele name
        if re.match(hla_a_regex, allele):
            hla_a.append(allele)
        elif re.match(hla_b_regex, allele):
            hla_b.append(allele)
        elif re.match(hla_drb1_regex, allele):
            hla_drb1.append(allele)

# Print the arrays
#print('hla_a    : ', len(hla_a))    #### DEBUG
#print('hla_b    : ', len(hla_b))    #### DEBUG
#print('hla_drb1 : ', len(hla_drb1)) #### DEBUG

## Close file
f.close()


# Using those Arrays of HLA alleles

# Loop N times
for i in range(N):
    # Select two random elements from each array
    a1, a2 = random.sample(hla_a, 2)
    b1, b2 = random.sample(hla_b, 2)
    dr1, dr2 = random.sample(hla_drb1, 2)

    # Print the pairs separated by commas
    print(f"P{i},{a1},{a2},{b1},{b2},{dr1},{dr2}")

