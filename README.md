To run:
```
mkdir -p [whatever]/data && cd [whatever]
git clone --depth 1 https://github.com/LT-bot/bot .
```

If you use python a lot and have a bunch of system-wide packages:
```
python -m venv --system-site-packages --symlinks --upgrade-deps .
```
Otherwise:
```
python -m venv .
```
Install the dependencies:
```
pip install -U discord.py discord-py-slash-command

cp example.conf main.conf
```

Edit main.conf as needed, and put your token in the file 'data/token'. Make sure 
there are no spaces or newlines as that file isn't really parsed.

Create 'data/responses' as needed. Note that the welcome message is hardcoded, so 
you should edit it at 'cogs/Listener.py'.
