from __future__ import annotations
from dataclasses import dataclass
from branch_decision import BranchDecision

from computer import Computer

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from virus import VirusType


@dataclass
class RouteSplit:
    """
    A split in the route.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Route
    bottom: Route
    following: Route

    def remove_branch(self) -> RouteStore:
        """Removes the branch, should just leave the remaining following route."""
        return self.following.store

@dataclass
class RouteSeries:
    """
    A computer, followed by the rest of the route

    --computer--following--

    """

    computer: Computer
    following: Route

    def remove_computer(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Removing the computer at the beginning of this series.
        """
        return self.following.store

    def add_computer_before(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer in series before the current one.
        """
        return RouteSeries(computer, Route(self))

    def add_computer_after(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, Route(RouteSeries(computer, self.following)))

    def add_empty_branch_before(self) -> RouteStore:
        """Returns a route store which would be the result of:
        Adding an empty branch, where the current routestore is now the following path.
        """
        return RouteSplit(Route(None), Route(None), Route(self))

    def add_empty_branch_after(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, Route(RouteSplit(Route(None), Route(None), self.following)))


RouteStore = Union[RouteSplit, RouteSeries, None]

@dataclass
class Route:

    store: RouteStore = None

    def add_computer_before(self, computer: Computer) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding a computer before everything currently in the route.
        """
        return Route(RouteSeries(computer, self))

    def add_empty_branch_before(self) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding an empty branch before everything currently in the route.
        """
        return Route(RouteSplit(Route(None), Route(None), self))

    def follow_path(self, virus_type: VirusType) -> None:
        """Follow a path and add computers according to a virus_type."""
        current_route = self
        while current_route.store is not None:
            if isinstance(current_route.store, RouteSeries):
                virus_type.add_computer(current_route.store.computer)
                current_route = current_route.store.following
            elif isinstance(current_route.store, RouteSplit):
                decision = virus_type.select_branch(current_route.store.top, current_route.store.bottom)
                if decision == BranchDecision.TOP:
                    current_route = current_route.store.top
                elif decision == BranchDecision.BOTTOM:
                    current_route = current_route.store.bottom
                else:
                    break

    def add_all_computers(self) -> list[Computer]:
        """Returns a list of all computers on the route."""
        computers = []
        current_route = self
        while current_route.store is not None:
            if isinstance(current_route.store, RouteSeries):
                computers.append(current_route.store.computer)
                current_route = current_route.store.following
            elif isinstance(current_route.store, RouteSplit):
                # Add computers from both branches
                computers.extend(current_route.store.top.add_all_computers())
                computers.extend(current_route.store.bottom.add_all_computers())
                current_route = current_route.store.following
        return computers
