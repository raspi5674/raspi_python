# This goes to the python git repository, updates the repository, and sends the email

cd ~/raspi_python
python3 -c 'import makeMorningEmail; makeMorningEmail.main()' | mail -s "Morning Data" mot5600@yahoo.com
cd ~
