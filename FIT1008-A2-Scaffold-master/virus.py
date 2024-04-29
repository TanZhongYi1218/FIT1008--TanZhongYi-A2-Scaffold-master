from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries
from branch_decision import BranchDecision


class VirusType(ABC):

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    @abstractmethod
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        raise NotImplementedError()


class TopVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the top branch
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the bottom branch
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.
        Time complexity: O(1), as it only checks the first computer of each branch.
        """
        # Check if the first route in both branches is a RouteSeries
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        # If both branches have a RouteSeries
        if top_route and bot_route:
            # Get the computer from both branches
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            # Compare the hacking difficulty of both computers
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
        Selects a branch based on the risk factors and hacking difficulties of the computers in the branches.
        Time complexity: O(1), as it only checks the first computer of each branch.
        """
        # Check if the first route in both branches is a RouteSeries
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        # If both branches have a RouteSeries
        if top_route and bot_route:
            # Get the computer from both branches
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            # Calculate the value for both computers based on the hacking difficulty, hacked value, and risk factor
            top_value = max(top_comp.hacking_difficulty, top_comp.hacked_value / 2) / (top_comp.risk_factor if top_comp.risk_factor != 0 else 1)
            bot_value = max(bot_comp.hacking_difficulty, bot_comp.hacked_value / 2) / (bot_comp.risk_factor if bot_comp.risk_factor != 0 else 1)

            # Compare the calculated values
            if top_value > bot_value:
                return BranchDecision.TOP
            elif top_value < bot_value:
                return BranchDecision.BOTTOM
            else:
                # If the values are equal, compare the risk factors
                return BranchDecision.STOP if top_comp.risk_factor == bot_comp.risk_factor else (BranchDecision.TOP if top_comp.risk_factor < bot_comp.risk_factor else BranchDecision.BOTTOM)
        elif top_route:
            return BranchDecision.BOTTOM
        else:
            return BranchDecision.TOP


class FancyVirus(VirusType):
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def calculate_threshold(self, calc_str: str) -> float:
        """
        Calculates a threshold using reverse polish notation.
        Time complexity: O(N), where N is the number of elements in the calculation string.
        """
        # Initialize an empty stack
        stack = []
        # Split the calculation string into tokens
        for token in calc_str.split():
            # If the token is an operator
            if token in "+-*/":
                # Pop the last two numbers from the stack
                num2 = stack.pop()
                num1 = stack.pop()
                # Perform the operation and push the result back to the stack
                if token == '+':
                    stack.append(num1 + num2)
                elif token == '-':
                    stack.append(num1 - num2)
                elif token == '*':
                    stack.append(num1 * num2)
                else:
                    stack.append(num1 / num2)
            else:
                # If the token is a number, push it to the stack
                stack.append(float(token))
        # Return the last number in the stack
        return stack.pop()

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Selects a branch based on a calculated threshold.
        Time complexity: O(1), as it only checks the first computer of each branch.
        """
        # Calculate the threshold
        threshold = self.calculate_threshold(self.CALC_STR)

        # Check if the first route in both branches is a RouteSeries
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        # If both branches have a RouteSeries
        if top_route and bot_route:
            # Get the computer from both branches
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            # Compare the hacked value of both computers with the threshold
            if top_comp.hacked_value < threshold:
                return BranchDecision.TOP
            elif bot_comp.hacked_value > threshold:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP
        elif top_route:
            return BranchDecision.BOTTOM
        else:
            return BranchDecision.TOP
