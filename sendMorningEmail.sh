# This goes to the python git repository, updates the repository, and sends the email

cd ~/raspi_python
git pull origin master
python3 -c 'import makeMorningEmail; makeMorningEmail.main()' | mail -s "Morning Data" mot5600@yahoo.com
cd ~
