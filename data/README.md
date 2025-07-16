## Overview
Add all .pcap files here. 
The extract script will auto-populate other folders on initial run.

In a nutshell:

Decoding Process and Output
Raw .pcap files are placed in the data folder.

extract.sh extracts raw payloads using tshark, saving them in data/tsharkOutput/.

Python script tshark_OutputParser.py cleans and parses payloads, outputting to data/payloadOutput/.

decoder.py decodes parsed payloads into readable CSV files stored in data/decodedOutput/.

This workflow separates extraction, parsing, and decoding into distinct steps with dedicated folders for easier management and clarity.
