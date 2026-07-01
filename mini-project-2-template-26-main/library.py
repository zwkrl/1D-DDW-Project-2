from __future__ import annotations
import token
from typing import TypeAlias
from typing import Optional, Any, Iterator

Number: TypeAlias = int | float
NumberList: TypeAlias = list[Number] 

class Stack:
    def __init__(self) -> None:
        self.__items: list[Any] = []
        
    def push(self, item: Any):
        self.__items.append(item)

    def pop(self) -> Any:
        if self.is_empty:
            return None
        else:
            return self.__items.pop()

    def peek(self) -> Any:
        if self.is_empty:
            return None
        return self.__items[-1]

    @property
    def is_empty(self) -> bool:
        if self.size == 0:
            return True
        else:
            return False

    @property
    def size(self):
        return len(self.__items)


class EvaluateExpression:
    valid_char = '0123456789+-*/(). '
    operators = '+-*/()'

    def __init__(self, string=""):
        self.expression = string

    @property
    def expression(self):
        return self._expr

    @expression.setter
    def expression(self, new_expr):
        for char in new_expr:
            if char not in self.valid_char:
                self._expr = ""
                return 
        self._expr = new_expr

    def insert_space(self):
        spaced_expr = self.expression
        for op in self.operators:
            spaced_expr = spaced_expr.replace(op, f" {op} ")
        return spaced_expr

    def process_operator(self, operand_stack, operator_stack):
        operator = operator_stack.pop()
        op_2 = operand_stack.pop()
        op_1 = operand_stack.pop()
        if operator == "+":
            operand_stack.push(op_1 + op_2)
        elif operator == "-":
            operand_stack.push(op_1 - op_2)
        elif operator == "*":
            operand_stack.push(op_1 * op_2)
        elif operator == "/":
            operand_stack.push(op_1 / op_2)


    def evaluate(self):
        if self.expression == "":
            return None
        operand_stack = Stack()
        operator_stack = Stack()
        expression = self.insert_space()
        tokens = expression.split()
        while len(tokens) > 0:
            token = tokens.pop(0)
            if token not in self.operators:
                operand_stack.push(float(token))
            elif token in self.operators:
                if token == "(":
                    operator_stack.push(token)
                elif token == ")":
                    while operator_stack.peek() != "(":
                        self.process_operator(operand_stack, operator_stack)
                    operator_stack.pop()
                elif token == "*" or token == "/":
                    while (not operator_stack.is_empty) and (operator_stack.peek() in "*/") and operand_stack.size >= 2:
                        self.process_operator(operand_stack, operator_stack)
                    operator_stack.push(token)
                elif token == "+" or token == "-":
                    while (not operator_stack.is_empty) and (operator_stack.peek() in "+-*/") and operand_stack.size >= 2:
                        self.process_operator(operand_stack, operator_stack)
                    operator_stack.push(token)
        while not operator_stack.is_empty:
            self.process_operator(operand_stack, operator_stack)
        return operand_stack.pop()