# Monitoring

```bash
juju bootstrap microk8s
juju add-model ecosystem microk8s

juju model-config logging-config="<root>=DEBUG"

cd prometheus-operator/
charmcraft build
juju deploy ./prometheus.charm

cd ../grafana-operator/
charmcraft build
juju deploy ./grafana.charm --resource grafana-image=ubuntu/grafana:latest

juju relate grafana prometheus

cd ../prometheus-node-exporter-operator/
charmcraft build
juju deploy ./node-exporter.charm

juju relate prometheus node-exporter

juju scale-application node-exporter 3
```

In grafana, do:
```
rate(node_cpu_seconds_total{instance="node-exporter-0.node-exporter-endpoints:9100"}[5m])
rate(node_cpu_seconds_total{instance="node-exporter-1.node-exporter-endpoints:9100"}[5m])
rate(node_cpu_seconds_total{instance="node-exporter-1.node-exporter-endpoints:9100"}[5m])
```
# Logging

cd ../mongodb-operator/
charmcraft build
juju deploy ./mongodb.charm --resource mongodb-image=mongo:latest


cd ../elasticsearch-operator/
charmcraft build
juju deploy ./elasticsearch.charm

cd ../graylog-operator/
charmcraft build
juju deploy ./graylog.charm --resource graylog-image=graylog/graylog:3.3.8-1
juju config graylog admin-password=admin


juju relate graylog mongodb
juju relate graylog elasticsearch