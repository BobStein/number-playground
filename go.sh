#!/bin/bash

cd /home/visibone/qiki/qiki-python
git pull origin rnsdev

cd /home/visibone/qiki/number-playground
git pull origin rnsdev

PYTHONPATH=/home/visibone/qiki/number-playground:/home/visibone/qiki/qiki-python
python2.7 manage.py runserver 64.239.60.215:27647
