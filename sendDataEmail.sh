# This code sends the data email

# Get to the repository directory where the python code resides
cd ~/raspi_python

# Call the python to generate the text of the email and store it in a temp file
python3 -c 'import makeDataEmail; print(makeDataEmail.main(True))' > tempMessage.txt

# Send the email
cat tempMessage.txt | mail -s "Daily Data" mot5600@yahoo.com

# Remove the temp file and go back to the home directory
rm tempMessage.txt
cd ~
