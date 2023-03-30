python3.11 -m pip install -r requirements.txt

file="./.env"
echo "SECRET_KEY=DUMMY" >> file
cat $file
