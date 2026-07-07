"""Unit test untuk bowlplate.share.builtns.handler.decorator"""

import pytest

from bowlplate.share.builtns.handler.decorator import (
    validate_parameter,
    required_parameter,
)


class TestValidateParameter:
    def test_passes_with_correct_types(self):
        @validate_parameter({"name": str, "age": int})
        def greet(name: str, age: int):
            return f"{name} is {age}"

        assert greet("Budi", 20) == "Budi is 20"

    def test_passes_with_keyword_arguments(self):
        @validate_parameter({"name": str})
        def greet(name: str):
            return name

        assert greet(name="Ani") == "Ani"

    def test_raises_valueerror_when_param_missing(self):
        @validate_parameter({"missing_param": str})
        def fn(name: str):
            return name

        with pytest.raises(ValueError):
            fn("x")

    def test_raises_typeerror_when_type_mismatch(self):
        @validate_parameter({"age": int})
        def fn(age):
            return age

        with pytest.raises(TypeError):
            fn("not-an-int")

    @pytest.mark.xfail(
        reason=(
            "When expected_type is a PEP 604 union (e.g. `dict | str`), the "
            "TypeError branch tries to access `expected_type.__name__`, but "
            "types.UnionType has no __name__ attribute, so an AttributeError "
            "is raised instead of the intended TypeError."
        ),
        raises=AttributeError,
        strict=True,
    )
    def test_type_mismatch_message_with_union_type_currently_broken(self):
        @validate_parameter({"data": dict | str})
        def fn(data):
            return data

        with pytest.raises(TypeError):
            fn(123)


class TestRequiredParameter:
    def test_passes_when_all_args_provided(self):
        @required_parameter
        def fn(a, b, c):
            return a + b + c

        assert fn(1, 2, 3) == 6

    def test_passes_when_mixed_args_and_kwargs_complete(self):
        @required_parameter
        def fn(a, b, c):
            return (a, b, c)

        assert fn(1, b=2, c=3) == (1, 2, 3)

    def test_raises_when_argument_missing(self):
        @required_parameter
        def fn(a, b, c):
            return a + b + c

        with pytest.raises(TypeError):
            fn(1, 2)

    def test_raises_when_extra_argument_given(self):
        @required_parameter
        def fn(a, b):
            return a + b

        with pytest.raises(TypeError):
            fn(1, 2, 3)
