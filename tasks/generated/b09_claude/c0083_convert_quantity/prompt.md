```python
def convert_quantity(text: str, target: str) -> str:
    """Convert a physical quantity like "12.5 kN*m/s^2" into the unit `target`.

    `text` is <number> + exactly one space + <units>; `target` is <units>.
    <number>: optional "-", ASCII digits, optional "." + digits, optional
    exponent "e"/"E" + optional sign + digits ("2.5e-3"). Parse it EXACTLY.
    <units>: factors joined by "*" or "/" (no spaces). Evaluate left to right
    like arithmetic: "a/b*c" is (a/b)*c, and "a/b/c" is a/(b*c). The first
    factor may be the literal "1" (as in "1/s"); every other factor is
    SYMBOL optionally followed by "^" and a nonzero integer ("^2", "^-1").

    Units (scale to SI, dimension):
      m metre; g gram = 0.001 kg; s second; A ampere; K kelvin; mol; cd
      N = kg*m/s^2; Pa = N/m^2; J = N*m; W = J/s; Hz = 1/s; bar = 100000 Pa;
      L litre = 0.001 m^3; min = 60 s; h hour = 3600 s.
    Prefixes: G 1e9, M 1e6, k 1e3, h 1e2, d 1e-1, c 1e-2, m 1e-3, u 1e-6, n 1e-9.
    A SYMBOL is first looked up as a whole unit name; only if that fails is it
    read as one prefix letter + a unit name. Prefixes are not allowed on
    "min" and "h". So "h" is an hour, "hPa" is hectopascal, "mm" is millimetre.
    An exponent applies to the prefixed unit: "cm^2" is (0.01 m)^2.

    Convert exactly, then round to 9 decimal places with ties to EVEN; remove
    trailing zeros and a trailing "."; never "-0". No exponent notation.
    Raise ValueError for malformed input, unknown symbols, or when the
    dimensions of `text` and `target` differ.

    >>> convert_quantity("1 km/h", "m/s")
    '0.277777778'
    >>> convert_quantity("3 kg*m/s^2", "N")
    '3'
    """
```
