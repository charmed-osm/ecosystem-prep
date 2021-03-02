#!/usr/bin/env python3
# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

import hashlib
import logging
import random
import string
import yaml

from oci_image import OCIImageResource, OCIImageResourceError
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
from ops.framework import StoredState

logger = logging.getLogger(__name__)


class FilebeatCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        # initialize image resource
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.leader_elected, self._on_config_changed)
        self.framework.observe(self.on.logstash_relation_changed, self._on_logstash_relation_changed)
        self.framework.observe(self.on.logstash_relation_broken, self._on_logstash_relation_broken)

        self.image = OCIImageResource(self, "filebeat-image")

    def _on_logstash_relation_changed(self, event):
        self._configure_pod()
        

    def _on_logstash_relation_broken(self, event):
        self._configure_pod()

    def _on_config_changed(self, _):
        self._configure_pod()

    def _on_update_status(self, _):
        self._configure_pod()

    def _on_stop(self, _):
        self.unit.status = MaintenanceStatus("Pod is terminating.")

    def get_logstash_hosts(self):
        hosts = []
        for relation in self.model.relations["logstash"]:
            if not relation.app or relation.app not in relation.data:
                continue
            relation_data = relation.data[relation.app]
            if "host" in relation_data and "port" in relation_data:
                hosts.append(f'{relation_data["host"]}:{relation_data["port"]}')
        return hosts

    def _build_pod_spec(self, logstash_hosts):
        config = self.model.config

        spec = {
            "version": 3,
            "containers": [
                {
                    "name": self.app.name,
                    "image": "elastic/filebeat:7.11.1",
                    "ports": [{"containerPort": config["port"], "protocol": "TCP"}],
                    "envConfig": {"hosts": str(logstash_hosts)},
                    "args": ["-c", "/etc/filebeat/filebeat.yml", "-e"],
                    "volumeConfig": [
                        {
                            "name": "logs",
                            "mountPath": "/var/log/pods",
                            "hostPath": {"path": "/var/log/pods", "type": "Directory"},
                        },
                        {
                            "name": "config",
                            "mountPath": "/etc/filebeat",
                            "files": [
                                {
                                    "path": "filebeat.yml",
                                    "content": yaml.dump(
                                        {
                                            "filebeat": {
                                                "inputs": [
                                                    {
                                                        "type": "log",
                                                        "paths": [
                                                            "/var/log/pods/*/*/*.log",
                                                            "/var/log/*.log",
                                                            "/var/log/*/*.log",
                                                            "/var/log/syslog",
                                                        ],
                                                        "scan_frequency": "10s",
                                                    },
                                                ],
                                            },
                                            "output": {
                                                "logstash": {"hosts": logstash_hosts}
                                            },
                                        }
                                    ),
                                }
                            ],
                        },
                    ],
                }
            ],
        }

        return spec

    def _configure_pod(self):
        """Configure the K8s pod spec for Filebeat."""
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        logstash_hosts = self.get_logstash_hosts()
        if not logstash_hosts:
            self.unit.status = BlockedStatus("Need logstash relation.")
            return
        spec = self._build_pod_spec(logstash_hosts)
        if not spec:
            return
        self.model.pod.set_spec(spec)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(FilebeatCharm)
