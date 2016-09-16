import pytest
import re


@pytest.fixture()
def GetTimeServers(File):
    """ Extract the timeservers from ntp.conf

    Args:
        File - Module to access ntp config file

    Returns:
        ntp_servers - List of configured servers as indicated by ntp.conf
    """
    ntp_conf = File("/etc/ntp.conf")

    # Remove any configuration options that come after the server/pool name
    all_ntp_servers = map(lambda x: re.sub(" .*", "", x),
                          re.findall("\n(?:server|pool)\s*(.*)",
                                     ntp_conf.content_string))

    # Filter fallback NTP server from configuration file.
    user_ntp_servers = filter(lambda x: x != 'ntp.ubuntu.com', all_ntp_servers)
    return user_ntp_servers


@pytest.fixture()
def AnsibleDefaults(Ansible):
    """ Load default variables into dictionary.

    Args:
        Ansible - Requires the ansible connection backend.
    """
    return Ansible("include_vars", "./defaults/main.yml")["ansible_facts"]


def test_ntp_exists(Package, AnsibleDefaults, GetTimeServers):
    """ Ensure the desired version of NTP is installed.

    Args:
        Package - Module to determine package install status and version
        AnsibleDefaults - Get desired package version
    """
    ntp = Package("ntp")
    ntp_target_version = AnsibleDefaults["ntp_version"].split("*")[0]
    assert ntp.is_installed
    assert ntp.version.startswith(ntp_target_version)


def test_ntp_config(AnsibleDefaults, GetTimeServers):
    """ Ensure NTP is configured to use the proper timeservers

    Args:
        AnsibleDefaults - Get desired timeservers
        GetTimeServers - Get configured timeservers
    """
    ntp_target_servers = AnsibleDefaults["ntp_servers"]
    assert(set(GetTimeServers) == set(ntp_target_servers))


def test_ntp_service(Service):
    """ Ensure the NTP service is both enabled and running

    Args:
        Service - Module used to determine service status
    """
    ntp = Service("ntp")
    assert ntp.is_enabled
    assert ntp.is_running
