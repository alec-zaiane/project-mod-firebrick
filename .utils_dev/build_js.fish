#!/usr/bin/fish

echo "Building the JS files..."
for file in scripts/*.js
    echo "Building $file"
    set basename (basename $file .js)
    npx esbuild ./scripts/$basename.js --bundle --minify --sourcemap --outfile=./src/socialnetwork/static/$basename.min.js --log-level=warning
end