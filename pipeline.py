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
#before printing error trps I print ERROR message in order to get attention of the user
def error_msg(): 			
	print('\n')
	for i in range(20):        #twenty times print **  before word, want no new line in the end, because need to print word
		print("**",end="")
	print("ERROR", end="")      #then print word ERROR without newline
	for i in range(20):         #twenty times print ** after word
		print("**", end="")  
	print("\n")     #newline in the end          
	return (0)     #function just returns 0

#in order to check if the input is valid name, I check that word in easearch and count the found data. This check separately done for both inputs		
def check_valid(name):     #input is any name
	#when you do esearch it print out ENTREZ_DIRECT, where you can find found data count, I try to save that value and check
	count = subprocess.check_output('esearch -db protein -query "{0}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(name),shell=True) 
	if int(count) == 0:      #if there is no data found thenfunctionss return 0 further it gaves error message to the user
		return 0
	return 1         #if there is at least one data found regarding to the user input we continue program
 
#now use both valid inpput names to check if there is data with that organism and with that protein names
def check_both_input(name,protein):   
	#saving as a value the Count data from esearch commamd output 
        count = subprocess.check_output('esearch -db protein -query "{0}[prot]" -organism "{1}" | xtract -pattern ENTREZ_DIRECT -element Count'.format(protein, name),shell=True)
        if int(count) == 0:       #if count 0 for input searched it means do data in the server iwth those inputs
                return 0	#to check function output it must return 0 when count 0
        return 1		#otherwise it return 1 for positive results

#this function for checking syntax errors and special characters then runs to esearch
def check_input(name):       #as an input we need one name
	valid = re.compile("[A-Za-z0-9- ]+")       #valid names can contain Upper or lower letters and numbers and space and dashes
	if name.isdigit() == True or valid.fullmatch(name) == None or re.search(r'^[\s\n\t]', name):      #error if there is only numbers or other special charaters or starts with sapce or tabs
		error_msg()     #calling error messaging  printing function
		print("The name "+name+" is invalid. Special characters, Only numbers, Whitespaces starts strongly restricted!\n")   #Explaining error for wrong input
		return 0     	#after finding error stops funciton and returns 0
	if check_valid(name) != 1:       #after checking for syntaxes, we call function which checks for esearch for valid data for that name, if it's not 1 then means count is 0
		error_msg()    #printing error msg          
		print("In database there is no imformation about "+name+". The name might have mispelling. Please try again!\n")  #Explaining the user the error   
		return 0      #after finding error stops funciton and returns 0  
	return 1  	#if all checking is correct then function returns 1

#if in the begining the inputs did not pass the checkings program ask for valid name
def get_input():     
	name = str(input("Please enter the taxonomic group name (No need for quotation!):\n"))    #asking to type the organism name
	while check_input(name) != 1: #until we dont get right input we call for function that checks syntax and in esearch combined
		name = str(input("Enter the valid taxonomic group name (No need for quotation):\n")) #if every input is wrong ask again for right input 
	protein = str(input("Please specify protein family name:\n")) #asking for protein name
	while check_input(protein) != 1:	  #until we dont get right input we call for function that checks syntax and in esearch combined	
		protein = str(input("Enter the valid protein name\n"))    #if every input is wrong ask again for right input
	return (name, protein)      #in the it returns the valid name for organism and protein

#before downloading all datas we run esearch with valid names and count all sequences and species after ask user if this what s/he wants
def begin(name, protein):   #need organism and protein name
	while check_both_input(name, protein) != 1:   #calling the function which ckeck for both names in esearch, until there is data for both input
		error_msg()		#calling function to print Error
		#Explaining the error message
		print("No data found with a taxonomic group name \""+name+"\" and protein family name \""+protein+"\" in database. Try one more time with the valid names!\n")
		name, protein = get_input()     #again going back, where we ask for inputs and check, then send here
	rename = name.replace(" ","_")     #if there is spaces in name I replace them to underscore in order to use it later for kaming file names
	reprotein = protein.replace(" ","_")  
	os.mkdir('{0}/{1}_{2}'.format(my_ws,rename, reprotein))   #By names with spaces replaced to undersocre, I make a folder for this run 
	os.chdir('{0}/{1}_{2}'.format(my_ws,rename, reprotein))  #Move to that folder, in order make it working directory
	#From all found Data about proteins sequenced for that taxonomic groups, first downloaded the organism list and save into file
	subprocess.call('esearch -db protein -query "{0}[prot]" -organism "{1}" | efetch -db protein -format docsum | xtract -pattern DocumentSummary -element Organism > {2}_{3}_organism_list.txt'.format(protein, name, rename,reprotein), shell=True)
	my_list = open('{0}_{1}_organism_list.txt'.format(rename, reprotein)).readlines()  #open organism list file and read by line saving it into array 
	count = len(my_list)    #length of read lines is organism numbers found
	species = len(set(my_list))  #founding unique in that list is for finding the number of species
	print('The search with your input resulted in '+str(count)+' sequences from '+str(species)+' species.\n')  #Telling the user about how many species are represented in the dataset chosen by user 
	if count >= 10000:    #this program does not allow to use the dataset with more than 10,000 sequences
		error_msg()    #calling Error printer function
		print("Allowable starting sequence set shouldn't be bigger than 10,000 sequences.\n")  
		reply = "BREAK"     #in this error case the function will return as BREAK
		return (reply, name, protein)    #it does not continue the program returns values
	reply = input('Do you want to continue the process with this dataset? (Otherwise you can stop it and run again with other inputs) yes/no\n').upper()  #otherwise program asks if user is satisfied with found dataset
	return (reply, name, protein)   #the user reply and organism and protein names transferred as output

############################### START #######################################################

arguments = len(sys.argv) - 1    #taking out the program name
if (arguments != 2):      #to check if user inputted two names only
        error_msg()      #calling error printer function
        print("You have to enter two arguments to run the program!Quote the Names which have spaces!\n")
        sys.exit("Number of arguments are not valid! Program is exiting!\n")       #exiting the program until user enters two names for search

name  = sys.argv[1]     #fisrt argument after the program name is taxonomic group name
protein = sys.argv[2]	#second argument after the program name is protein name
	
reply, name, protein = begin(name, protein)     #calling my function that checks and if valid downloads organism list and returns the user reply and valid organism and protein name
while not (re.search('[YES]|[Y]',reply)):      #if the user reply is other then Yes or Y, we are returning to the beginning 
	print("We are going back to the beginning!")
	rename = name.replace(" ","_")         #Since we dont return renamed names from previous functions, here we are doing it again  
	reprotein = protein.replace(" ","_")   #replacing spaces with underscores
	os.chdir('{0}'.format(my_ws))	       #going out of the folder which was created for this run
	shutil.rmtree('{0}/{1}_{2}'.format(my_ws,rename, reprotein))   #since user does not want to use this dataset we are deleting whole directory
	name, protein = get_input()            #getting new inputs
	reply, name, protein = begin(name,protein)  #calling function begin with new outputs, and inside while loop will check again for reply is yes gets out of the loop

#Okay now starting to Download fasta files
inside_dir = os.getcwd()	 #setting path of the folder with tax_group and protein name
print("All sequences are being downloaded...")      
rename = name.replace(" ","_")    #Since we dont return renamed names from previous functions, here we are doing it again
reprotein = protein.replace(" ","_")    #replacing spaces with underscores
#downloading fasta file with that orgainsm and protein name
subprocess.call('esearch -db protein -query "{0}[prot]" -organism "{1}" | efetch -db protein -format fasta > {2}_{3}.fasta'.format(protein, name, rename, reprotein), shell=True)    
#using clustalo to align all sequences
subprocess.call('clustalo -i {0}_{1}.fasta -o {0}_{1}_aln.fasta -v'.format(rename, reprotein), shell =True)
print("Multiple Alignment for downloaded protein sequences is done")

#Asking user if want to see the alignment result in pretty format
show_al = str(input("Do you want to visualize alignment results in pretty format? (y/n)\n"))
if (re.search('[YES]|[Y]',show_al)):    #for positive results we run prettyplot functin for aligned sequences
	subprocess.call('prettyplot -residuesperline=70 -boxcol -consensus -ratio=0.59 -docolour -sequence {0}_{1}_aln.fasta -graph svg'.format(rename,reprotein),shell=True)        #in each line wanted to 70 residues and, respresent residues and backgrounds in colors, for consensus match used 0.59 as pluraity ratio
	print("Emboss Prettyplot function used to draw the aligned sequences with pretty formating!\n")	
	subprocess.call('firefox prettyplot.svg&')   #need to open output in firefox since plot is large


#For conservation plotting we are using the most similar 250 sequences from dataset
#Running cons function from Emboss to create the consensus sequence from multiple alignment 
subprocess.call('cons -plurality 0.59 -sequence {0}_{1}_aln.fasta -outseq {0}_{1}_consensus.fasta -auto'.format(rename, reprotein), shell=True)   #used same prularity as for pretty plot in order to have same consensus sequence and it should ne a bit more than half of the total sequence weighting 0.59
print("Program has created a consensus sequence from a multiple alignment")

#We can get most similar sequences by running the blastp
#before running we are creating a database from all sequences
subprocess.call('makeblastdb -in {0}_{1}.fasta -dbtype prot -out {0}_{1}_db'.format(rename, reprotein), shell=True)
print("From all fasta sequences the program created database for blast alingment\n")
#After running the blast programgram with database and created consensus sequence
subprocess.call('blastp -db {0}_{1}_db -query {0}_{1}_consensus.fasta -outfmt 7 -max_hsps 1 > {0}_{1}_similarity_seq_blast.out'.format(rename, reprotein), shell = True)   #outformat wanted with tabs and comments, per each query and subject sequences we want only one HSPs 
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
for item in second_files:
	keys = item.replace("_fasta.garnier","")
	sec_file = open("{0}/{1}".format(sec_str,item)).read().rstrip()
	m = re.search(r"percent: H: (\d+.\d+) E: (\d+.\d+) T: (\d+.\d+) C: (\d+.\d+)",sec_file)
	H[keys] = m.group(1)
	E[keys] = m.group(2)
	T[keys] = m.group(3)
	C[keys] = m.group(4)

table = open("{0}/Secondary_struct_percent_table.txt".format(inside_dir), "w")
table.write("Accession numbers\tHelix %\tSheet %\tTurns %\tcoils %\n")
for key in H.keys():
        table.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(key,H[key],E[key],T[key],C[key]))
table.close()

S = pd.read_csv("{0}/Secondary_struct_percent_table.txt".format(inside_dir), sep = "\t")
S.plot(figsize=(12,12))
plt.xlabel('Sequence numbers')
plt.ylabel('Percentage')
plt.title('Secondary structure Residue Percentage in Protein sequence dataset')
plt.savefig("{0}/Secondary_struct_profile_plot.png".format(inside_dir), transparent=True)
plt.show()
