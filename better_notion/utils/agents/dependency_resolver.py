"""Dependency resolution for task management in the agents workflow system.

This module provides functionality to resolve task dependencies, determine
execution order, and find tasks that are ready to start.
"""

from collections import deque
from typing import Any, AsyncIterator, Dict, List, Set, Tuple


class DependencyResolver:
    """Resolves task dependencies and determines execution order.

    This class provides methods to:
    - Build dependency graphs from tasks
    - Perform topological sorting to find execution order
    - Detect circular dependencies
    - Find tasks that are ready to start (all dependencies completed)
    - Find tasks that are blocked by incomplete dependencies

    Example:
        >>> # Build dependency graph
        >>> graph = {
        ...     "task-a": ["task-b"],  # A depends on B
        ...     "task-b": [],           # B has no dependencies
        ... }
        >>>
        >>> # Get execution order
        >>> order = DependencyResolver.topological_sort(graph)
        >>> print(order)  # ["task-b", "task-a"]
    """

    @staticmethod
    def build_dependency_graph(
        tasks: List[Any],
        get_task_id: callable,
        get_dependency_ids: callable,
    ) -> Dict[str, List[str]]:
        """Build dependency graph (adjacency list) from tasks.

        Args:
            tasks: List of task objects
            get_task_id: Function to extract task ID from task object
            get_dependency_ids: Function to extract dependency IDs from task object

        Returns:
            Dict mapping task_id → list of task_ids it depends on

        Example:
            >>> tasks = [task1, task2, task3]
            >>> graph = DependencyResolver.build_dependency_graph(
            ...     tasks,
            ...     lambda t: t.id,
            ...     lambda t: t.dependencies
            ... )
        """
        graph: Dict[str, List[str]] = {}

        for task in tasks:
            task_id = get_task_id(task)
            deps = get_dependency_ids(task)

            # Ensure deps is a list
            if deps is None:
                deps = []
            elif isinstance(deps, str):
                deps = [deps]
            elif not isinstance(deps, list):
                deps = list(deps)

            graph[task_id] = deps

        return graph

    @staticmethod
    def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort to find execution order.

        Args:
            graph: Dependency graph (task_id → list of dependencies)

        Returns:
            List of task IDs in dependency order (dependencies before dependents)

        Raises:
            ValueError: If graph contains circular dependencies

        Example:
            >>> graph = {
            ...     "A": ["B"],
            ...     "B": ["C"],
            ...     "C": [],
            ... }
            >>> order = DependencyResolver.topological_sort(graph)
            >>> print(order)  # ["C", "B", "A"]
        """
        # Calculate in-degrees
        in_degree: Dict[str, int] = {node: 0 for node in graph}

        for node in graph:
            for dep in graph[node]:
                # Only count dependencies that are in our graph
                if dep in in_degree:
                    in_degree[node] += 1

        # Start with nodes that have no dependencies
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result: List[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Reduce in-degree for dependent nodes
            for dependent, deps in graph.items():
                if node in deps:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Check for cycles
        if len(result) != len(graph):
            # Find which nodes are in the cycle
            processed = set(result)
            cycle_nodes = [node for node in graph if node not in processed]

            if cycle_nodes:
                raise ValueError(
                    f"Circular dependency detected involving tasks: {', '.join(cycle_nodes[:3])}"
                )

            raise ValueError("Circular dependency detected in task graph")

        return result

    @staticmethod
    def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in the graph.

        Args:
            graph: Dependency graph

        Returns:
            List of cycles (each cycle is a list of task IDs)

        Example:
            >>> graph = {
            ...     "A": ["B"],
            ...     "B": ["C"],
            ...     "C": ["A"],  # Circular!
            ... }
            >>> cycles = DependencyResolver.detect_cycles(graph)
            >>> print(len(cycles))  # 1
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> None:
            """Depth-first search to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    @staticmethod
    def get_ready_tasks(
        tasks: List[Any],
        get_task_id: callable,
        get_dependency_ids: callable,
        get_task_status: callable,
        completed_status: str = "Completed",
    ) -> List[Any]:
        """Find tasks that can be started (all dependencies completed).

        Args:
            tasks: List of task objects
            get_task_id: Function to extract task ID
            get_dependency_ids: Function to extract dependency IDs
            get_task_status: Function to extract task status
            completed_status: Status that means dependencies are satisfied

        Returns:
            List of tasks that are ready to start

        Example:
            >>> ready = DependencyResolver.get_ready_tasks(
            ...     tasks,
            ...     lambda t: t.id,
            ...     lambda t: t.depends_on,
            ...     lambda t: t.status
            ... )
        """
        # Build task map for O(1) lookups
        task_map = {get_task_id(t): t for t in tasks}

        ready_tasks: List[Any] = []

        for task in tasks:
            task_id = get_task_id(task)
            deps = get_dependency_ids(task)

            if deps is None:
                deps = []
            elif isinstance(deps, str):
                deps = [deps]
            elif not isinstance(deps, list):
                deps = list(deps)

            # Check if all dependencies are satisfied
            all_complete = True

            for dep_id in deps:
                dep_task = task_map.get(dep_id)

                if dep_task is None:
                    # Dependency doesn't exist in our task list
                    # Assume it's not completed
                    all_complete = False
                    break

                dep_status = get_task_status(dep_task)

                if dep_status != completed_status:
                    all_complete = False
                    break

            if all_complete and len(deps) > 0:
                # Task has dependencies and all are complete
                ready_tasks.append(task)
            elif len(deps) == 0:
                # Task has no dependencies - also ready
                task_status = get_task_status(task)
                # Only include if not already completed
                if task_status != completed_status:
                    ready_tasks.append(task)

        return ready_tasks

    @staticmethod
    def get_blocked_tasks(
        tasks: List[Any],
        get_task_id: callable,
        get_dependency_ids: callable,
        get_task_status: callable,
        completed_status: str = "Completed",
    ) -> List[Tuple[Any, List[Any]]]:
        """Find tasks that are blocked by incomplete dependencies.

        Args:
            tasks: List of task objects
            get_task_id: Function to extract task ID
            get_dependency_ids: Function to extract dependency IDs
            get_task_status: Function to extract task status
            completed_status: Status that means dependencies are satisfied

        Returns:
            List of (task, blocking_tasks) tuples where blocking_tasks
            are the incomplete dependencies

        Example:
            >>> blocked = DependencyResolver.get_blocked_tasks(
            ...     tasks,
            ...     lambda t: t.id,
            ...     lambda t: t.depends_on,
            ...     lambda t: t.status
            ... )
            >>> for task, blockers in blocked:
            ...     print(f"{task.id} blocked by {[b.id for b in blockers]}")
        """
        # Build task map
        task_map = {get_task_id(t): t for t in tasks}

        blocked: List[Tuple[Any, List[Any]]] = []

        for task in tasks:
            task_id = get_task_id(task)
            deps = get_dependency_ids(task)

            if deps is None:
                deps = []
            elif isinstance(deps, str):
                deps = [deps]
            elif not isinstance(deps, list):
                deps = list(deps)

            if not deps:
                # No dependencies = not blocked
                continue

            # Check for incomplete dependencies
            blocking: List[Any] = []

            for dep_id in deps:
                dep_task = task_map.get(dep_id)

                if dep_task is None:
                    # Dependency doesn't exist - treat as blocker
                    continue

                dep_status = get_task_status(dep_task)

                if dep_status != completed_status:
                    blocking.append(dep_task)

            if blocking:
                blocked.append((task, blocking))

        return blocked

    @staticmethod
    def get_execution_order(
        tasks: List[Any],
        get_task_id: callable,
        get_dependency_ids: callable,
    ) -> List[Any]:
        """Get tasks in dependency execution order.

        Args:
            tasks: List of task objects
            get_task_id: Function to extract task ID
            get_dependency_ids: Function to extract dependency IDs

        Returns:
            List of tasks in execution order

        Raises:
            ValueError: If circular dependencies are detected

        Example:
            >>> ordered = DependencyResolver.get_execution_order(
            ...     tasks,
            ...     lambda t: t.id,
            ...     lambda t: t.depends_on
            ... )
        """
        # Build dependency graph
        graph = DependencyResolver.build_dependency_graph(
            tasks,
            get_task_id,
            get_dependency_ids,
        )

        # Get execution order
        order = DependencyResolver.topological_sort(graph)

        # Build task map and return in order
        task_map = {get_task_id(t): t for t in tasks}

        return [task_map[task_id] for task_id in order if task_id in task_map]
