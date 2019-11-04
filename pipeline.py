#!/bin/usr/python3

import sys, subprocess, shutil, os
import string, re

def check_valid(name):
	count = subprocess.check_output('esearch -db protein -query {0} | xtract -pattern ENTREZ_DIRECT -element Count'.format(name),shell=True)
	if int(count) == 0:
		print("The inserted "+name+" is not valid name. Please try again!")
		return 0
	return 1


def get_input():
	valid = re.compile("[A-Za-z0-9-]+") 
	name = str(input("Please specify the taxonomic group:\n"))
	while name.isdigit() == True:
		print("Please enter a valid name!")
		name = str(input("Please specify the taxonomic group:\n"))
	if valid.fullmatch(name) == None:
		print(name+" not match")
#	while check_valid(name) != 1:
#		name = str(input("Please specify the taxonomic group:\n"))
	protein = str(input("Please specify protein family name:\n"))
	return (name,protein)

get_input()
#subprocess.call('esearch -db protein -query "Aves AND glucose-6-phosphatase" | efetch -db protein -format acc > aves_acc.txt', shell=True)
#subprocess.call('esearch -db protein -query "Aves AND glucose-6-phosphatase" | efetch -db protein -format gb > aves_gb.txt', shell=True)
#subprocess.call('esearch -db protein -query "Aves AND glucose-6-phosphatase" | efetch -db protein -format fasta > aves_acc.fasta', shell=True)
