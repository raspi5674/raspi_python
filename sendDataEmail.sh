# This code sends the data email

# Get to the repository directory where the python code resides
cd ~/raspi_python

# Call the python to generate the text of the email and store it in a temp file
python3 -c 'import makeDataEmail, os; print(makeDataEmail.main(True, os.getcwd()))' > tempMessage.txt

# Send the email
cat tempMessage.txt | mail -s "Daily Data" mot5600@yahoo.com -A daily_img.png

# Remove the temp files and go back to the home directory
rm tempMessage.txt
rm daily_img.png
cd ~
