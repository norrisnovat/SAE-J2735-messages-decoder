# SAE J2735 Message Decoder

## Overview  
These scripts decode SAE J2735 messages captured in `.pcap` files. While not every field is decoded by default, additional fields can be added easily by editing the `decoder.py` script. Originally designed to decode one message type from a single `.pcap` file, this repository has been enhanced to automatically process **all `.pcap` files** in the `data` directory, decoding one message type at a time across the dataset.

Users are encouraged to customize and extend the scripts to suit specific needs.

---

## Prerequisites

Before running the scripts, ensure the system is prepared with the necessary tools and libraries:

- **Python 3:**  
  ```bash
  sudo apt install python3
  ```
- **pip3:**  
  ```bash
  sudo apt install python3-pip
  ```
- **Wireshark:**  
  ```bash
  sudo add-apt-repository ppa:wireshark-dev/stable
  sudo apt-get update
  sudo apt-get -y install wireshark
  ```
- **Tshark (command-line tool for Wireshark):**  
  ```bash
  sudo apt-get -y install tshark
  ```
- **Python packages:**  
  ```bash
  pip3 install pycrate numpy
  ```

---

## Usage

1. **Place all `.pcap` files you wish to decode into the `data` folder.**

2. **Run the decoding script:**  
   ```bash
   cd extractPackets/src/
   bash extract.sh
   ```

3. **Follow the interactive prompts to specify the J2735 message type you want to decode.**  
   The script will then process all `.pcap` files found in the `data` directory for the selected message type.

4. **Output:**  
   Decoded message data will be saved as CSV files in:  
   `extractPackets/data/decodedOutput/`

---

## Notes

- The script currently processes one message type at a time but does so automatically for all `.pcap` files in the `data` directory, enabling efficient batch decoding.
- You may customize `decoder.py` to add or modify fields for your specific message types.
- Ensure proper permissions are set for Wireshark and tshark to capture and decode network data.

# Decoding Process and Output Files

## How Decoding Works

### Input `.pcap` Files:  
Place all raw `.pcap` capture files in the `data` folder. These files contain recorded vehicular communication messages.

### Payload Extraction:  
The bash script `extract.sh` uses `tshark` to read each `.pcap` file and extract raw payload data. Initially, it attempts to extract the payload as hexadecimal strings. If the message type is not found, it retries using ASCII extraction.

### Payload Parsing:  
Extracted raw payloads are parsed and cleaned using the Python script `tshark_OutputParser.py`. This step removes unnecessary bytes and formats the payload for decoding.

### Message Decoding:  
The cleaned payloads are then decoded by `decoder.py`, which interprets the payload according to the selected SAE J2735 message type (e.g., BSM, SPAT, MAP). The decoded data is written into human-readable CSV files.

---

## Output Folder Structure

- **`data/tsharkOutput/`**  
  Contains the raw extracted payload files from each `.pcap` file after running `tshark`. These files are intermediate outputs in hex or ASCII format.

- **`data/payloadOutput/`**  
  Stores the cleaned and parsed payload CSV files produced by `tshark_OutputParser.py`. These files have extraneous data removed and are ready for decoding.

- **`data/decodedOutput/`**  
  Contains the final decoded CSV files output by `decoder.py`. Each file corresponds to a decoded message type from a source `.pcap` file and contains human-readable columns with the extracted fields.
