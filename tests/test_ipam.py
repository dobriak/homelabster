from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from homelabster.main import create_app
from homelabster.models import IpamPort, IpamHost, IpamNetwork, IpamDocument
from homelabster.repository import IpamRepository


class TestIpamPort:
    def test_valid_port(self):
        p = IpamPort(name="webserver1", port=8080)
        assert p.name == "webserver1"
        assert p.port == 8080

    def test_port_must_be_at_least_1(self):
        with pytest.raises(ValidationError):
            IpamPort(name="bad", port=0)

    def test_port_must_be_at_most_65535(self):
        with pytest.raises(ValidationError):
            IpamPort(name="bad", port=65536)

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            IpamPort(name="", port=8080)


class TestIpamHost:
    def test_valid_host(self):
        h = IpamHost(hostname="myhost1", ip="192.168.1.5")
        assert h.hostname == "myhost1"
        assert h.ip == "192.168.1.5"
        assert h.ports == []

    def test_hostname_required(self):
        with pytest.raises(ValidationError):
            IpamHost(hostname="", ip="192.168.1.5")

    def test_ip_must_be_valid_ipv4(self):
        with pytest.raises(ValidationError):
            IpamHost(hostname="h", ip="not-an-ip")

    def test_host_with_ports(self):
        h = IpamHost(hostname="h", ip="10.0.0.1", ports=[IpamPort(name="web", port=80)])
        assert len(h.ports) == 1


class TestIpamNetwork:
    def test_valid_network(self):
        n = IpamNetwork(cidr="192.168.1.0/24")
        assert n.cidr == "192.168.1.0/24"
        assert n.hosts == []

    def test_cidr_must_be_valid(self):
        with pytest.raises(ValidationError):
            IpamNetwork(cidr="not-a-cidr")

    def test_host_ips_must_be_within_cidr(self):
        with pytest.raises(ValidationError, match="not within CIDR"):
            IpamNetwork(cidr="192.168.1.0/24", hosts=[IpamHost(hostname="h", ip="10.0.0.1")])

    def test_host_ips_unique_within_network(self):
        with pytest.raises(ValidationError, match="unique"):
            IpamNetwork(cidr="192.168.1.0/24", hosts=[
                IpamHost(hostname="a", ip="192.168.1.5"),
                IpamHost(hostname="b", ip="192.168.1.5"),
            ])

    def test_host_ip_at_network_boundary(self):
        n = IpamNetwork(cidr="192.168.1.0/24", hosts=[IpamHost(hostname="h", ip="192.168.1.255")])
        assert n.hosts[0].ip == "192.168.1.255"


class TestIpamDocument:
    def test_valid_empty_document(self):
        d = IpamDocument()
        assert d.version == 1
        assert d.networks == []

    def test_document_with_networks(self):
        d = IpamDocument(networks=[IpamNetwork(cidr="10.0.0.0/8")])
        assert len(d.networks) == 1


# ---------------------------------------------------------------------------
# Repository tests
# ---------------------------------------------------------------------------


def _sample_network(cidr="192.168.1.0/24"):
    hosts = [
        IpamHost(hostname="myhost1", ip="192.168.1.5", ports=[IpamPort(name="web", port=80)])
    ]
    return IpamNetwork(cidr=cidr, hosts=hosts)


class TestIpamRepository:
    def test_load_missing_returns_empty(self, tmp_path: Path):
        doc = IpamRepository(tmp_path / "ipam.yaml").load()
        assert doc.networks == []

    def test_create_and_list(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        assert len(repo.list_networks()) == 1

    def test_create_duplicate_raises(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        with pytest.raises(ValueError, match="already exists"):
            repo.create_network(_sample_network())

    def test_get_network_and_not_found(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        assert repo.get_network("192.168.1.0/24").cidr == "192.168.1.0/24"
        with pytest.raises(KeyError):
            repo.get_network("10.0.0.0/8")

    def test_update_network(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        new_net = IpamNetwork(cidr="10.0.0.0/8", hosts=[
            IpamHost(hostname="renamed", ip="10.0.0.1")
        ])
        repo.update_network("192.168.1.0/24", new_net)
        with pytest.raises(KeyError):
            repo.get_network("192.168.1.0/24")
        assert repo.get_network("10.0.0.0/8").cidr == "10.0.0.0/8"

    def test_delete_network(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        repo.delete_network("192.168.1.0/24")
        assert repo.list_networks() == []

    def test_add_host_and_validate(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(IpamNetwork(cidr="192.168.1.0/24"))
        repo.create_host("192.168.1.0/24", IpamHost(hostname="h2", ip="192.168.1.10"))
        assert len(repo.get_network("192.168.1.0/24").hosts) == 1

    def test_add_host_duplicate_ip_raises(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        with pytest.raises(ValueError, match="already has a host"):
            repo.create_host("192.168.1.0/24", IpamHost(hostname="dup", ip="192.168.1.5"))

    def test_add_host_outside_cidr_raises(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(IpamNetwork(cidr="192.168.1.0/24"))
        with pytest.raises(ValueError, match="not within CIDR"):
            repo.create_host("192.168.1.0/24", IpamHost(hostname="bad", ip="10.0.0.1"))

    def test_update_and_delete_host(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        repo.update_host("192.168.1.0/24", "192.168.1.5", IpamHost(hostname="renamed", ip="192.168.1.5"))
        assert repo.get_host("192.168.1.0/24", "192.168.1.5").hostname == "renamed"
        repo.delete_host("192.168.1.0/24", "192.168.1.5")
        assert repo.get_network("192.168.1.0/24").hosts == []

    def test_port_crud(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        repo.create_port("192.168.1.0/24", "192.168.1.5", IpamPort(name="ssh", port=22))
        host = repo.get_host("192.168.1.0/24", "192.168.1.5")
        assert len(host.ports) == 2
        repo.update_port("192.168.1.0/24", "192.168.1.5", 22, IpamPort(name="https", port=443))
        host = repo.get_host("192.168.1.0/24", "192.168.1.5")
        assert any(p.port == 443 for p in host.ports)
        assert any(p.port == 80 for p in host.ports)
        repo.delete_port("192.168.1.0/24", "192.168.1.5", 443)
        host = repo.get_host("192.168.1.0/24", "192.168.1.5")
        assert len(host.ports) == 1

    def test_duplicate_port_raises(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        with pytest.raises(ValueError, match="already has a port"):
            repo.create_port("192.168.1.0/24", "192.168.1.5", IpamPort(name="dup", port=80))

    def test_atomic_save_no_temp_files(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.create_network(_sample_network())
        assert not list(tmp_path.glob(".ipam-*.yaml"))

    def test_ensure_exists_copies_example_when_missing(self, tmp_path: Path):
        example = tmp_path / "ipam.yaml.example"
        example.write_text("version: 1\nnetworks: []\n")
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.ensure_exists()
        assert (tmp_path / "ipam.yaml").read_text() == "version: 1\nnetworks: []\n"

    def test_ensure_exists_creates_empty_when_no_example(self, tmp_path: Path):
        repo = IpamRepository(tmp_path / "ipam.yaml")
        repo.ensure_exists()
        doc = repo.load()
        assert doc.networks == []

    def test_ensure_exists_does_not_overwrite_existing(self, tmp_path: Path):
        path = tmp_path / "ipam.yaml"
        path.write_text("version: 1\nnetworks: []\n")
        example = tmp_path / "ipam.yaml.example"
        example.write_text("version: 1\nnetworks:\n- cidr: 10.0.0.0/8\n")
        repo = IpamRepository(path)
        repo.ensure_exists()
        assert path.read_text() == "version: 1\nnetworks: []\n"


# ---------------------------------------------------------------------------
# Route / integration tests
# ---------------------------------------------------------------------------


def _ipam_client(tmp_path: Path) -> TestClient:
    config = tmp_path / "services.yaml"
    config.write_text("version: 1\nservices: []\n")
    app = create_app(config)
    app.state.icons._metadata = {}
    app.state.ipam = IpamRepository(tmp_path / "ipam.yaml")
    return TestClient(app)


class TestIpamRoutes:
    def test_ipam_page_loads(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            response = c.get("/ipam")
            assert response.status_code == 200
            assert "IP Address Management" in response.text
            assert "No CIDR ranges configured" in response.text

    def test_ipam_nav_link_present(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            response = c.get("/")
            assert response.status_code == 200
            assert '<a class="nav-link" href="/ipam">IPAM</a>' in response.text

    def test_network_crud(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            created = c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            assert created.status_code == 200
            assert "192.168.1.0/24" in created.text
            assert "1 host" not in created.text

            page = c.get("/ipam")
            assert "192.168.1.0/24" in page.text

            updated = c.put("/ipam/networks/192.168.1.0%2F24", data={"cidr": "10.0.0.0/8"})
            assert updated.status_code == 200
            assert "10.0.0.0/8" in updated.text

            deleted = c.delete("/ipam/networks/10.0.0.0%2F8")
            assert deleted.status_code == 200
            assert "192.168.1.0/24" not in deleted.text

    def test_network_form_endpoints(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            new_form = c.get("/ipam/networks/new")
            assert new_form.status_code == 200
            assert "Add CIDR" in new_form.text

            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            edit_form = c.get("/ipam/networks/192.168.1.0%2F24/edit")
            assert edit_form.status_code == 200
            assert "Edit CIDR" in edit_form.text
            assert "192.168.1.0/24" in edit_form.text

            cancel = c.get("/ipam/networks/cancel")
            assert cancel.status_code == 200
            assert "Add CIDR" in cancel.text

    def test_network_validation_error(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            response = c.post("/ipam/networks", data={"cidr": "not-a-cidr"})
            assert response.status_code == 422
            assert "must be a valid CIDR" in response.text

    def test_host_crud(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})

            created = c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts",
                data={"hostname": "myhost1", "ip": "192.168.1.5"},
            )
            assert created.status_code == 200
            assert "myhost1" in created.text
            assert "192.168.1.5" in created.text

            updated = c.put(
                "/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5",
                data={"hostname": "renamed", "ip": "192.168.1.5"},
            )
            assert updated.status_code == 200
            assert "renamed" in updated.text

            deleted = c.delete("/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5")
            assert deleted.status_code == 200
            assert "renamed" not in deleted.text

    def test_host_validation_error(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            response = c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts",
                data={"hostname": "bad", "ip": "10.0.0.1"},
            )
            assert response.status_code == 422
            assert "not within CIDR" in response.text

    def test_port_crud(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts",
                data={"hostname": "myhost1", "ip": "192.168.1.5"},
            )

            created = c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5/ports",
                data={"name": "web", "port": "80"},
            )
            assert created.status_code == 200
            assert "web:80" in created.text

            updated = c.put(
                "/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5/ports/80",
                data={"name": "https", "port": "443"},
            )
            assert updated.status_code == 200
            assert "https:443" in updated.text

            deleted = c.delete(
                "/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5/ports/443"
            )
            assert deleted.status_code == 200
            assert "https:443" not in deleted.text

    def test_browse_modal(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts",
                data={"hostname": "myhost1", "ip": "192.168.1.5"},
            )
            c.post(
                "/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.5/ports",
                data={"name": "web", "port": "80"},
            )

            response = c.get("/ipam/browse")
            assert response.status_code == 200
            assert "192.168.1.0/24" in response.text
            assert "myhost1" in response.text
            assert "web:80" in response.text
            assert 'data-ip="192.168.1.5"' in response.text
            assert 'data-port="80"' in response.text

    def test_browse_modal_empty(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            response = c.get("/ipam/browse")
            assert response.status_code == 200
            assert "No IPAM data configured" in response.text

    def test_404_for_missing_network(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            assert c.get("/ipam/networks/10.0.0.0%2F8/edit").status_code == 404
            assert c.delete("/ipam/networks/10.0.0.0%2F8").status_code == 404

    def test_404_for_missing_host(self, tmp_path: Path):
        with _ipam_client(tmp_path) as c:
            c.post("/ipam/networks", data={"cidr": "192.168.1.0/24"})
            assert c.get("/ipam/networks/192.168.1.0%2F24/hosts/192.168.1.99/edit").status_code == 404
