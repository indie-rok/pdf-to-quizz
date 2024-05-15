### running venv

```
source myprojectenv/bin/activate
```

### installing req

```
pip install -r requirements.txt
```

### Running local

```
flask --app app run
```

### running prod

```
gunicorn --config gunicorn_config.py app:app
```
