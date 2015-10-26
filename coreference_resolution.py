#!/usr/bin/env python
# -*- coding: utf8 -*-

""" Entity coreference resolution system for the CLIN26 Shared Task.
Based on the Stanford Coreference Resolution system. Requires CoNLL-formatted
input data and Alpino pars in xml as input, gives CoNLL-formatted output. """

import argparse, copy
from utils import *
from mentionDetection import mentionDetection
from sieveDummy import sieveDummy
from sieveHeadMatch import sieveHeadMatch
from sieveStringMatch import sieveStringMatch

def main(input_file, output_file, doc_tags, verbosity):
	num_sentences = 9999 # Maximum number of sentences for which to read in parses
	# Read input files
	try:
		conll_list, num_sentences = read_conll_file(input_file)
	except IOError:
		print 'CoNLL input file not found: %s' % (input_file)
	xml_tree_list = read_xml_parse_files(input_file)[:num_sentences]
	if verbosity == 'high':
		print 'Number of sentences found: %d' % (num_sentences)
		print 'Number of xml parse trees used: %d' % (len(xml_tree_list))
	sentenceDict = {} # Initialize dictionary containing sentence strings
	# Do mention detection, give back 3 global variables:
	## mention_id_list contains list of mention IDs in right order, for traversing in sieves
	## mention_dict contains the actual mentions, format: {id: Mention}
	## cluster_dict contains all clusters, in a dict
	mention_id_list, mention_dict = mentionDetection(conll_list, xml_tree_list, input_file, verbosity, sentenceDict)
	if verbosity == 'high':
		print 'OUR MENTION OUTPUT:'
		print_mentions_inline(sentenceDict, mention_id_list, mention_dict)
		print 'MENTION DETECTION OUTPUT VS. GOLD STANDARD:'
		print_mention_analysis_inline(conll_list, sentenceDict, mention_id_list, mention_dict)								
	cluster_dict, cluster_id_list, mention_dict = initialize_clusters(mention_dict, mention_id_list)
	## APPLY SIEVES HERE
	## string matching sieve(s) (sieve 2, sieve 3)
	old_mention_dict = copy.deepcopy(mention_dict) # Store to print changes afterwards
	mention_id_list, mention_dict, cluster_dict, cluster_id_list = \
		sieveStringMatch(mention_id_list, mention_dict, cluster_dict, cluster_id_list, verbosity)
	if verbosity == 'high':
		print_linked_mentions(old_mention_dict, mention_id_list, mention_dict, sentenceDict) # Print changes
	## strictest head matching sieve (sieve 5)	
	old_mention_dict = copy.deepcopy(mention_dict) # Store to print changes afterwards
	mention_id_list, mention_dict, cluster_dict, cluster_id_list = \
		sieveHeadMatch(mention_id_list, mention_dict, cluster_dict, cluster_id_list, 3, verbosity)
	if verbosity == 'high':
		print_linked_mentions(old_mention_dict, mention_id_list, mention_dict, sentenceDict) # Print changes
	## more relaxed head matching sieve (sieve 6)
	old_mention_dict = copy.deepcopy(mention_dict) # Store to print changes afterwards
	mention_id_list, mention_dict, cluster_dict, cluster_id_list = \
		sieveHeadMatch(mention_id_list, mention_dict, cluster_dict, cluster_id_list, 2, verbosity)
	if verbosity == 'high':		
		print_linked_mentions(old_mention_dict, mention_id_list, mention_dict, sentenceDict) # Print changes
	## even more relaxed head matching sieve (sieve 7)
	old_mention_dict = copy.deepcopy(mention_dict) # Store to print changes afterwards
	mention_id_list, mention_dict, cluster_dict, cluster_id_list = \
		sieveHeadMatch(mention_id_list, mention_dict, cluster_dict, cluster_id_list, 1, verbosity)
	if verbosity == 'high':		
		print_linked_mentions(old_mention_dict, mention_id_list, mention_dict, sentenceDict) # Print changes
	## most relaxed head matching sieve (sieve 9)
	old_mention_dict = copy.deepcopy(mention_dict) # Store to print changes afterwards
	mention_id_list, mention_dict, cluster_dict, cluster_id_list = \
		sieveHeadMatch(mention_id_list, mention_dict, cluster_dict, cluster_id_list, 0, verbosity)
	if verbosity == 'high':		
		print_linked_mentions(old_mention_dict, mention_id_list, mention_dict, sentenceDict) # Print changes			
	## Generate output
	generate_conll(input_file, output_file, doc_tags, sentenceDict, mention_dict)

if __name__ == '__main__':
	# Parse input arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', type=str, help='Path to a file, in .conll format, to be resolved')
	parser.add_argument('output_file', type = str, help = 'The path of where the output should go, e.g. WR77.xml.coref')
	parser.add_argument('--docTags', help = 'If this flag is given, a begin and end document is printed at first and last line of output', dest = 'doc_tags', action = 'store_true')
	args = parser.parse_args()
	main(args.input_file, args.output_file, args.doc_tags, verbosity)

