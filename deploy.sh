#!/bin/bash
set +ex
if [ ! -e secret.json ]; then
    gsutil cp gs://vape-survey-secrets/secret.json secret.json
fi

if [ ! -e secret.yaml ]; then
    gsutil cp gs://vape-survey-secrets/secret.yaml secret.yaml
fi
if [ ! -e winners.yaml ]; then
    gsutil cp gs://vape-survey-secrets/winners.yaml winners.yaml
fi

yes | gcloud app deploy --project vape-survey

