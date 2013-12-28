#!/bin/bash

celery -A sydgig.tasks worker --loglevel=debug -B -c 1
