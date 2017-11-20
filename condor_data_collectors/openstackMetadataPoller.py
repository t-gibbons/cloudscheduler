from multiprocessing import Process
import time
import json
import logging
import config

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient

## NEED TO TO CONFIG
# openstack_metadata_log_file
# cacert


# The purpose of this file is to get some information from the various registered
# openstack clouds and place it in a database for use by cloudscheduler
#
# Target data sets (should all be available from novaclient):
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information

## UTILITY FUNCTIONS
#

def get_openstack_session(auth_url, username, password, project, user_domain="Default", project_domain="Default"):
    authsplit = auth_url.split('/')
    version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    if version == 2:
        try:
            auth = v2.Password(auth_url=auth_url, username=username, password=password, tenant_name=project)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as e:
            print("Problem importing keystone modules, and getting session: %s" % e)
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(auth_url=auth_url, username=username, password=password, project_name=project, user_domain_name=user_domain, project_domain=project_domain)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as e:
            print("Problem importing keystone modules, and getting session: %s" % e)
        return sess

def get_nova_client(session):
    nova = novaclient.Client("2", session=session)
    return nova

def get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def get_cinder_client(session):
    cinder = cinclient.Client(session=session)
    return cinder



def get_flavor_data(nova):
    return  nova.flavors.list()

# Returns a tuple of quotas (novaquotas, cinderquotas)
def get_quota_data(nova, cinder, project):
    # this command gets the default quotas for a project
    nova_quotas = nova.quotas.defaults(project)
    # it should be possible to get quotas at the project-user level but access must be enabled on the openstack side
    # the command for this is nova.quotas.get(tenant_id, user_id)

    # weneed to also get the storage quotas for a project since they are not available from nova
    cinder_quotas = cinder.quotas.defaults(project)
    return nova_quotas, cinder_quotas

def get_image_data(nova):
    return nova.glance.list()

def get_network_data(neutron):
    return neutron.list_networks()['networks']



## PROCESS FUNCTIONS
#
def metadata_poller():

    while(True):
        # Prepare Database session and objets
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Cloud = Base.classes.cloud_resources
        Flavor = Base.classes.cloud_flavors
        Image = Base.classes.cloud_images
        Network = Base.classes.cloud_networks
        Quota = Base.classes.cloud_quotas
        # Retrieve registered clouds
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type=="openstack")

        # Itterate over cloud list
        for cloud in cloud_list:
            # check if v3 or v2
            authsplit = cloud.authurl.split('/')
            version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            if version == 2:
                session = get_openstack_session(auth_url=cloud.authurl, username=cloud.username, password=cloud.password, project=cloud.prject)
            else:
                session = get_openstack_session(auth_url=cloud.authurl, username=cloud.username, password=cloud.password, project=cloud.prject, user_domain=cloud.userdomainname, project_domain=cloud.projectdomainname):
 
            # setup openstack api objects
            nova = get_nova_client(session)
            neutron = get_neutron_client(session)
            cinder = get_cinder_client(session)

            # Retrieve and proccess metadata

            # FLAVORS
            flav_list = get_flavor_data(nova)
            for flavor in flav_list:
                flav_dict = {
                    'auth_url': cloud.authurl,
                    'project': cloud.project,
                    'ram': flavor.ram,
                    'vcpus': flavor.vcpus,
                    'id': flavor.id,
                    'swap': flavor.swap,
                    'disk': flavor.disk,
                    'is_public': flavor.__dict__.get('os-flavor-access:is_public')
                }
                new_flav = Flavor(**flav_dict)
                db_session.merge(new_flav)

            # QUOTAS
            nova_quotas, storage_quotas = get_quota_data(nova, cinder, cloud.project)
            quota_dict = {
                'auth_url': cloud.authurl,
                'project': cloud.project,
                'cores': nova_quotas.cores,
                'instances': nova_quotas.instances,
                'ram': nova_quotas.ram,
                'key_pairs': nova_quotas.key_pairs,
                'security_groups': nova_quotas.security_groups,
                'backup_gigabytes': storage_quotas.backup_gigabytes,
                'backups': storage_quotas.backups,
                'gigabytes': storage_quotas.gigabytes,
                'per_volume_gigabytes': storage_quotas.per_volume_gigabytes,
                'snapshots': storage_quotas.snapshots,
                'volumes': storage_quotas.volumes
            }
            new_quota = Quota(**quota_dict)
            db_session.merge(new_quota)

            # IMAGES
            image_list = get_image_data(nova)
            for image in image_list:
                img_dict = {
                    'auth_url': cloud.authurl,
                    'project': cloud.project,
                    'container_format': image.container_format,
                    'disk_format': image.disk_format,
                    'min_ram': image.min_ram,
                    'id': image.id,
                    'size': image.size,
                    'visibility': image.visibility,
                    'min_disk': image.min_disk,
                    'name': image.name
                }
                new_image = Image(**img_dict)
                db_session.merge(new_image)

            # NETWORKS
            '''
            name
            subnets
            tenant_id
            router:external
            shared
            id
            '''
            net_list = get_network_data(neutron)
            for network in net_list:
                network_dict = {
                    'auth_url': cloud.authurl,
                    'project': cloud.project,
                    'name': network['name'],
                    'subnets': network['subnets'],
                    'tenant_id': network['tenant_id'],
                    'router:external': network['router:external'],
                    'shared': network['shared'],
                    'id': network['id']
                }
                new_network = Network(**network_dict)
                db_session.merge(new_network)

            #finalize session
            session.commit()


        time.sleep(config.sleep_interval) # default 5 mins
 

    return None


def cleanUp():
    # Will need some sort of cleanup routine to remove db enteries for images and networks that have been renamed/deleted
    return None


## MAIN 
#
if __name__ == '__main__':

    logging.basicConfig(filename=config.poller_log_file,level=logging.DEBUG)
    processes = []

    p_metadata_poller = Process(target=metadata_poller)
    processes.append(p_metadata_poller)

    # Wait for keyboard input to exit
    try:
        for process in processes:
            process.start()
        while(True):
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!" % process.name)
                    logging.error("Restarting %s process...")
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s" % process.name)


