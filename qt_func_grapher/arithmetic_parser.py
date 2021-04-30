import re
from collections import deque

import numpy as np


class _BinaryTreeNode:
    """
    Expression Tree representation in the form of a Binary Tree.

    ...

    Attributes
    ----------
    token : str_or_float
        A token to represent the operation or operand
    left : _BinaryTreeNode
        The left node
    right : _BinaryTreeNode
        The right node

    Methods
    -------
    evaulate(x)
        Get the value of the node and its children after applying all
        operations
    """

    def __init__(self, token):
        """
        Parameters
        ----------
        token : str_or_float
            A token to represent the operation or operand
        """

        self.token = token
        self.left = None
        self.right = None

    def __str__(self):
        res = ""
        if self.left:
            res += str(self.left)

        res += str(self.token)

        if self.right:
            res += str(self.right)

        return res

    def getToken(self):
        return self.token

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def setToken(self, token):
        self.token = token

    def insertLeft(self, token):
        self.left = _BinaryTreeNode(token)

    def insertRight(self, token):
        self.right = _BinaryTreeNode(token)

    def evaluate(self, x):
        """Get the value of the node and its cildren after applying all operations

        The tree is walked in a DFS fashion and the value of x replaces the
        variable "x".

        Parameters
        ----------
        x : numpy.array
            The with which to replace the variable

        Returns
        -------
        numpy.array
            The value of the node after applying all the operations to itsef
            and its children

        Raises
        ------
        ValueError
            If an operand is missing
        """

        # Dictionary defining the operation associated with each token
        ops = {
            "+": np.add,
            "-": np.subtract,
            "*": np.multiply,
            "/": np.divide,
            "^": np.power,
        }

        left_operand = self.getLeft()
        right_operand = self.getRight()

        if left_operand and right_operand:
            # Token is an operation
            fn = ops[self.getToken()]
            return fn(left_operand.evaluate(x), right_operand.evaluate(x))
        elif left_operand:
            # Token is "=" and is equal to its left node value
            return left_operand.evaluate(x)
        elif self.getToken() != "=":
            # Token is an operand
            if self.getToken() == "x":
                return x
            else:
                return self.getToken()
        else:
            raise ValueError("Missing Operand")


class ArithmeticParser:
    """
    A class that parses the user enterd function and forms an expression tree
    out of it

    ...

    Attributes
    ----------
    expr : str
        The string representation of the function
    lexems : list
        A list of lexems after preprocessing and tockenizing the expressions
    ast : _BinaryTreeNode
        The root node of the Expression Tree

    Methods
    -------
    parse()
        Parse the expression and convert it into an Expression Tree
    evaluate(x)
        Calls the evaluate method on the root node
    """

    def __init__(self, expression):
        self.expr = expression

    def _insertParanthesesAround(self, index):
        """Wrap an operation by parantheses to prioritize it

        Uses a LIFO fashion to walk parantheses in order to avoid overriding
        previous wrappings or parantheses inputted by the user.

        Raises
        ------
        SyntaxError
            If the number of opening and closing parantheses don't match
        """

        parantheses_count = 0

        # Insert an opening parenthesis
        for ptr in range(index - 1, -1, -1):
            if self.lexems[ptr] == ")":
                parantheses_count += 1
                continue
            elif self.lexems[ptr] == "(":
                parantheses_count -= 1

            if parantheses_count == 0:
                self.lexems.insert(ptr, "(")
                break

        if parantheses_count != 0:
            raise SyntaxError("Too many closing parantheses")

        # Insert a closing parenthesis at the end of the expression
        if index + 2 >= len(self.lexems):
            self.lexems.insert(index + 2, ")")
            return

        # Insert a closing parenthesis
        for ptr in range(index + 2, len(self.lexems), 1):
            if self.lexems[ptr] == "(":
                parantheses_count += 1
                continue
            elif self.lexems[ptr] == ")":
                parantheses_count -= 1

            if parantheses_count == 0:
                self.lexems.insert(ptr + 1, ")")
                break

        if parantheses_count != 0:
            raise SyntaxError("Too few closing parantheses")

    def _preprocess(self):
        """Give more important operations precendence.

        Wraps more important operations with parantheses first.
        """

        # Wrap ^ first
        pow_indices = [i for i, el in enumerate(self.lexems) if el == "^"]
        for i in range(len(pow_indices)):
            self._insertParanthesesAround(pow_indices[i] + 2 * i)

        # Wrap *,/ second
        mul_indices = [i for i, el in enumerate(self.lexems) if el in ["*", "/"]]
        for i in range(len(mul_indices)):
            self._insertParanthesesAround(mul_indices[i] + 2 * i)

        # Wrap +,- last (optional)
        add_indices = [i for i, el in enumerate(self.lexems) if el in ["+", "-"]]
        for i in range(len(add_indices)):
            self._insertParanthesesAround(add_indices[i] + 2 * i)

    def _tockenize(self):
        """Split the string into lexemes

        Uses regex to split the expressions into lexemes of operations and
        operands based on operations.
        """

        self.expr = self.expr.replace(" ", "")
        self.lexems = [
            token for token in re.split(r"([\+\-\*\/\^\(\)])", self.expr) if token != ""
        ]
        self._preprocess()

    def parse(self):
        """Parse the expression and converts it into an Expression Tree

        Uses a LIFO structure (deque) to create a new frame (node) each time
        parantheses are opened

        Raises
        ------
        SyntaxError
            If the experssion is unparsable
        NameError
            If an unkown lexeme is encountered
        """

        nodes_stack = deque()
        ast = _BinaryTreeNode("=")
        current_node = ast

        self._tockenize()

        for tk in self.lexems:
            # Push a new frame (node)
            if tk == "(":
                if not current_node.getLeft():
                    current_node.insertLeft("=")
                    nodes_stack.append(current_node)
                    current_node = current_node.getLeft()
                else:
                    current_node.insertRight("=")
                    current_node = current_node.getRight()

            # Change operation of current node
            elif tk in ["+", "-", "*", "/", "^"]:
                current_node.setToken(tk)
                current_node.insertRight("=")
                current_node = current_node.getRight()

            # Pop to parent node if it has space for operands
            elif tk == ")":
                if len(nodes_stack) > 0:
                    current_node = nodes_stack.pop()

            # Add x as an operand
            elif tk == "x":
                current_node.insertLeft(tk)

            # Add number as operand
            else:
                try:
                    value = float(tk)
                except ValueError:
                    raise NameError(f"Unknown variable ('{tk}')")

                current_node.insertLeft(value)

        if len(nodes_stack) > 0:
            raise SyntaxError("Too few closing parantheses")

        self.ast = ast

    def evaluate(self, x):
        return self.ast.evaluate(x)


# def eval_expression(expression, x):
#     allowed_names = {"x": x}
#     code = compile(expression, "<string>", "eval")
#     for name in code.co_names:
#         if name not in allowed_names:
#             raise NameError(f"Use of {name} not allowed")

#     return eval(code, {"__builtins__": {}}, allowed_names)
