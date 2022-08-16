Development Notes
=================

Creating Package for pypi
-------------------------
Follow the [instructions](https://packaging.python.org/en/latest/tutorials/packaging-projects/). Create a virtual enviornment and install

```
pip install build
pip install -r requirements.txt
```

Build the package
```
python -m build -n
```

and upload the package
```
twine upload dist/taskfarm-0.3.1*
```

Docker
------
I followed these instructions: https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/