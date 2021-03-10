# Pre-requisites

## Minimum requirements

- An Ubuntu 20.04 LTS, 18.04 LTS or 16.04 LTS environment to run the commands
- At least 20G of disk space and 8G of memory are recommended
- An internet connection

## Prepare environment

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
```

Requirement for elasticsearch:

```bash
sudo sysctl -w vm.max_map_count=262144
```

# Deployment

```bash
juju deploy cs:knf-lma-stack
```

# Scaling

```bash
juju scale-application mock-knf 3
```

# Known issues

## MongoDB takes a lot of time to configure the replica set

In the start hook, MongoDB will try to initialize the replica set. Normally, when Juju will trigger that hook,
the `mongod` service of the workload pod won't be ready, so the start hook will be deferred. This mean that before
running the next hook, the start hook will be executed again. This process keeps going until the `mongod` service
is up and running, and the charm can configure the replica set.

Usually, the `update-status` hook will make possible the re-trigger of the start hook in order to configure the
replica set. The `update-status-hook-interval` defaults to 5m. If we want to have a faster deployment, we can override
the value `update-status-hook-interval` to 1m.

```bash
juju model-config update-status-hook-interval=1m
```
