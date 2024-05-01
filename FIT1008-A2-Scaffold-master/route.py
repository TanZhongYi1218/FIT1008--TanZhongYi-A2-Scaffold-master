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
        """Follow a path and add computers according to a virus_type."""
        path = self
        stop = False
        following_items_stack = LinkedStack()

        dispatch_table = {
            RouteSplit: self.handle_route_split,
            RouteSeries: self.handle_route_series,
            None: self.handle_none_type
        }

        while True:
            handler = dispatch_table.get(type(path.store))
            if handler:
                stop, path = handler(path, virus, following_items_stack)
            if stop:
                break

        while not following_items_stack.is_empty() and not stop:
            virus.add_computer(following_items_stack.pop())

    def handle_route_split(self, path, virus, following_items_stack):
        path = path.store
        branch_decision = virus.select_branch(path.top, path.bottom)

        if isinstance(path.following.store, RouteSeries) and isinstance(path.following.store.computer, Computer):
            self.populate_following_items_stack(path, following_items_stack)

        if branch_decision == BranchDecision.TOP:
            path = self.handle_top_decision(path)
        elif branch_decision == BranchDecision.BOTTOM:
            path = self.handle_bottom_decision(path)
        elif branch_decision == BranchDecision.STOP:
            return True, path

        return False, path

    def handle_route_series(self, path, virus, following_items_stack):
        virus.add_computer(path.store.computer)
        return False, path.store.following

    def handle_none_type(self, path, virus, following_items_stack):
        return True, path

    def populate_following_items_stack(self, path, following_items_stack):
        """
        Populate the following_items_stack based on the path.
        """
        if isinstance(path.following.store, RouteSeries) and isinstance(path.following.store.computer, Computer):
            following_items_stack.push(path.following.store.computer)

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
