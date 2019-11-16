#!/bin/usr/python3

import sys, subprocess, shutil, os
import string, re
import collections
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import OrderedDict

my_ws = os.getcwd()     #to get the path of working space

################################# FUNCTIONS ################################
def error_msg():
	print('\n')
	for i in range(20):
		print("**",end="")
	print("ERROR", end="")
	for i in range(20):
		print("**", end="")
	print("\n")
	return (0)
		
def check_valid(name):
	count = subprocess.check_output('esearch -db protein -query "{0}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(name),shell=True)
	if int(count) == 0:
		return 0
	return 1

def check_both_input(name,protein):
        count = subprocess.check_output('esearch -db protein -query "{0}[prot]" -organism "{1}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(protein, name),shell=True)
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
	name = str(input("Please enter the taxonomic group name (No need for quotation!):\n"))
	while check_input(name) != 1:
		name = str(input("Enter the valid taxonomic group name (No need for quotation):\n"))
	protein = str(input("Please specify protein family name:\n"))
	while check_input(protein) != 1:
		protein = str(input("Enter the valid protein name\n"))
	return (name, protein)

def begin(name, protein):
	while check_both_input(name, protein) != 1:
		error_msg()
		print("No data found with a taxonomic group name \""+name+"\" and protein family name \""+protein+"\" in database. Try one more time with the valid names!\n")
		name, protein = get_input()
	rename = name.replace(" ","_")
	reprotein = protein.replace(" ","_")
	os.mkdir('{0}/{1}_{2}'.format(my_ws,rename, reprotein))
	os.chdir('{0}/{1}_{2}'.format(my_ws,rename, reprotein))
	subprocess.call('esearch -db protein -query "{0}[prot]" -organism "{1}" | efetch -db protein -format docsum | xtract -pattern DocumentSummary -element Organism > {2}_{3}_organism_list.txt'.format(protein, name, rename,reprotein), shell=True)
	my_list = open('{0}_{1}_organism_list.txt'.format(rename, reprotein)).readlines()
	count = len(my_list)
	species = len(set(my_list))
	print('The search with your input resulted in '+str(count)+' sequences from '+str(species)+' species.\n')
	if count >= 10000:
		error_msg()
		print("Allowable starting sequence set shouldn't be bigger than 10,000 sequences.\n")
		reply = "BREAK"
		return (reply, name, protein)
	reply = input('Do you want to continue the process or change the input? yes/no\n').upper()
	return (reply, name, protein)

############################### START #######################################################

arguments = len(sys.argv) - 1    #taking out the program name
if (arguments != 2):
        error_msg()
        print("You have to enter two arguments to run the program!Quote the Names which have spaces!\n")
        sys.exit("Number of arguments are not valid! Program is exiting!\n")       #exiting the program until user enters two names for search

name  = sys.argv[1]     #Please for inputs with spaces with quotation
protein = sys.argv[2]
	
reply, name, protein = begin(name, protein)
while not (re.search('[YES]|[Y]',reply)):
	print("We are going back to the beginning!")
	rename = name.replace(" ","_")
	reprotein = protein.replace(" ","_")
	os.chdir('{0}'.format(my_ws))
	shutil.rmtree('{0}/{1}_{2}'.format(my_ws,rename, reprotein))
	name, protein = get_input()
	reply, name, protein = begin(name,protein)

inside_dir = os.getcwd()	
print("All sequences are being downloaded...")
rename = name.replace(" ","_")
reprotein = protein.replace(" ","_")
subprocess.call('esearch -db protein -query "{0}[prot]" -organism "{1}" | efetch -db protein -format fasta > {2}_{3}.fasta'.format(protein, name, rename, reprotein), shell=True)
subprocess.call('clustalo -i {0}_{1}.fasta -o {0}_{1}_aln.fasta -v'.format(rename, reprotein), shell =True)
print("Multiple Alignment for downloaded protein sequences is done")
#subprocess.call('showalign ')
#S (Similarity to the reference sequence)
subprocess.call('cons -sequence {0}_{1}_aln.fasta -outseq {0}_{1}_consensus.fasta -auto'.format(rename, reprotein), shell=True)
print("Program has created a consensus sequence from a multiple alignment")

subprocess.call('makeblastdb -in {0}_{1}.fasta -dbtype prot -out {0}_{1}_db'.format(rename, reprotein), shell=True)
print("From all fasta sequences the program created database for blast alingment\n")
subprocess.call('blastp -db {0}_{1}_db -query {0}_{1}_consensus.fasta -outfmt 7 -max_hsps 1 > {0}_{1}_similarity_seq_blast.out'.format(rename, reprotein), shell = True)
print("Alighned all sequences in BLAST and their HSP score saved in new file\n")

blast_file = open("{0}/{1}_{2}_similarity_seq_blast.out".format(inside_dir,rename, reprotein)).read().rstrip('\n')
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
acc_list_file = open("acc_filt_header.txt", "w")
acc_list_file.write("\n".join(access_hsp_ord.keys()))
acc_list_file.close()
subprocess.call('/localdisk/data/BPSM/Assignment2/pullseq -i {0}_{1}_aln.fasta -n acc_filt_header.txt -v > similar_aln_seq_250.fasta'.format(rename, reprotein), shell=True)

#insert window size for plotting
subprocess.call('plotcon -sequence similar_aln_seq_250.fasta -winsize 60 -graph svg', shell=True)
subprocess.call('eog plotcon.svg&', shell = True)    #'eog' used for presenting output to the screen and '&' sign used so that program continues its funtion further, while action of presenting figure taking place in the behind of main program


#for calling my files I need to put accession numbers as a name for each files
fasta_all = open("{0}_{1}.fasta".format(rename, reprotein)).read().rstrip()
os.mkdir('{0}/FASTA_FILES'.format(inside_dir))
os.chdir('{0}/FASTA_FILES'.format(inside_dir))
pat_out = ('{0}/PATMOTIFS_OUT'.format(inside_dir))
os.mkdir(pat_out)
found_motif = open('{0}/FOUND_MOTIFS.txt'.format(inside_dir),"w")
found_motif.write("Accession number\tMotif name\n")
motif_array = []
each_seq = fasta_all.split(">")
for seq in each_seq:
	for keys in access_hsp.keys():
		if re.match(keys, seq):
			sep_file = open("{0}.fasta".format(keys), "w")
			sep_file.write(">"+seq)
			sep_file.close()
			subprocess.call("patmatmotifs -sequence {0}.fasta -outfile {1}/{0}.patmatmotifs -full".format(keys, pat_out), shell=True)
			pat_file = open("{0}/{1}.patmatmotifs".format(pat_out, keys)).readlines()
			for line in pat_file:
				if re.search('#',line):
					next
				elif re.search('Motif', line):
					line.rstrip()
					index = line.find("=")
					motif = line[index+2:]
					motif_array.append(motif)
					found_motif.write('{0}\t{1}'.format(keys,motif))
found_motif.close()
print("The output of all sequences' scanning for motifs from the PROSITE database are saved in the folder by name PATMOTIFS_OUT inside the  working directory\n")
print("In subset of protein sequences {0} known motifs were associated with {1} protein sequences. In FOUND_MOTIFS.txt file you can find list of accesiion numbers with found motif names\n".format(len(set(motif_array)),len(motif_array)))
print("Found MOTIF names are: ")
print("\n".join(set(motif_array)))

fasta_files = os.listdir()
sec_str = ('{0}/Secondary_STRUCT'.format(inside_dir))
os.mkdir(sec_str)
H = {}
E = {}
T = {}
C = {}
for item in fasta_files:
	reitem = item.replace(".fasta","_fasta")
	subprocess.call("garnier -sequence {0} -outfile {1}/{2}.garnier".format(item,sec_str,reitem), shell=True)
second_files = os.listdir('{0}'.format(sec_str))
print(second_files)
for item in second_files:
	keys = item.replace("_fasta.garnier","")
	sec_file = open("{0}/{1}".format(sec_str,item)).read().rstrip()
	m = re.search(r"percent: H: (\d+.\d+) E: (\d+.\d+) T: (\d+.\d+) C: (\d+.\d+)",sec_file)
	H[keys] = m.group(1)
	E[keys] = m.group(2)
	T[keys] = m.group(3)
	C[keys] = m.group(4)

S = pd.DataFrame([H,E,T,C])
S.plot.barh()
plt.show()
print(S)
#S.to_csv("secondary.txt", sep="\t")
