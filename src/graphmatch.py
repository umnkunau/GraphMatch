#!/usr/bin/python3
##
## GraphMatch: a Python script to perform Patient/Donor matches through Alleles 
##             in support of stem cell transplants.
##
## Author: Timothy M. Kunau, kunau@umn.edu
## Version: 202309151015
##
## Note: requires Python >3.6.x for f-strings, and a collection of non-core libraries.
##

from neo4j import GraphDatabase
## from pandas import DataFrame
from iteration_utilities import duplicates, unique_everseen
import csv
import sys

## ENV file variable 
## .env at the root of the project directory
from decouple import config

GM_DEBUG           = config('GM_DEBUG')

GM_NEO4J_USER      = config('GM_NEO4J_USER')
GM_NEO4J_DB        = config('GM_NEO4J_DB')
GM_NEO4J_PASSWORD  = config('GM_NEO4J_PASSWORD')
GM_NEO4J_URI       = config('GM_NEO4J_URI')

if GM_DEBUG == 'True':
    print('#### GM_DEBUG:', GM_DEBUG)
    print('#### GM_NEO4J_USER', GM_NEO4J_USER)
    print('#### GM_NEO4J_DB', GM_NEO4J_DB)
    print('#### GM_NEO4J_PASSWORD', GM_NEO4J_PASSWORD)
    print('#### GM_NEO4J_URI', GM_NEO4J_URI)


## Parsing passed arguments (-f) and (-p)
import argparse

parser = argparse.ArgumentParser(
    prog='GraphMatch',
    description='Takes either a file (-f) of patients or a list of patients (-p) on the CLI and runs match reports.',
    epilog='(This work is offered as part of Timothy Kunau\'s disertation project, 20230903)')

## enter a file of patients to be serached from the CLI
parser.add_argument('-f', help='enter the path to the CSV file of PatientUIDs to match.')
## enter a patient_UID or multiples to be serached from the CLI
parser.add_argument('-p', help='enter a short list of PatientUIDs to match.')

args = parser.parse_args()

GM_SEARCHFILE = args.f
GM_SEARCHUIDS = args.p

if GM_DEBUG == 'True':
    print('#### GM_SEARCHFILE: ', GM_SEARCHFILE)
    print('#### GM_SEARCHUIDS: ', GM_SEARCHUIDS)


## Neo4j connection methods
class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

## Connection details
conn = Neo4jConnection(uri=GM_NEO4J_URI, user=GM_NEO4J_USER, pwd=GM_NEO4J_PASSWORD)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


#### START_LOOP: iterate through the patients and perform match searches

## Open the Patient list and use the first column as the test mmatches
with open(GM_SEARCHFILE, mode ='r')as import_file:
    # reading the CSV file
    csvFile = csv.reader(import_file)

    #### iterate through the patients and perform match searches
    # retrieve the patient ids for matching by iterating through the patient data file
    for line in csvFile:
        # copy the first item from the list
        PATIENT_ID = (line[0])

       ## Match Query: set up
        match_query_string = f'''
            MATCH (p:Patient)-[:HAS_ALLELE|HAS_DUPLICATE_ALLELE]->(a:Allele)
            MATCH (a:Allele)<-[:HAS_ALLELE|HAS_DUPLICATE_ALLELE]-(d:Donor)
            WHERE p.name = \'{PATIENT_ID}\'
        	WITH p,d, count(d) as degree, collect(a.name) as shared_alleles
        	WHERE degree > 3
        	RETURN  p.name, shared_alleles, d.name, degree ORDER BY degree DESC
        	LIMIT 10
        	''' 

        ## Match Query: execute
        match_results = conn.query(match_query_string, db=GM_NEO4J_DB)

        # Begin report for PATIENT_ID
        print('\n')              #### DEBUG
        sys.stdout.write(PATIENT_ID)
        sys.stdout.write(" ")

        # test for match results, if there are results then proceed to the rest of the queries
        # if there are no match results, then go on to the next patient
        if match_results is not None:

            # create a hashtag counter in a 'for loop' below to count the number 
            # of results (typically 1..10), creating a histogram with hashtags
            for count in match_results:
                sys.stdout.write("#")
            print('\n')              #### DEBUG

            ## Patient allele set
            ## retrive all Patient alleles from db
            patient_allele_query_string = f'''
                MATCH (p:Patient {{name: \"{PATIENT_ID}\" }})--(pa:Allele)
                RETURN collect(pa.name) AS pa_list
                '''
            ## Patient allele set Query: execute
            pa_results = conn.query(patient_allele_query_string, db='neo4j')
            ## create a list, by iterating over the results of the query
            pa_list = []

            for pa_record in pa_results:
                pa_list = pa_record['pa_list']

            ## Query: print the results to the limit specified above
            for record in match_results:
                ## retrive all Donor alleles from db
                ## d_unmatched_alleles = d_alleles - shared_alleles
                DONOR_ID = record['d.name']
                ## Patient allele set
                ## retrive all Patient alleles from db
                donor_allele_query_string = f'''
                    MATCH (d:Donor {{name: \"{DONOR_ID}\" }})--(da:Allele)
                    RETURN collect(da.name) AS da_list
                    '''
                ## Patient allele set Query: execute
                da_results = conn.query(donor_allele_query_string, db='neo4j')
                ## create a list, by iterating over the results of the query
                da_list = []
                for da_record in da_results:
                    da_list = da_record['da_list']

                ## Find mis-matched patient alleles: p_unmatched_alleles = pa_list - shared_alleles
                p_unmatched_alleles = (list(filter(lambda i: i not in record['shared_alleles'], pa_list)))

                ## Find mis-matched donor alleles: d_unmatched_alleles = da_list - shared_alleles
                d_unmatched_alleles = (list(filter(lambda i: i not in record['shared_alleles'], da_list)))

                ## delete the common alleles between Patient and Donor
                print(record['degree'], "|", p_unmatched_alleles, "|", record['p.name'], "|", record['shared_alleles'], "|", record['d.name'], "|", d_unmatched_alleles)

#### END_LOOP

## close the database connection
conn.close()

## Close file
import_file.close()