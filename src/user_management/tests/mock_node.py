from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass
from uuid import UUID
import requests

from user_management.models import Node, User

from django.db import models


DUMMY_RESPONSE = requests.Response()
DUMMY_RESPONSE.status_code = 200


class ActionType:
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


@dataclass
class Action:
    action_type: str
    url: str
    json: Optional[dict[str, Any]] = None

    def __str__(self) -> str:
        return f"Action ({self.action_type}) to {self.url} with json {self.json}"


ACTION_LOG: dict[UUID, list[Action]] = {}


def get_actions(node: MockNode) -> list[Action]:
    return ACTION_LOG.get(node.uuid, [])


class MockNodeManager(models.Manager["MockNode"]):
    def get_queryset(self) -> models.QuerySet[MockNode]:
        return super().get_queryset().filter(is_local_node=False, is_disabled=False)

    def create_node(self, name: str, host_url: str, user: User, host_site_url: str = "") -> MockNode:
        return self.create(host_url=host_url, internal_user=user, name=name)

    def verify_connection(self, host_url: str, internal_username: str, internal_password: str) -> requests.Response:
        # Simulate a successful connection verification
        return DUMMY_RESPONSE

    def find_node(self, host_url: str) -> Optional[MockNode]:
        # Simulate finding a node
        return self.filter(host_url=host_url).first()


class MockNode(Node):
    """Mock class for Node model, logs all actions performed on the node"""
    class Meta:
        proxy = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def MOCK_add_to_action_log(self, action: Action) -> None:
        if self.uuid not in ACTION_LOG:
            ACTION_LOG[self.uuid] = []
        ACTION_LOG[self.uuid].append(action)

    def _post(self, json: dict[str, Any], url: str) -> requests.Response:
        self.MOCK_add_to_action_log(Action(ActionType.POST, url, json))
        return DUMMY_RESPONSE

    def _put(self, json: dict[str, Any], url: str) -> requests.Response:
        self.MOCK_add_to_action_log(Action(ActionType.PUT, url, json))
        return DUMMY_RESPONSE

    def _delete(self, url: str) -> requests.Response:
        self.MOCK_add_to_action_log(Action(ActionType.DELETE, url))
        return DUMMY_RESPONSE

    mock_nodes: MockNodeManager = MockNodeManager()

    @property
    def actions_log(self) -> list[Action]:
        return get_actions(self)

    def clear_action_log(self) -> None:
        ACTION_LOG[self.uuid] = []


def monkeypatch_mock_nodes() -> None:
    Node.external_nodes = MockNode.mock_nodes  # type: ignore
    MockNode_added_methods = set(dir(MockNode)) - set(dir(Node))
    override_methods = {
        "_post",
        "_put",
        "_delete",
    }
    MockNode_added_methods = MockNode_added_methods.union(override_methods)

    for method_name in MockNode_added_methods:
        method = getattr(MockNode, method_name)
        setattr(Node, method_name, method)
