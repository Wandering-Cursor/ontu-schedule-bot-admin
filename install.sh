python3.11 -m pip install -r requirements.txt

file="./.env"
if [ ! -f $file ]; then
  echo "SECRET_KEY=DUMMY" >> $file
fi

cat $file
