#!/bin/usr/python3

import sys, subprocess, shutil, os
import string, re

def check_valid(name):
	count = subprocess.check_output('esearch -db protein -query "{0}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(name),shell=True)
	if int(count) == 0:
		return 0
	return 1


def check_both_input(name,protein):
        count = subprocess.check_output('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(protein, name),shell=True)
        if int(count) == 0:
                return 0
        return 1


def check_input(name):
	valid = re.compile("[A-Za-z0-9- ]+") 
	if name.isdigit() == True or valid.fullmatch(name) == None:
		print("The name "+name+" is invalid. Special characters in name or name with only numbers are not welcomed!")
		return 0
	if check_valid(name) != 1:
		print("In database there is no imformation about "+name+". The name might have mispelling. Please try again!")
		return 0
	return 1

def get_input():     
	name = str(input("Please enter the taxonomic group name:\n"))
	while check_input(name) != 1:
		name = str(input("Enter the valid taxonomic group name:\n"))
	protein = str(input("Please specify protein family name:\n"))
	while check_input(protein) != 1:
		protein = str(input("Enter the valid protein name\n"))
	return (name, protein)

name, protein = get_input()
while check_both_input(name, protein) != 1:
	print("No data found with a taxonomic group name \""+name+"\" and protein family name \""+protein+"\" in database. Try one more time with the valid names!")
	name, protein = get_input()

rename = name.replace(" ","_")
reprotein = protein.replace(" ","_")

subprocess.call('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | efetch -db protein -format docsum | xtract -pattern DocumentSummary -element Organism > {2}_seq_species_{3}.txt'.format(protein, name, reprotein,rename), shell=True)
my_list = open('{0}_seq_species_{1}.txt'.format(reprotein, rename)).readlines()
count = len(my_list)
print(count)
spec_count = 43
#print('The search with your input resulted in '+str(count)+' sequences from '+str(spec_count)+' species. Do you want to continue the process or change the inout? y/n\n')
#subprocess.call('esearch -db protein -query "Aves AND glucose-6-phosphatase" | efetch -db protein -format gb > aves_gb.txt', shell=True)
#subprocess.call('esearch -db protein -query "Aves AND glucose-6-phosphatase" | efetch -db protein -format fasta > aves_acc.fasta', shell=True)
