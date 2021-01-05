#!/usr/bin/env sh

pip install coverage # Install test dependency

export PATH=$PATH:/home/app/.local/bin
coverage run --source="." manage.py test # Run Tests
coverage report
coverage xml # Output report
