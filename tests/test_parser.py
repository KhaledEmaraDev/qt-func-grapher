import pytest
import numpy as np

from qt_func_grapher.arithmetic_parser import ArithmeticParser


class TestValidation:
    def test_too_many_closing_parantheses(self):
        arithmetic_parser = ArithmeticParser("(3 + 2))^2")
        with pytest.raises(SyntaxError):
            arithmetic_parser.parse()

    def test_too_many_few_parantheses(self):
        arithmetic_parser = ArithmeticParser("2^((2)")
        with pytest.raises(SyntaxError):
            arithmetic_parser.parse()

    def test_unkown_variable(self):
        arithmetic_parser = ArithmeticParser("z + 10")
        with pytest.raises(NameError):
            arithmetic_parser.parse()


class TestEvaluation:
    def test_missing_operand(self):
        arithmetic_parser = ArithmeticParser("3 + ")
        with pytest.raises(ValueError):
            arithmetic_parser.parse()
            arithmetic_parser.evaluate(np.ones(5))

    def test_variable_substitution(self):
        arithmetic_parser = ArithmeticParser("3 + x")
        with pytest.raises(ValueError):
            arithmetic_parser.parse()
            assert arithmetic_parser.evaluate(np.linspace(1, 5, 5)) == np.array(
                [4.0, 5.0, 6.0, 7.0, 8.0]
            )

    def test_operator_precedence(self):
        arithmetic_parser = ArithmeticParser("3 + x * 2")
        with pytest.raises(ValueError):
            arithmetic_parser.parse()
            assert arithmetic_parser.evaluate(np.linspace(1, 5, 5)) == np.array(
                [5.0, 7.0, 9.0, 11.0, 13.0]
            )

    def test_parantheses(self):
        arithmetic_parser = ArithmeticParser("(3 + x) * 2")
        with pytest.raises(ValueError):
            arithmetic_parser.parse()
            assert arithmetic_parser.evaluate(np.linspace(1, 5, 5)) == np.array(
                [8.0, 10.0, 12.0, 14.0, 16.0]
            )
