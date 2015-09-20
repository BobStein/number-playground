#!/bin/bash
git pull origin rnsdev
PYTHONPATH=/home/visibone/qiki/number-playground:/home/visibone/qiki/qiki-python
python2.7 manage.py runserver 64.239.60.215:27647
