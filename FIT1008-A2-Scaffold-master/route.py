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
        """
        Follow a path and add computers according to a virus_type.
        It has a time complexity of O(N), where N is the number of elements in the route.
        This is because the function traverses the route once, visiting each element exactly once.
        The operations inside the loop (checking the type of the current route and adding a computer
        to the virus) are constant time operations, so they do not affect the overall time complexity.
        """
        current_route = self  # Start from the current route
        while current_route.store is not None:  # Continue until the end of the route
            if isinstance(current_route.store, RouteSeries):  # If the current route is a RouteSeries
                virus_type.add_computer(current_route.store.computer)  # Add the computer to the virus
                current_route = current_route.store.following  # Move to the next route
            elif isinstance(current_route.store, RouteSplit):  # If the current route is a RouteSplit
                decision = virus_type.select_branch(current_route.store.top,
                                                    current_route.store.bottom)  # Decide which branch to take
                if decision == BranchDecision.TOP:  # If the decision is to take the top branch
                    current_route = current_route.store.top  # Move to the top branch
                elif decision == BranchDecision.BOTTOM:  # If the decision is to take the bottom branch
                    current_route = current_route.store.bottom  # Move to the bottom branch
                else:  # If the decision is to stop
                    break  # Stop following the path

    def add_all_computers(self) -> list[Computer]:
        """
        Returns a list of all computers on the route.
        It has a time complexity of O(N), where N is the number of elements in the route.
        Similar to the follow_path function, this function also traverses the route once,
        visiting each element exactly once. The operations inside the loop (checking the type of
        the current route and adding a computer to the list) are constant time operations,
        so they do not affect the overall time complexity.
        """
        computers = []  # Initialize an empty list to store the computers
        current_route = self  # Start from the current route
        while current_route.store is not None:  # Continue until the end of the route
            if isinstance(current_route.store, RouteSeries):  # If the current route is a RouteSeries
                computers.append(current_route.store.computer)  # Add the computer to the list
                current_route = current_route.store.following  # Move to the next route
            elif isinstance(current_route.store, RouteSplit):  # If the current route is a RouteSplit
                # Add computers from both branches
                computers.extend(current_route.store.top.add_all_computers())  # Add computers from the top branch
                computers.extend(current_route.store.bottom.add_all_computers())  # Add computers from the bottom branch
                current_route = current_route.store.following  # Move to the next route
        return computers  # Return the list of computers
