import subprocess

class BlastAnnot():
	
	def __init__(self, blast_dict):
		self.blast_dict = blast_dict
		self.seq_ids = blast_dict.keys()
	
	
	# get species name
	def get_spec_name(self, seq_id):
		return self.blast_dict[seq_id][0]
	
	
	# get alignment start position of subject seq
	def get_sstart(self, seq_id):
		return int(self.blast_dict[seq_id][1])
	
	
	# get alignment end position of subject seq
	def get_send(self, seq_id):
		return int(self.blast_dict[seq_id][2])
	
	
	# get evalue
	def get_evalue(self, seq_id):
		return int(self.blast_dict[seq_id][3])
	
	
	# get subject nucl alignment seq w/o gaps
	def get_nucl_sseq(self, seq_id):
		return self.blast_dict[seq_id][4]
	
	
	# get alignment start position of query seq
	def get_qstart(self, seq_id):
		return int(self.blast_dict[seq_id][5])
	
	
	# get alignment end position of query seq
	def get_qend(self, seq_id):
		return int(self.blast_dict[seq_id][6])
	
	
	# get length of alignment
	def get_length(self, seq_id):
		return int(self.blast_dict[seq_id][7])
	
	
	# get number of mismatches in alignment
	def get_num_mismatch(self, seq_id):
		return int(self.blast_dict[seq_id][8])
	
	
	# get number of gaps in alignment
	def get_tot_num_gaps(self, seq_id):
		return int(self.blast_dict[seq_id][9])
	
	
	# get query alignment seq w/ gaps
	def get_qseq(self, seq_id):
		return self.blast_dict[seq_id][10]
	
	
	# get subject alignment seq w/ gaps
	def get_sseq(self, seq_id):
		return self.blast_dict[seq_id][11]
	
	
	# get subject frame
	def get_sframe(self, seq_id):
		return int(self.blast_dict[seq_id][12])
	
	
	# get subject strand
	def get_sstrand(self, seq_id, db, mode):
		db_info = subprocess.run("blastdbcmd -db {0} -entry {1} -strand {2}".format(db, seq_id, mode).split(), capture_output=True, text=True).stdout.split("\n")
		return ''.join(db_info[1:-1])
	
	
	# get num of gaps in query sequence
	def query_sig_gaps(self, seq_id):
		seq = self.get_qseq(seq_id)
		if "----------" in seq:
			return True
		else:
			return False

	# filter sequences into those w/ gaps and those w/o gaps
	def process_seqs(self):
		no_gap_dict = {}
		gap_dict = {}

		for seq_id in self.seq_ids:
			sig_gaps = self.query_sig_gaps(seq_id)
			if sig_gaps is True:
				gap_dict[seq_id] = self.blast_dict[seq_id]
			else:
				no_gap_dict[seq_id] = self.blast_dict[seq_id]

		return no_gap_dict, gap_dict

	# find 5' and 3' stop codons, find first start codon starting from 5' stop codon
	def find_codons(self, seq_id, db):
		start_codon = "ATG"
		stop_codons = ["TAG", "TAA", "TGA"]
		frame = self.get_sframe(seq_id)
		start_posit = self.get_sstart(seq_id)
		end_posit = self.get_send(seq_id)
		curr_fiv_posit = start_posit 
		curr_thr_posit = end_posit
		curr_start_posit = None
		mode = ''
		whole_strand = ''
		stop_five = None
		stop_three = None
		start = None
		length = None
		codon = ''
		
		if frame > 0:
			mode = "plus"
			whole_strand = self.get_sstrand(seq_id, db, mode)
			length = len(whole_strand)
			
			# find stop codon in 3' direction
			while True:
				if curr_thr_posit + 3 > length:
					stop_three = curr_thr_posit + 1
					break
					
				codon = whole_strand[curr_thr_posit:curr_thr_posit+3]
				
				if codon.upper() in stop_codons:
					stop_three = curr_thr_posit + 1
					break
					
				curr_thr_posit += 3			
			
			# find stop codon in 5' direction
			while True:
				if curr_fiv_posit - 4 < 0:
					stop_five = abs(frame)
					break
					
				curr_fiv_posit -= 1
				codon = whole_strand[curr_fiv_posit-3:curr_fiv_posit]
				curr_fiv_posit += 1
				curr_fiv_posit -= 3
			
				if codon.upper() in stop_codons:
					stop_five = curr_fiv_posit
					break
					
			# find start codon 
			if stop_five is not None:
				curr_start_posit = stop_five + 2
				while True:
					if curr_start_posit >= stop_three:
						break

					codon = whole_strand[curr_start_posit:curr_start_posit+3]

					if codon.upper() == start_codon:
						start = curr_start_posit + 1
						break

					curr_start_posit += 3
				
		else:
			mode = "minus"	
			# need to flip sequence since blast gives positions in 3'-5' but sequence in 5'-3'
			whole_strand = self.get_sstrand(seq_id, db, mode)[::-1]
			length = len(whole_strand)
			
			# find stop codon in 3' direction
			while True:
				if curr_thr_posit - 4 < 0:
					stop_three = abs(frame)
					break
				
				# flip sequence back to 5'-3'
				curr_thr_posit -= 1
				codon = whole_strand[curr_thr_posit - 3:curr_thr_posit][::-1]
				curr_thr_posit += 1
				
				if codon.upper() in stop_codons:
					stop_three = curr_thr_posit - 3
					break

				curr_thr_posit -= 3		
			
			# find stop codon in 5' direction
			while True:
				if curr_fiv_posit + 3 > length:
					stop_five = curr_fiv_posit - 2
					break
					
				# flip sequence back to 5'-3'
				codon = whole_strand[curr_fiv_posit:curr_fiv_posit + 3][::-1]
			
				if codon.upper() in stop_codons:
					stop_five = curr_fiv_posit + 1
					break
					
				curr_fiv_posit += 3
				
			# find start codon 
			if stop_five is not None:
				curr_start_posit = stop_five - 4
				while True:
					if curr_start_posit <= stop_three:
						break

					codon = whole_strand[curr_start_posit-3:curr_start_posit][::-1]

					if codon.upper() == start_codon:
						start = curr_start_posit - 2
						break

					curr_start_posit -= 3
		
		return stop_five, start, stop_three
	
	
	# annotate stop and start codons for all seqs in no_gap
	def annotate_no_gaps(self, no_gap_dict, db):
		annotated_seqs = {}
		no_start_codons = []

		for seq_id in no_gap_dict.keys():
			
			stop_five, start, stop_three = self.find_codons(seq_id, db)
		
			if start is not None:
				spec_name = self.get_spec_name(seq_id)
				db_info = None
				frame = self.get_sframe(seq_id)

				if frame > 0:
					stop_three = stop_three - 1

					db_info = subprocess.run("blastdbcmd -db {0} -entry {1} -strand plus -range {2}-{3}".format(db, seq_id, start, stop_three).split(), capture_output=True, text=True).stdout.split("\n")
				else:
					stop_three = stop_three + 3
					start = start + 2

					db_info = subprocess.run("blastdbcmd -db {0} -entry {1} -strand minus -range {2}-{3}".format(db, seq_id, stop_three, start).split(), capture_output=True, text=True).stdout.split("\n")		

				seq = ''.join(db_info[1:-1])

				annotated_seqs[seq_id] = [spec_name, start, stop_three, frame, seq]
				
			else:
				no_start_codons.append(seq_id)

		return annotated_seqs, no_start_codons

	# move seq to manual annotation dict if no start codon is found
	def update_gap_dicts(self, no_start_codons, no_gap_dict, gap_dict):
		if len(no_start_codons) > 0:
			for seq_id in no_start_codons:
				gap_dict[seq_id] = no_gap_dict[seq_id]
				del no_gap_dict[seq_id]

