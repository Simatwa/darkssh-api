#!/usr/bin/bash
export PATH="$PATH:/home/container/.local/bin"
DIR="darkssh-api"
if [[ -d "$DIR" ]]; then
   rm $DIR -rf
fi

git clone https://Simatwa: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@github.com/Simatwa/$DIR.git
cp .env $DIR
cd $DIR

pip install -U pip
pip install -r requirements.txt
python bot.py
#export smartbetsbot_config="$HOME/.config.json