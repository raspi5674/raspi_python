#! /bin/bash

# This code sends the data email

# Get to the repository directory where the python code resides
cd ~/raspi_python

# Call the python to generate the text of the email and store it in a temp file
python3 -c 'import makeDataEmail; makeDataEmail.main(True)'

# Send the daily email
cat dailyMessage.txt | mail -s "Daily Data" mot5600@yahoo.com -A daily_img.png

# Send the weight challenge emails


# Remove the temp files and go back to the home directory
rm *.txt
rm *.png
cd ~
