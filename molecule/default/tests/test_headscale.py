"""Testinfra tests for ansible-role-headscale."""

import pytest


# Directories

def test_data_dir_exists(host):
    """Verify that the data directory exists."""
    d = host.file("/opt/headscale")
    assert d.exists
    assert d.is_directory
    assert d.user == "root"
    assert d.group == "root"
    assert d.mode == 0o700


def test_data_subdir_exists(host):
    """Verify that the data subdirectory exists."""
    d = host.file("/opt/headscale/data")
    assert d.exists
    assert d.is_directory


def test_config_dir_exists(host):
    """Verify that the config directory exists."""
    d = host.file("/opt/headscale/config")
    assert d.exists
    assert d.is_directory
    assert d.user == "root"
    assert d.group == "root"
    assert d.mode == 0o700


# Configuration

def test_config_file_exists(host):
    """Verify that the headscale config file exists."""
    f = host.file("/opt/headscale/config/config.yaml")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o600


def test_config_contains_server_url(host):
    """Verify that the config contains the correct server URL."""
    f = host.file("/opt/headscale/config/config.yaml")
    assert 'server_url: "https://headscale.test.local"' in f.content_string


def test_config_contains_listen_addr(host):
    """Verify that the config contains the listen address."""
    f = host.file("/opt/headscale/config/config.yaml")
    assert 'listen_addr: "0.0.0.0:8080"' in f.content_string


def test_config_contains_database(host):
    """Verify that the config contains database settings."""
    f = host.file("/opt/headscale/config/config.yaml")
    content = f.content_string
    assert "type: \"sqlite\"" in content
    assert "path: \"/var/lib/headscale/db.sqlite\"" in content


def test_config_contains_dns(host):
    """Verify that the config contains DNS settings."""
    f = host.file("/opt/headscale/config/config.yaml")
    content = f.content_string
    assert "magic_dns: true" in content
    assert 'base_domain: "tailnet.local"' in content


# Docker container

def test_headscale_container_is_running(host):
    """Verify that the headscale container is running."""
    result = host.run("docker ps --filter name=headscale --format '{{.Status}}'")
    assert result.rc == 0
    assert "Up" in result.stdout


def test_headscale_container_image(host):
    """Verify that the container uses the correct image."""
    result = host.run("sudo docker inspect headscale --format '{{.Config.Image}}'")
    assert result.rc == 0
    assert "headscale/headscale" in result.stdout


def test_headscale_container_volumes(host):
    """Verify that the container has correct volume mounts."""
    result = host.run("sudo docker inspect headscale --format '{{.Mounts}}'")
    assert result.rc == 0
    assert "/opt/headscale/config" in result.stdout
    assert "/opt/headscale/data" in result.stdout


def test_headscale_container_network(host):
    """Verify that the container is attached to its configured network."""
    result = host.run(
        "sudo docker inspect headscale --format '{{json .NetworkSettings.Networks}}'"
    )
    assert result.rc == 0
    assert "headscale" in result.stdout


# Users

@pytest.mark.parametrize("user", ["alice", "bob"])
def test_headscale_user_exists(host, user):
    """Verify that headscale users are created."""
    result = host.run("sudo docker exec headscale headscale users list")
    assert result.rc == 0
    assert user in result.stdout


@pytest.mark.parametrize("user", ["alice", "bob"])
def test_headscale_preauthkey_exists(host, user):
    """Verify that preauthkeys are generated for users."""
    result = host.run(
        f"sudo docker exec headscale headscale preauthkeys list -o json"
    )
    assert result.rc == 0
    assert user in result.stdout


# Preauthkeys

def test_preauthkeys_dir_exists(host):
    """Verify that the preauthkeys directory exists."""
    d = host.file("/opt/headscale/preauthkeys")
    assert d.exists
    assert d.is_directory
    assert d.user == "root"
    assert d.mode == 0o700


@pytest.mark.parametrize("user", ["alice", "bob"])
def test_preauthkey_file_exists(host, user):
    """Verify that a preauthkey file is created for each user."""
    f = host.file(f"/opt/headscale/preauthkeys/{user}.key")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.mode == 0o600
    assert f.content_string.startswith("hskey-auth-")


# Exit node

def test_ip_forward_enabled(host):
    """Verify that IPv4 forwarding is enabled."""
    result = host.run("sysctl net.ipv4.ip_forward")
    assert result.rc == 0
    assert "net.ipv4.ip_forward = 1" in result.stdout


def test_ipv6_forward_enabled(host):
    """Verify that IPv6 forwarding is enabled."""
    result = host.run("sysctl net.ipv6.conf.all.forwarding")
    assert result.rc == 0
    assert "net.ipv6.conf.all.forwarding = 1" in result.stdout


def test_exit_node_state_dir_exists(host):
    """Verify that the exit node state directory exists."""
    d = host.file("/opt/headscale/tailscale-exit-node")
    assert d.exists
    assert d.is_directory


def test_exit_node_container_is_running(host):
    """Verify that the tailscale exit node container is running."""
    result = host.run(
        "sudo docker ps --filter name=tailscale-exit-node --format '{{.Status}}'"
    )
    assert result.rc == 0
    assert "Up" in result.stdout


def test_exit_node_container_network_mode(host):
    """Verify that the exit node container uses host networking."""
    result = host.run(
        "sudo docker inspect tailscale-exit-node "
        "--format '{{.HostConfig.NetworkMode}}'"
    )
    assert result.rc == 0
    assert "host" in result.stdout


def test_exit_node_user_exists(host):
    """Verify that the exit-node user is created in headscale."""
    result = host.run("sudo docker exec headscale headscale users list")
    assert result.rc == 0
    assert "exit-node" in result.stdout


def test_exit_node_registered_in_headscale(host):
    """Verify that the exit node is registered in headscale."""
    result = host.run(
        "sudo docker exec headscale headscale nodes list -o json"
    )
    assert result.rc == 0
    assert "exit-node" in result.stdout


def test_headscale_port_published_to_localhost(host):
    """Verify headscale container publishes port 8080 to localhost."""
    result = host.run(
        "sudo docker inspect headscale "
        "--format '{{json .HostConfig.PortBindings}}'"
    )
    assert result.rc == 0
    assert "127.0.0.1" in result.stdout
    assert "8080" in result.stdout
