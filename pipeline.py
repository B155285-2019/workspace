#!/bin/usr/python3

import sys, subprocess, shutil, os
import string, re
import collections
import numpy as np

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
	if name.isdigit() == True or valid.fullmatch(name) == None or re.search(r'^[\s\n\t]', name):
		print("The name "+name+" is invalid. Special characters or name with only numbers or name starting with whitespaces are not welcomed!")
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


def begin():
	name, protein = get_input()
	while check_both_input(name, protein) != 1:
		print("No data found with a taxonomic group name \""+name+"\" and protein family name \""+protein+"\" in database. Try one more time with the valid names!")
		name, protein = get_input()
	rename = name.replace(" ","_")
	reprotein = protein.replace(" ","_")
	subprocess.call('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | efetch -db protein -format docsum | xtract -pattern DocumentSummary -element Organism > {2}_seq_species_{3}.txt'.format(protein, name, reprotein,rename), shell=True)
	my_list = open('{0}_seq_species_{1}.txt'.format(reprotein, rename)).readlines()
	count = len(my_list)
	species = len(set(my_list))
	print('The search with your input resulted in '+str(count)+' sequences from '+str(species)+' species.')
	reply = input('Do you want to continue the process or change the input? yes/no\n').upper()
	return (reply, name, protein)

#def unique(list1): 
#    unique_list = [] 
#    for x in list1: 
#        if x not in unique_list: 
#            unique_list.append(x) 
#    print(len(unique_list)) 

#organism_dict = {}
#    for seq in my_list:
#      if not organism_dict.get(seq):
#        seq.strip()
#        organism[seq] = 1
reply, name, protein = begin()
while not (re.search('[YES]|[Y]',reply)):
	print("We are going back to the beginning!")
	rename = name.replace(" ","_")
	reprotein = protein.replace(" ","_")
	os.remove("{0}_seq_species_{1}.txt".format(reprotein, rename))
	reply, name, protein = begin()
	
print("All sequences are being downloaded...")
rename = name.replace(" ","_")
reprotein = protein.replace(" ","_")
subprocess.call('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | efetch -db protein -format fasta > {2}_{3}.fasta'.format(protein, name, reprotein, rename), shell=True)
