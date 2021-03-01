# Pre-requisites

Microk8s:

```bash
sudo snap install microk8s --classic --channel 1.19/stable

sudo usermod -a -G microk8s `whoami`
sudo chown -f -R `whoami` ~/.kube

newgrp microk8s
microk8s.status --wait-ready
microk8s.enable storage dns
```

Juju controller:

```bash
sudo snap install juju --classic --channel 2.8/stable
juju bootstrap microk8s
```

Juju model:

```bash
juju add-model ecosystem microk8s

juju model-config update-status-hook-interval=1m
juju model-config logging-config="<root>=DEBUG"
```

Build charms:

```bash
./build_charms.sh
```

# Monitoring

TODO: Change name of `node-exporter` to something else.

Prometheus:

```bash
juju deploy ./prometheus
```

Grafana:

```bash
juju deploy ./grafana
```

Relate prometheus and grafana:

```bash
juju relate grafana prometheus
```

Deploy simulator:

```bash
juju deploy ./node-exporter
```

Relate simulator to prometheus:

```bash
juju relate prometheus node-exporter
```

Scale simulator:

```bash
juju scale-application node-exporter 3
```

## Test

Go to Prometheus url and check under status/targets if all node exporters are listed there.

Login to grafana, create a dashboard and check the metrics for the following queries:

```
rate(node_cpu_seconds_total{instance="node-exporter-0.node-exporter-endpoints:9100"}[5m])
rate(node_cpu_seconds_total{instance="node-exporter-1.node-exporter-endpoints:9100"}[5m])
rate(node_cpu_seconds_total{instance="node-exporter-1.node-exporter-endpoints:9100"}[5m])
```

TODO: Add an action to start a process of something, to see it in Grafana

# Logging

Deploy Graylog:

```bash
juju deploy ./graylog
juju config graylog admin-password=admin
```

Deploy Mongo and elasticsearch:

```bash
juju deploy ./mongodb
juju deploy ./elasticsearch
```

Graylog relations:

```bash
juju relate graylog mongodb
juju relate graylog elasticsearch
```

Deploy Filebeat and relate to graylog:

```bash
juju deploy ./filebeat
# juju relate graylog filebeat
```

TODO: Add filebeat-graylog relation
TODO: Create a bundle with all charms
TODO: Create OSM packages and test it :)
TODO: Try to add the beat input of graylog automatically