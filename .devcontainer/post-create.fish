#!/usr/bin/fish
# Install the requirements
echo '
set PATH $PATH:/home/dev/.local/bin
' >> /home/dev/.config/fish/config.fish

set PATH $PATH:/home/dev/.local/bin

pip install -r src/requirements-dev.txt
pip install -r src/requirements.txt

# install NPM packages and minify the scripts
npm install 
fish .utils_dev/build_js.fish

# Make the shell look nice :)
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
fisher install IlanCosman/tide@v6

# tell the user to input their git credentials
echo "
Don't forget to update your git credentials! Use the following commands to update your git credentials: 
    git config --global user.email \"your username\" 
    git config --global user.name \"your email\"
"