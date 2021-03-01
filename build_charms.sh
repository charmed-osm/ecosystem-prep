#!/bin/bash

sudo snap install charmcraft --beta

cd prometheus-operator/
charmcraft build
mv ./prometheus.charm ../prometheus

cd ../grafana-operator/
charmcraft build
mv ./grafana.charm ../grafana

cd ../prometheus-node-exporter-operator/
charmcraft build
mv ./node-exporter.charm ../node-exporter

cd ../mongodb-operator/
charmcraft build
mv ./mongodb.charm ../mongodb

cd ../elasticsearch-operator/
charmcraft build
mv ./elasticsearch.charm ../elasticsearch

cd ../graylog-operator/
charmcraft build
mv ./graylog.charm ../graylog

cd ../filebeat-operator/
charmcraft build
mv ./filebeat.charm ../filebeat
