#!/usr/bin/fish
# Install the requirements
echo '
set PATH $PATH:/home/dev/.local/bin
' >> /home/dev/.config/fish/config.fish

pip install -r src/requirements.txt

# Make the shell look nice :)
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
fisher install IlanCosman/tide@v6