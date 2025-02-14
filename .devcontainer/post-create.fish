#!/usr/bin/fish
# Install the requirements
set PATH $PATH:~/.local/bin

pip install -r src/requirements.txt

# Make the shell look nice :)
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
fisher install IlanCosman/tide@v6