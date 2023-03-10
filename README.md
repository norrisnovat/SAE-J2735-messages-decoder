## Overview
These scripts decode SAE J2735 messages. Not every field is decoded, but desired fields can easily be added in the decoder.py script. 
The scripts are meant to decode only one message type at time from one .pcap file. However, they may be edited to decode every message type within a file.
Feel free to make your own changes!

## Prerequisites:
* python3:   `sudo apt install python3`
* pip3:      `sudo apt install python3-pip`
* wireshark: `sudo apt-get install wireshark`
* pycrate:   `pip3 install pycrate`
* numpy:     `pip3 install numpy`

## Usage
Save all pcap files in data folder.

1. Run:
	```
	$ cd extractPackets/src/
	$ bash extract.sh
	```

2. Follow the prompts to decode your desired files and message types.
3. Decoded messages will be found in the .csv files in extractPackets/data/decodedOutput/