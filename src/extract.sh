#!/bin/bash

#this takes the location of the executed script as opposed to the current location
#this allows it to be run anywhere
directory="`dirname \"$0\"`"
directory="`( cd \"$directory\" && cd ../ && pwd )`"
cd $directory

mkdir -p data
cd data
mkdir -p tsharkOutput
mkdir -p payloadOutput
mkdir -p decodedOutput

cd $directory

printf "\nWhat type of J2735 message was captured?\n"
printf "MAP\nSPAT\nBSM\nPSM\nMobility\nTraffic Control\n\n"
IFS= read -r message_type

if [ "$message_type" == "MAP" ]; then
	message_type_id=0012
elif [ "$message_type" == "SPAT" ]; then
	message_type_id=0013
elif [ "$message_type" == "BSM" ]; then
	message_type_id=0014
elif [ "$message_type" == "PSM" ]; then
	message_type_id=0020
elif [ "$message_type" == "Mobility" ]; then
	printf "\nRequest, Response, Path, or Operation?\n"
	read message_second
	if [ $message_second == "Request" ]; then
		message_type_id=00f0
	elif [ $message_second == "Response" ]; then
		message_type_id=00f1
	elif [ $message_second == "Path" ]; then	
		message_type_id=00f2
	elif [ $message_second == "Operation" ]; then
		message_type_id=00f3
	else 
		echo "Invalid J2735 message type..."
		exit
	fi
	message_type+=" $message_second"
elif [ "$message_type" == "Traffic Control" ]; then
	echo "Request or Message?"
	read message_second
	if [ $message_second == "Request" ]; then
		message_type_id=00f4
	elif [ $message_second == "Message" ]; then	
		message_type_id=00f5
	else 
		echo "Invalid J2735 message type..."
		exit
	fi
	message_type+=" $message_second"
else echo "Invalid J2735 message type..."
	exit
fi

payloadType="hex"
messageTypeIdFound=false

searchForMessageTypeIdInFile(){
fileToCheck=$1
messageTypeIdToFind=$2
numPacketsToCheck=$3
messageTypeIdFound=false

echo
#check the first 10 packets for the desired message type ID
for (( c=1; c<=$numPacketsToCheck; c++ ))
do
	currentPayload=$(sed '$cq;d' $fileToCheck | awk -F ',' '{print $2}')
#id=int(sys.argv[2])
	if [[ "$currentPayload" == *"$messageTypeIdToFind"* ]]; then
		messageTypeIdFound=true
		echo "Found desired message ID ($messageTypeIdToFind) in packet $c"
		#echo $currentPayload
		break
	fi
done
}


extractPackets(){ 
echo
cd $directory/data
ls *.pcap
echo 

while true; do
	read -rep "Input filename from list: " file_to_read
	file_to_write="${file_to_read//pcap/csv}"
	if [ ! -f $file_to_read ]; then
		echo "File not found!"
	else
		break
	fi
done

tshark -r $file_to_read --disable-protocol wsmp -Tfields -Eseparator=, -e frame.time_epoch -e data.data > $directory/data/tsharkOutput/$file_to_write

searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10

if [ $messageTypeIdFound == true ]; then
        # The first packet contains the message id
        printf "\nSuccessfully decoded pcap into hex payloads\n"
        payloadType="hex"
else
        # The first packet does not contain the message id. This is most likely becuase payload is contained in ASCII
        printf "\nCould not find message ID in hex decoded payloads, trying ascii\n"
        tshark -r $file_to_read -o data.show_as_text:TRUE --disable-protocol wsmp -T fields -E separator=, -e frame.time_epoch -e data.text > $directory/data/tsharkOutput/$file_to_write
        payloadType="ascii"
        
        searchForMessageTypeIdInFile $directory/data/tsharkOutput/$file_to_write $message_type_id 10
        
        if [ $messageTypeIdFound ]; then
        	printf "\nSuccessfully decoded pcap into ascii payloads\n\n"
        else
        	printf "\nDecoding in ascii still resulted in an empty file, exiting...\n"
        	exit
        fi
        
fi 
}


getPayload(){
  cd $directory/data/tsharkOutput
  #parse tshark output to get rid of unnecessary bytes in front of payloads
  for i in *
  do
    python3 $directory/src/tshark_OutputParser.py $i $message_type $payloadType
  done
  mv *_payload.csv $directory/data/payloadOutput
}


decodePackets(){
  cd $directory/data/payloadOutput
  printf 'Decoding...\n'
  for i in $(find . -name "*.csv")
  do
    file=$(basename -- "$i")
    fileName="decoded_${file%.*}.csv"
	echo "$fileName"
    python3 $directory/src/decoder.py $i ${fileName} "$message_type" $message_type_id
  done

  mv *decoded* $directory/data/decodedOutput
  printf 'Complete.\n'
}


processing(){
  extractPackets
  getPayload
  decodePackets
}

processing
