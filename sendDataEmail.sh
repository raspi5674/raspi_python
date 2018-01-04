# This code sends the data email

# Get to the repository directory where the python code resides
cd ~/raspi_python

# Call the python to generate the text of the email and store it in a temp file
python3 -c 'import makeMorningEmail; makeMorningEmail.main()' > tempMessage.txt

# Log the date/time of the message and add the message to the log
date +'%Y-%m-%d %H:%M' >> /home/pi/logging/data_email_log.txt
cat tempMessage.txt >> /home/pi/logging/data_email_log.txt

# Send the email
cat tempMessage.txt | mail -s "Morning Data" mot5600@yahoo.com

# Remove the temp file and go back to the home directory
rm tempMessage.txt
cd ~
