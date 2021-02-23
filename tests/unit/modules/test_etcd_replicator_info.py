from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.sensu.sensu_go.plugins.module_utils import (
    errors, utils,
)
from ansible_collections.sensu.sensu_go.plugins.modules import etcd_replicator_info

from .common.utils import (
    AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args,
)


class TestEtcdReplicatorInfo(ModuleTestCase):
    def test_all_parameters(self, mocker):
        get_mock = mocker.patch.object(utils, "get")
        get_mock.return_value = {"spec": {"k1": "v1"}}
        set_module_args(
            auth=dict(
                user="user",
                password="pass",
                url="http://127.0.0.1:1234",
                api_key="123-key",
                verify=False,
                ca_path="/tmp/ca.bundle",
            ),
            name="demo",
        )

        with pytest.raises(AnsibleExitJson):
            etcd_replicator_info.main()

    def test_get_all_secrets(self, mocker):
        get_mock = mocker.patch.object(utils, "get")
        get_mock.return_value = [
            {"spec": {"k1": "v1"}}, {"spec": {"k2": "v2"}},
        ]
        set_module_args()

        with pytest.raises(AnsibleExitJson) as context:
            etcd_replicator_info.main()

        _client, path = get_mock.call_args[0]
        assert path == "/api/enterprise/federation/v1/etcd-replicators"
        assert context.value.args[0]["objects"] == [
            {"k1": "v1"}, {"k2": "v2"},
        ]

    def test_get_single_replicator(self, mocker):
        get_mock = mocker.patch.object(utils, "get")
        get_mock.return_value = {"spec": {"k3": "v3"}}
        set_module_args(name="demo")

        with pytest.raises(AnsibleExitJson) as context:
            etcd_replicator_info.main()

        _client, path = get_mock.call_args[0]
        assert path == "/api/enterprise/federation/v1/etcd-replicators/demo"
        assert context.value.args[0]["objects"] == [{"k3": "v3"}]

    def test_missing_single_replicator(self, mocker):
        get_mock = mocker.patch.object(utils, "get")
        get_mock.return_value = None
        set_module_args(name="demo")

        with pytest.raises(AnsibleExitJson) as context:
            etcd_replicator_info.main()

        assert context.value.args[0]["objects"] == []

    def test_failure(self, mocker):
        get_mock = mocker.patch.object(utils, "get")
        get_mock.side_effect = errors.Error("Bad error")
        set_module_args(name="demo")

        with pytest.raises(AnsibleFailJson):
            etcd_replicator_info.main()
