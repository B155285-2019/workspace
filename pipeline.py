#!/bin/usr/python3

import sys, subprocess, shutil, os
import string, re
import collections
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import OrderedDict

def error_msg():
	for i in range(20):
		print("==",end="")
	print("ERROR", end="")
	for i in range(20):
		print("==", end="")
	print("\n")
	return (0)
		

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
		error_msg()
		print("The name "+name+" is invalid. Special characters, Only numbers, Whitespaces starts strongly restricted!\n")
		return 0
	if check_valid(name) != 1:
		error_msg()
		print("In database there is no imformation about "+name+". The name might have mispelling. Please try again!\n")
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
		error_msg()
		print("No data found with a taxonomic group name \""+name+"\" and protein family name \""+protein+"\" in database. Try one more time with the valid names!\n")
		name, protein = get_input()
	rename = name.replace(" ","_")
	reprotein = protein.replace(" ","_")
	subprocess.call('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | efetch -db protein -format docsum | xtract -pattern DocumentSummary -element Organism > {2}_{3}_organism_list.txt'.format(protein, name, rename,reprotein), shell=True)
	my_list = open('{0}_{1}_organism_list.txt'.format(rename, reprotein)).readlines()
	count = len(my_list)
	species = len(set(my_list))
	print('The search with your input resulted in '+str(count)+' sequences from '+str(species)+' species.\n')
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
	os.remove("{0}_{1}_organism_list.txt".format(rename, reprotein))
	reply, name, protein = begin()
	
print("All sequences are being downloaded...")
rename = name.replace(" ","_")
reprotein = protein.replace(" ","_")
subprocess.call('esearch -db protein -query "{0}[prot] NOT PARTIAL" -organism "{1}" | efetch -db protein -format fasta > {2}_{3}.fasta'.format(protein, name, rename, reprotein), shell=True)
subprocess.call('clustalo -i {0}_{1}.fasta -o {0}_{1}_aln.fasta -v'.format(rename, reprotein), shell =True)
print("Multiple Alignment for downloaded protein sequences is done")
subprocess.call('cons -sequence {0}_{1}_aln.fasta -outseq {0}_{1}_consensus.fasta -auto'.format(rename, reprotein), shell=True)
print("Program has created a consensus sequence from a multiple alignment")

subprocess.call('makeblastdb -in {0}_{1}.fasta -dbtype prot -out {0}_{1}_db'. format(rename, reprotein), shell=True)
print("From all fasta sequences the program created database for blast alingment\n")
subprocess.call('blastp -db {0}_{1}_db -query {0}_{1}_consensus.fasta -outfmt 7 -max_hsps 1 > {0}_{1}_similarity_seq_blast.out'.format(rename, reprotein), shell = True)
print("Alighned all sequences in BLAST and their HSP score saved in new file\n")

blast_file = open("{0}_{1}_similarity_seq_blast.out".format(rename, reprotein)).read().rstrip('\n')
access_hsp = {}
data_lines = blast_file.split('\n')
for lines in data_lines:
	if re.search('#',lines):
		next
	else:
		data_tab = lines.split('\t')
		acc = data_tab[1]
		hsp = data_tab[11]
		access_hsp[acc] = hsp
access_hsp_ord = {}
access_hsp_ord=OrderedDict(sorted(access_hsp.items(), key=lambda value: value[1], reverse=True)[:250])

