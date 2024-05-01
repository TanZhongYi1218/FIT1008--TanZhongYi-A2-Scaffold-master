from __future__ import annotations
from dataclasses import dataclass

from computer import Computer

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from virus import VirusType

from branch_decision import BranchDecision
from data_structures.linked_stack import LinkedStack


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
        return RouteSeries(computer, Route(RouteSeries(self.computer, self.following)))

    def add_computer_after(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, following=Route(RouteSeries(computer, self.following)))

    def add_empty_branch_before(self) -> RouteStore:
        """Returns a route store which would be the result of:
        Adding an empty branch, where the current routestore is now the following path.
        """
        return RouteSplit(Route(), Route(), Route(RouteSeries(self.computer, self.following)))

    def add_empty_branch_after(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch after the current computer, but before the following route.
        """
        return RouteSeries(self.computer, following=Route(
            store=RouteSplit(
                top=Route(store=None),
                bottom=Route(store=None),
                following=self.following)))


RouteStore = Union[RouteSplit, RouteSeries, None]


@dataclass
class Route:
    store: RouteStore = None

    def add_computer_before(self, computer: Computer) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding a computer before everything currently in the route.
        """
        return Route(RouteSeries(computer, Route(self.store)))

    def add_empty_branch_before(self) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding an empty branch before everything currently in the route.
        """
        return Route(store=RouteSplit( \
            top=Route(store=None), \
            bottom=Route(store=None), \
            following=Route(store=None) \
            ))

    def follow_path(self, virus: VirusType) -> None:
        """Follow a path and add computers according to a virus type."""
        current = self
        stop = False
        post_path_computers = LinkedStack()

        while True:
            if isinstance(current.store, RouteSplit):
                current = current.store
                branch_decision = virus.select_branch(current.top, current.bottom)

                # Handle nested RouteSeries within RouteSplit
                self.process_route_series(current.following, post_path_computers, virus)

                if branch_decision == BranchDecision.TOP:
                    current = self.process_branch(current.top, virus)
                    if current is None:
                        break
                elif branch_decision == BranchDecision.BOTTOM:
                    current = self.process_branch(current.bottom, virus)
                    if current is None:
                        break
                elif branch_decision == BranchDecision.STOP:
                    stop = True
                    break

            elif isinstance(current.store, RouteSeries):
                virus.add_computer(current.store.computer)
                current = current.store.following

            else:
                break

        # Add any computers found in post path processing
        while not post_path_computers.is_empty() and not stop:
            virus.add_computer(post_path_computers.pop())

    def process_route_series(self, route, stack, virus):
        """Process a nested RouteSeries and add computers to a stack."""
        while isinstance(route.store, RouteSeries):
            stack.push(route.store.computer)
            route = route.store.following

    def process_branch(self, branch, virus):
        """Process a branch decision and return the next path or None if end."""
        if isinstance(branch.store, RouteSeries):
            virus.add_computer(branch.store.computer)
            return branch.store.following
        elif isinstance(branch.store, RouteSplit):
            return branch
        return None

    def add_all_computers(self) -> list[Computer]:
        """Returns a list of all computers on the route."""
        route = self
        return self.add_all_computers_aux(self, [])

    def add_all_computers_aux(self, route: Route, computer_list: list[Computer]):
        if route.store == None:
            return

        elif isinstance(route.store, RouteSeries):
            computer_list.append(route.store.computer)
            route = route.store.following
            self.add_all_computers_aux(route, computer_list)

        elif isinstance(route.store, RouteSplit):
            self.add_all_computers_aux(route.store.top, computer_list)
            self.add_all_computers_aux(route.store.bottom, computer_list)
            self.add_all_computers_aux(route.store.following, computer_list)

        return computer_list
