```python
def word_frequency(text: str, stop_words: list[str], min_letters: int, k: int) -> list[tuple[str, int]]:
    """The k most frequent words of a text.

    A word is one or more runs of ASCII letters (A-Z, a-z) joined by single
    connectors, where a connector is an apostrophe "'" or a hyphen "-" with a
    letter immediately on both sides: "don't", "well-known" and "rock'n'roll"
    are single words. Everything else separates words, including digits,
    non-ASCII letters, a doubled connector ("well--known" is two words) and a
    connector at the start or end of a run ("'quoted'" gives "quoted",
    "dogs'" gives "dogs").

    Words are compared after lowercasing their ASCII letters. Then, in order:
    1. drop the word if it equals a stop word (stop words are lowercased the
       same way; only whole words are dropped: "re-use" is not dropped by "re");
    2. drop the word if it has fewer than `min_letters` LETTERS (connectors do
       not count: "a-b" has 2 letters).

    Return the k most common remaining words as (word, count), sorted by count
    descending, then word ascending (plain string order). Fewer than k distinct
    words: return them all. k <= 0: return [].

    >>> word_frequency("The cat's toy; the CAT's toy -- the end!", ["the"], 3, 2)
    [("cat's", 2), ('toy', 2)]
    """
```
