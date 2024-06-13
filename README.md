### set up asdf

1. https://asdf-vm.com/guide/getting-started.html

```
sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

```
asdf plugin-add python
```

```
asdf install python latest
```

```
asdf global python latest
```

### creat venv

```
 python -m venv env
```

### running venv

```
source env/bin/activate
```

### installing req

```
pip install -r requirements.txt
```

### install popple-utils

sudo apt install poppler-utils

### Running local

```
flask --debug run --host 0.0.0.0  --port 6001
```

### running prod

```
gunicorn --config gunicorn_config.py app:app
```
