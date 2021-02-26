#!/usr/bin/env python3
# Copyright 2020 Balbir Thomas
# See LICENSE file for licensing details.

import logging
import yaml
import json

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus

logger = logging.getLogger(__name__)


class PrometheusNodeExporterCharm(CharmBase):
    """A Juju Charm for Prometheus"""

    def __init__(self, *args):
        logger.debug("Initializing Charm")

        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.stop, self._on_stop)

    def _on_config_changed(self, _):
        """Set a new Juju pod specification"""
        self._configure_pod()

    def _on_stop(self, _):
        """Mark unit is inactive"""
        self.unit.status = MaintenanceStatus("Pod is terminating.")

    def _build_pod_spec(self):
        """Construct a Juju pod specification for Prometheus"""
        logger.debug("Building Pod Spec")
        config = self.model.config
        spec = {
            "version": 3,
            "containers": [
                {
                    "name": self.app.name,
                    "imageDetails": {
                        "imagePath": config["prometheus-node-exporter-image-path"],
                        "username": config.get(
                            "prometheus-node-exporter-image-username", ""
                        ),
                        "password": config.get(
                            "prometheus-node-exporter-image-password", ""
                        ),
                    },
                    "ports": [
                        {
                            "containerPort": config["port"],
                            "name": "exporter-http",
                            "protocol": "TCP",
                        }
                    ],
                }
            ],
        }

        return spec

    def _check_config(self):
        """Identify missing but required items in configuation

        :returns: list of missing configuration items (configuration keys)
        """
        logger.debug("Checking Config")
        config = self.model.config
        missing = []

        if not config.get("prometheus-node-exporter-image-path"):
            missing.append("prometheus-node-exporter-image-path")

        if config.get("prometheus-node-exporter-image-username") and not config.get(
            "prometheus-node-exporter-image-password"
        ):
            missing.append("prometheus-node-exporter-image-password")

        return missing

    def _configure_pod(self):
        """Setup a new Prometheus pod specification"""
        logger.debug("Configuring Pod")
        missing_config = self._check_config()
        if missing_config:
            logger.error(
                "Incomplete Configuration : {}. "
                "Application will be blocked.".format(missing_config)
            )
            self.unit.status = BlockedStatus(
                "Missing configuration: {}".format(missing_config)
            )
            return

        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return

        self.unit.status = MaintenanceStatus("Setting pod spec.")
        pod_spec = self._build_pod_spec()

        self.model.pod.set_spec(pod_spec)
        self.app.status = ActiveStatus()
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(PrometheusNodeExporterCharm)
