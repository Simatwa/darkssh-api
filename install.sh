#!/usr/bin/bash
export PATH="$PATH:/home/container/.local/bin"
DIR="darkssh-api"
if [[ -d "$DIR" ]]; then
   rm $DIR -rf
fi

git clone https://Simatwa:$GITHUB_TOKEN@github.com/Simatwa/$DIR.git
cp .env $DIR
cd $DIR

pip install -U pip
pip install -r requirements.txt
python bot.py
#export smartbetsbot_config="$HOME/.config.json