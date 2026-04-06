"""
Test to verify Hypothesis setup without requiring database.

These tests verify that Hypothesis is properly installed and configured.
"""

from hypothesis import given, strategies as st, settings, example


@given(st.text(min_size=1, max_size=100))
def test_hypothesis_text_generation(text: str):
    """Test that Hypothesis can generate text strings."""
    assert isinstance(text, str)
    assert len(text) >= 1
    assert len(text) <= 100


@given(st.integers(min_value=0, max_value=1000))
def test_hypothesis_integer_generation(num: int):
    """Test that Hypothesis can generate integers."""
    assert isinstance(num, int)
    assert 0 <= num <= 1000


@given(
    st.lists(st.integers(), min_size=0, max_size=10)
)
def test_hypothesis_list_generation(numbers: list):
    """Test that Hypothesis can generate lists."""
    assert isinstance(numbers, list)
    assert len(numbers) <= 10


@given(
    st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.integers(),
        min_size=0,
        max_size=5
    )
)
def test_hypothesis_dict_generation(data: dict):
    """Test that Hypothesis can generate dictionaries."""
    assert isinstance(data, dict)
    assert len(data) <= 5


@given(st.integers(), st.integers())
def test_commutative_property(a: int, b: int):
    """Test that addition is commutative."""
    assert a + b == b + a


@given(st.lists(st.integers()))
def test_reverse_twice_is_identity(lst: list):
    """Test that reversing a list twice returns the original."""
    assert list(reversed(list(reversed(lst)))) == lst


@given(st.text())
def test_string_length_property(s: str):
    """Test that string length is always non-negative."""
    assert len(s) >= 0


@given(st.lists(st.integers(), min_size=1))
def test_max_is_in_list(numbers: list):
    """Test that max of a list is always in the list."""
    max_val = max(numbers)
    assert max_val in numbers


@given(st.lists(st.integers()))
def test_sorted_list_property(numbers: list):
    """Test that sorted list is in non-decreasing order."""
    sorted_numbers = sorted(numbers)
    
    for i in range(len(sorted_numbers) - 1):
        assert sorted_numbers[i] <= sorted_numbers[i + 1]


@settings(max_examples=50)
@given(st.text(min_size=1))
def test_custom_settings(text: str):
    """Test that custom Hypothesis settings work."""
    # This test runs with 50 examples instead of the default 100
    assert len(text) >= 1


@given(st.integers(min_value=1, max_value=100))
@example(1)  # Always test with 1
@example(100)  # Always test with 100
def test_with_explicit_examples(n: int):
    """Test that explicit examples work alongside generated ones."""
    assert 1 <= n <= 100


def test_hypothesis_is_installed():
    """Test that Hypothesis is properly installed."""
    import hypothesis
    
    # Check version
    version = hypothesis.__version__
    assert version is not None
    
    # Parse version to ensure it's >= 6.100.0
    major, minor, patch = map(int, version.split('.')[:3])
    assert major >= 6
    if major == 6:
        assert minor >= 100
