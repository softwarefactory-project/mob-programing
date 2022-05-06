# memray

Today session is about:

- Learn the memray tool to diagnose python runtime performance
- Use it to inspect the nodepool-builder process and look for memory leak

## Installation

```sh
yum group install -y 'Development Tools'
yum install -y rh-python38 rh-python38-python-devel
scl enable rh-python38 bash
pip3 install memray
```

## Preparation

- create a clouds.yaml file in /var/lib/nodepool/.config/openstack/

```yaml
cache:
  expiration:
    server: 5
clouds:
  default:
    auth:
      application_credential_id: app1_id
      application_credential_secret: app1_secret
      auth_url: https://mycloud_01:5000/v3
    auth_type: v3applicationcredential
    image_format: raw
    regions:
      - name: myRegion
        values:
          networks:
            - default_interface: true
              name: public
              nat_source: true
              routes_externally: true
            - name: private
              nat_destination: true
              routes_externally: false
  mycloud_1_user:
    auth:
      auth_url: https://mycloud_01:5000/v3
      password: userpass
      username: username
    image_format: raw
    regions:
      - name: myRegion
        values:
          networks:
            - default_interface: true
              name: public
              nat_source: true
              routes_externally: true
            - name: private
              nat_destination: true
              routes_externally: false
  mycloud_2:
    auth:
      application_credential_id: app2_id
      application_credential_secret: app2_secret
    auth_type: v3applicationcredential
    image_format: qcow2
    profile: mycloud_2
```

- Edit nodepool.yaml file in /etc/nodepool/nodepool.yaml

```yaml
elements-dir: /etc/nodepool/elements:/usr/share/sf-elements
images-dir: /var/lib/nodepool/dib
build-log-dir: /var/www/html/nodepool-builder/

diskimages:
  - name: dib-centos-7
    elements:
      - centos-minimal
      - nodepool-minimal
      - zuul-worker-user
  - name: cloud-fedora-rawhide
    python-path: /usr/bin/python3
    dib-cmd: /usr/bin/dib-virt-customize /etc/nodepool/virt_images/cloud-fedora-rawhide.yaml
labels:
  - name: dib-centos-7
    min-ready: 1
  - name: cloud-fedora-rawhide
    min-ready: 1
providers:
  - name: default
    cloud: default
    clean-floating-ips: true
    image-name-format: '{image_name}-{timestamp}'
    boot-timeout: 120
    rate: 10.0
    diskimages:
      - name: dib-centos-7
      - name: cloud-fedora-rawhide
    pools:
      - name: main
        max-servers: 5
        networks:
          - worker-net-name
        labels:
          - name: dib-centos-7
            min-ram: 1024
            diskimage: dib-centos-7
          - name: cloud-fedora-rawhide
            min-ram: 1024
            diskimage: cloud-fedora-rawhide
webapp:
  port: 8006
zookeeper-servers:
  - host: managesf.sftests.com
    port: 2281
zookeeper-tls:
  cert: /etc/nodepool/ssl/zookeeper.crt
  key: /etc/nodepool/ssl/zookeeper.key
  ca: /etc/nodepool/ssl/zk-ca.pem
```

## Nodepool builder

We need to stop the nodepool builder service inside the container, that
systemd will not restart that service. Then we can go to next
step with analyzing the nodepool builder service.

```sh
podman exec -it nodepool-builder bash
pip3 install memray
# pause the running builder process:
kill -SIGSTOP $(pidof nodepool-builder)
```

## Test

### Basic test

```sh
# run the process and collect trace:
python3 -m memray run fake-builder.py -o output.bin
# display the traces:
python3 -m memray tree ./memray-fake-builder.py.3101.bin
```

### Live trace

NOTE: does not work with `--follow-fork` option. In that case,
we can run normal process, then in live view, change the threads with
arrows cursors.

```sh
# run the process live
python3 -m memray run --native --live fake-builder.py
memray run --live-remote /usr/local/bin/nodepool-builder -d -c /etc/nodepool/nodepool.yaml
# an in another window:   `memray live $PORT`
```

### Analyze output as html file

```sh
# we can dump information to a file, then parse it
memray run -o /var/lib/nodepool/output.bin  --follow-fork /usr/local/bin/nodepool-builder -d -c /etc/nodepool/nodepool.yaml
# parse it
memray flamegraph output.bin
# it will create a new file: memray-flamegraph-output.html
# with very simple http server, let's check the results
python3 -m http.server 8082
```
