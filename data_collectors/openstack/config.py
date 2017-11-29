import os
import sys
import yaml

poller_log_file = "/var/log/cloudscheduler/openstackpoller.log"
sleep_interval = 300
vm_sleep_interval = 60
cleanup_interval = 3600
vm_cleanup_interval = 120
cacert = "/etc/ssl/certs/CABundle.crt"
log_level = 20 #INFO

db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



if os.path.isfile("/etc/openstack_poller.yaml"):
    path = "/etc/openstack_poller.yaml"

elif os.path.isfile("/opt/cloudscheduler/data_collectors/openstack/openstack_poller.yaml"):
    path = "/opt/cloudscheduler/data_collectors/openstack/openstack_poller.yaml"


try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

except Exception as e:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path


if "general" in cfg:

    if "sleep_interval" in cfg["general"]:
        sleep_interval = cfg["general"]["sleep_interval"]

    if "vm_sleep_interval" in cfg["general"]:
        vm_sleep_interval = cfg["general"]["vm_sleep_interval"]

    if "cleanup_interval" in cfg["general"]:
        cleanup_interval = cfg["general"]["cleanup_interval"]

    if "vm_cleanup_interval" in cfg["general"]:
        vm_cleanup_interval = cfg["general"]["vm_cleanup_interval"]

    if "poller_log_file" in cfg["general"]:
        poller_log_file = cfg["general"]["poller_log_file"]

    if "cacert" in cfg["general"]:
        cacert = cfg["general"]["cacert"]

    if "log_level" in cfg["general"]:
        log_level = cfg["general"]["log_level"]


if "database" in cfg:
    if "db_host" in cfg["database"]:
        db_host = cfg["database"]["db_host"]

    if "db_port" in cfg["database"]:
        db_port = cfg["database"]["db_port"]

    if "db_name" in cfg["database"]:
        db_name = cfg["database"]["db_name"]

    if "db_user" in cfg["database"]:
        db_user = cfg["database"]["db_user"]

    if "db_password" in cfg["database"]:
        db_password = cfg["database"]["db_password"]
