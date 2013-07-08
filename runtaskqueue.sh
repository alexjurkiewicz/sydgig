#!/bin/bash

celery -A tasks worker --loglevel=debug
