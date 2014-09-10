#!/bin/bash

celery -A sydgig.tasks worker --loglevel=debug
