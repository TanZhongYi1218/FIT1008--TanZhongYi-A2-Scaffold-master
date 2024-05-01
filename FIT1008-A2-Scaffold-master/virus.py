from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries, RouteSplit
from branch_decision import BranchDecision
from data_structures.linked_stack import LinkedStack


class VirusType(ABC):
    # NOTE: Unless stated otherwise, time complexity for each method of t
    #       his class is measured with respect to its input size.
    #

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    @abstractmethod
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        pass


class TopVirus(VirusType):
    # NOTE: Time complexity for each method of this class is measured with respect to its
    #       input size.

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the top branch
        # Time Complexity (Best and Worst): O(1)
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the bottom branch
        # Time Complexity (Best and Worst): O(1)
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.
        Time Complexity (Best and Worst): O(1)
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                return BranchDecision.TOP
            elif top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP
        # If one of them has a computer, don't take it.
        # If neither do, then take the top branch.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP


class RiskAverseVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus is risk averse and likes to choose the path with the lowest risk factor.

        isinstance: A method which compares whether the (data type/ class) of an object
        is the same as the given (data type/ class).
        max: A method which returns the highest among the input values.

        Time Complexity:
            Best: O(isinstance), when the RouteStore (data type/ class) of one of the branches
            is not RouteSeries (data type/ class).
            Worst: O(isinstance + max), when both branches have the same RouteStore (data type/ class)
            which are RouteSeriers (data type/ class).
        """

        # Checks whether both RouteStore classes are RouteSeries.
        if isinstance(top_branch.store, RouteSeries) and isinstance(bottom_branch.store, RouteSeries):  # O(isinstance)

            # Checks whether one of computers have a risk factor of 0.0.
            if top_branch.store.computer.risk_factor == 0.0 or bottom_branch.store.computer.risk_factor == 0.0:
                if top_branch.store.computer.risk_factor == 0.0 and bottom_branch.store.computer.risk_factor == 0.0:
                    if top_branch.store.computer.hacking_difficulty < bottom_branch.store.computer.hacking_difficulty:
                        return BranchDecision.TOP
                    elif top_branch.store.computer.hacking_difficulty > bottom_branch.store.computer.hacking_difficulty:
                        return BranchDecision.BOTTOM

                elif top_branch.store.computer.risk_factor == 0.0:
                    return BranchDecision.TOP
                elif bottom_branch.store.computer.risk_factor == 0.0:
                    return BranchDecision.BOTTOM

            highest_value_top_branch = max(top_branch.store.computer.hacking_difficulty,
                                           (top_branch.store.computer.hacked_value / 2))  # O(max)
            highest_value_bottom_branch = max(bottom_branch.store.computer.hacking_difficulty,
                                              (bottom_branch.store.computer.hacked_value / 2))

            highest_value_top_branch = self.divide_by_risk_factor(top_branch.store.computer.risk_factor,
                                                                  highest_value_top_branch)
            highest_value_bottom_branch = self.divide_by_risk_factor(bottom_branch.store.computer.risk_factor,
                                                                     highest_value_bottom_branch)

            if highest_value_top_branch > highest_value_bottom_branch:
                return BranchDecision.TOP

            elif highest_value_top_branch < highest_value_bottom_branch:
                return BranchDecision.BOTTOM

            if top_branch.store.computer.risk_factor < bottom_branch.store.computer.risk_factor:
                return BranchDecision.TOP

            elif top_branch.store.computer.risk_factor > bottom_branch.store.computer.risk_factor:
                return BranchDecision.BOTTOM
            return BranchDecision.STOP

        elif isinstance(top_branch.store, RouteSplit):
            return BranchDecision.TOP

        elif isinstance(bottom_branch.store, RouteSplit):
            return BranchDecision.BOTTOM
        return BranchDecision.TOP

    def divide_by_risk_factor(self, risk_factor: float, value: float | int) -> float:
        '''
        Divides the highest value of a branch by the risk factor of the branch computer.

        Time Complexity (Best/ Worst) = O(1)
        '''
        if risk_factor != 0:
            value = value / risk_factor
        return value


class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus has a fancy-pants and likes to overcomplicate its approach.

        n: Number of characters in CALC_STAR

        Time Complexity (Best and Worst): O(n)
        """
        oper_stack = LinkedStack()
        operations_list = FancyVirus.CALC_STR.split()
        for token in operations_list:
            if token in ['+', '-', '*', '/']:
                num1 = oper_stack.pop()
                num2 = oper_stack.pop()
                res = eval(str(num2) + token + str(num1))
                oper_stack.push(res)
            else:
                oper_stack.push(token)
        threshold = oper_stack.pop()

        if isinstance(top_branch.store, RouteSeries) and isinstance(bottom_branch.store, RouteSeries):
            if isinstance(top_branch.store.computer, Computer) and isinstance(bottom_branch.store.computer, Computer):
                if top_branch.store.computer.hacked_value < threshold:
                    return BranchDecision.TOP

                elif bottom_branch.store.computer.hacked_value > threshold:
                    return BranchDecision.BOTTOM
                return BranchDecision.STOP

        elif isinstance(top_branch, RouteSplit):
            return BranchDecision.TOP

        elif isinstance(bottom_branch, RouteSplit):
            return BranchDecision.BOTTOM
        return BranchDecision.TOP
