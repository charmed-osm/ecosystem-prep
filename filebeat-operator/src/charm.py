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

        self.image = OCIImageResource(self, "filebeat-image")

    def _on_config_changed(self, _):
        self._configure_pod()

    def _on_update_status(self, _):
        self._configure_pod()

    def _on_stop(self, _):
        self.unit.status = MaintenanceStatus("Pod is terminating.")

    def _build_pod_spec(self):
        config = self.model.config

        # fetch OCI image resource
        try:
            image_info = self.image.fetch()
        except OCIImageResourceError:
            logging.exception("An error occurred while fetching the image info")
            self.unit.status = BlockedStatus("Error fetching image information")
            return {}

        # baseline pod spec
        spec = {
            "version": 3,
            "containers": [
                {
                    "name": self.app.name,
                    "imageDetails": image_info,
                    "ports": [{"containerPort": config["port"], "protocol": "TCP"}],
                    "envConfig": {},
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
                                                "logstash": {"hosts": ["graylog:5044"]}
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

        spec = self._build_pod_spec()
        if not spec:
            return
        self.model.pod.set_spec(spec)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(FilebeatCharm)
