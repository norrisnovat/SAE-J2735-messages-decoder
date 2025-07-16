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
