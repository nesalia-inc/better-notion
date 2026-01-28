"""Unit tests for dependency resolver."""

from dataclasses import dataclass
from typing import List

import pytest

from better_notion.utils.agents.dependency_resolver import DependencyResolver


@dataclass
class MockTask:
    """Mock task for testing."""

    id: str
    status: str
    depends_on: List[str]


class TestDependencyResolver:
    """Tests for DependencyResolver class."""

    def test_build_dependency_graph_empty(self) -> None:
        """Test building graph from empty task list."""
        graph = DependencyResolver.build_dependency_graph(
            [],
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        assert graph == {}

    def test_build_dependency_graph_simple(self) -> None:
        """Test building simple dependency graph."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        graph = DependencyResolver.build_dependency_graph(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        assert graph == {"a": [], "b": ["a"]}

    def test_build_dependency_graph_complex(self) -> None:
        """Test building complex dependency graph."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
            MockTask(id="c", status="Backlog", depends_on=["a", "b"]),
        ]

        graph = DependencyResolver.build_dependency_graph(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        assert graph == {"a": [], "b": ["a"], "c": ["a", "b"]}

    def test_build_dependency_graph_with_none_deps(self) -> None:
        """Test building graph with None dependencies."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=None),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        graph = DependencyResolver.build_dependency_graph(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        assert graph == {"a": [], "b": ["a"]}

    def test_topological_sort_simple(self) -> None:
        """Test topological sort with simple graph."""
        graph = {"a": [], "b": ["a"], "c": ["b"]}

        order = DependencyResolver.topological_sort(graph)

        assert order == ["a", "b", "c"]

    def test_topological_sort_multiple_dependencies(self) -> None:
        """Test topological sort with multiple dependencies."""
        graph = {
            "a": [],
            "b": [],
            "c": ["a", "b"],
        }

        order = DependencyResolver.topological_sort(graph)

        # a and b must come before c
        assert order.index("c") > order.index("a")
        assert order.index("c") > order.index("b")

    def test_topological_sort_complex(self) -> None:
        """Test topological sort with complex graph."""
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["a"],
            "d": ["b", "c"],
        }

        order = DependencyResolver.topological_sort(graph)

        # Check dependencies come before dependents
        assert order.index("a") < order.index("b")
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("d")
        assert order.index("c") < order.index("d")

    def test_topological_sort_circular_dependency(self) -> None:
        """Test topological sort detects circular dependencies."""
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }

        with pytest.raises(ValueError) as exc_info:
            DependencyResolver.topological_sort(graph)

        assert "Circular dependency" in str(exc_info.value)

    def test_topological_sort_self_loop(self) -> None:
        """Test topological sort with self-loop."""
        graph = {
            "a": ["a"],
        }

        with pytest.raises(ValueError):
            DependencyResolver.topological_sort(graph)

    def test_detect_cycles_no_cycles(self) -> None:
        """Test cycle detection with acyclic graph."""
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["b"],
        }

        cycles = DependencyResolver.detect_cycles(graph)

        assert cycles == []

    def test_detect_cycles_with_cycle(self) -> None:
        """Test cycle detection detects cycles."""
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }

        cycles = DependencyResolver.detect_cycles(graph)

        assert len(cycles) > 0
        # Each cycle should include all three nodes
        assert len(cycles[0]) == 4  # a, b, c, a (back to start)

    def test_detect_cycles_multiple_cycles(self) -> None:
        """Test cycle detection with multiple cycles."""
        graph = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
        }

        cycles = DependencyResolver.detect_cycles(graph)

        assert len(cycles) >= 2

    def test_get_ready_tasks_no_dependencies(self) -> None:
        """Test finding ready tasks with no dependencies."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=[]),
        ]

        ready = DependencyResolver.get_ready_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        # Both should be ready (no deps and not completed)
        assert len(ready) == 2
        task_ids = {t.id for t in ready}
        assert task_ids == {"a", "b"}

    def test_get_ready_tasks_with_satisfied_dependencies(self) -> None:
        """Test finding tasks with satisfied dependencies."""
        tasks = [
            MockTask(id="a", status="Completed", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        ready = DependencyResolver.get_ready_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        assert len(ready) == 1
        assert ready[0].id == "b"

    def test_get_ready_tasks_with_unsatisfied_dependencies(self) -> None:
        """Test finding tasks with unsatisfied dependencies."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        ready = DependencyResolver.get_ready_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        # Only 'a' should be ready
        assert len(ready) == 1
        assert ready[0].id == "a"

    def test_get_ready_tasks_completed_task_not_ready(self) -> None:
        """Test that completed tasks are not included in ready list."""
        tasks = [
            MockTask(id="a", status="Completed", depends_on=[]),
        ]

        ready = DependencyResolver.get_ready_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        assert len(ready) == 0

    def test_get_ready_tasks_missing_dependency(self) -> None:
        """Test tasks with missing dependencies are not ready."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=["missing"]),
        ]

        ready = DependencyResolver.get_ready_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        # Task should not be ready (dependency doesn't exist)
        assert len(ready) == 0

    def test_get_blocked_tasks_none_blocked(self) -> None:
        """Test finding blocked tasks when none are blocked."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=[]),
        ]

        blocked = DependencyResolver.get_blocked_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        assert len(blocked) == 0

    def test_get_blocked_tasks_with_blocked(self) -> None:
        """Test finding blocked tasks."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        blocked = DependencyResolver.get_blocked_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        assert len(blocked) == 1
        task, blockers = blocked[0]
        assert task.id == "b"
        assert len(blockers) == 1
        assert blockers[0].id == "a"

    def test_get_blocked_tasks_multiple_blockers(self) -> None:
        """Test task blocked by multiple dependencies."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=[]),
            MockTask(id="c", status="Backlog", depends_on=["a", "b"]),
        ]

        blocked = DependencyResolver.get_blocked_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        assert len(blocked) == 1
        task, blockers = blocked[0]
        assert task.id == "c"
        assert len(blockers) == 2
        blocker_ids = {b.id for b in blockers}
        assert blocker_ids == {"a", "b"}

    def test_get_blocked_tasks_partially_satisfied(self) -> None:
        """Test task with some satisfied dependencies."""
        tasks = [
            MockTask(id="a", status="Completed", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=[]),
            MockTask(id="c", status="Backlog", depends_on=["a", "b"]),
        ]

        blocked = DependencyResolver.get_blocked_tasks(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
            lambda t: t.status,
        )

        # c is blocked by b (a is completed)
        assert len(blocked) == 1
        task, blockers = blocked[0]
        assert task.id == "c"
        assert len(blockers) == 1
        assert blockers[0].id == "b"

    def test_get_execution_order_simple(self) -> None:
        """Test getting execution order for simple graph."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        order = DependencyResolver.get_execution_order(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        assert len(order) == 2
        assert order[0].id == "a"
        assert order[1].id == "b"

    def test_get_execution_order_complex(self) -> None:
        """Test getting execution order for complex graph."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=[]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
            MockTask(id="c", status="Backlog", depends_on=["a"]),
            MockTask(id="d", status="Backlog", depends_on=["b", "c"]),
        ]

        order = DependencyResolver.get_execution_order(
            tasks,
            lambda t: t.id,
            lambda t: t.depends_on,
        )

        # Check dependencies come before dependents
        order_ids = [t.id for t in order]
        assert order_ids.index("a") < order_ids.index("b")
        assert order_ids.index("a") < order_ids.index("c")
        assert order_ids.index("b") < order_ids.index("d")
        assert order_ids.index("c") < order_ids.index("d")

    def test_get_execution_order_with_cycle(self) -> None:
        """Test execution order detects circular dependencies."""
        tasks = [
            MockTask(id="a", status="Backlog", depends_on=["b"]),
            MockTask(id="b", status="Backlog", depends_on=["a"]),
        ]

        with pytest.raises(ValueError) as exc_info:
            DependencyResolver.get_execution_order(
                tasks,
                lambda t: t.id,
                lambda t: t.depends_on,
            )

        assert "Circular dependency" in str(exc_info.value)
