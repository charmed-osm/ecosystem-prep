#!/bin/bash

juju add-model ecosystem microk8s

juju model-config update-status-hook-interval=1m
juju model-config logging-config="<root>=DEBUG"

./build_charms.sh

juju deploy ./prometheus
juju deploy ./grafana
juju relate grafana prometheus
juju deploy ./mock-knf
juju relate prometheus mock-knf
juju scale-application mock-knf 3
juju deploy ./graylog
juju config graylog admin-password=admin
juju deploy ./mongodb
juju deploy ./elasticsearch
juju relate graylog mongodb
juju relate graylog elasticsearch
juju deploy ./filebeat
juju relate graylog filebeat