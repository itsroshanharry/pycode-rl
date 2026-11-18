"""Writes pipeline/prompts/seeds.jsonl: real-world rules that ground task generation.

Seeds are short descriptions of real conventions (formats, standards, business rules),
not problems. Classic benchmark puzzles (FizzBuzz, two-sum, Luhn, palindromes...) are
deliberately absent. Run: uv run python pipeline/prompts/make_seeds.py
"""

import json
from pathlib import Path

SEEDS = [
    # dates & time
    ("dates", "ISO-8601 week numbering: week 1 contains the year's first Thursday; weeks start Monday"),
    ("dates", "RFC 3339 timestamps with numeric UTC offsets (e.g. 2024-03-01T10:00:00+05:30) compared or normalized to UTC"),
    ("dates", "Business-day arithmetic: add N working days skipping weekends and a given holiday list"),
    ("dates", "Cron-style schedule fields (minute hour day-of-month month day-of-week) with lists, ranges and */step"),
    ("dates", "Recurring monthly billing dates clamped to month end (Jan 31 -> Feb 28/29 -> Mar 31)"),
    ("dates", "Wall-clock gaps and overlaps given an explicit UTC-offset change table (no tz database)"),
    ("dates", "Human duration formatting: seconds to '2h 5m' style strings with largest-unit rounding rules"),
    ("dates", "Fiscal year / quarter labelling where the fiscal year starts in a configurable month"),
    ("dates", "Age in full years on a date, with Feb 29 birthdays treated as Mar 1 in non-leap years"),
    ("dates", "Common free slots of minimum length from several people's busy intervals within working hours"),
    # versions & identifiers
    ("identifiers", "Semantic Versioning 2.0 precedence including pre-release identifiers and ignored build metadata"),
    ("identifiers", "Version range expressions with comparators, AND-ed by spaces and OR-ed by '||' (npm-like subset)"),
    ("identifiers", "IBAN structure check: country length table, move first four chars, letters to numbers, mod 97 == 1"),
    ("identifiers", "ISBN-10 and ISBN-13 conversion and check-digit validation (X as 10 for ISBN-10)"),
    ("identifiers", "UUID string normalization: accept braces/urn/no-dash forms, output canonical lowercase 8-4-4-4-12"),
    ("identifiers", "Natural sort order for file names: digit runs compared numerically, case-insensitive, stable tie-break"),
    ("identifiers", "Resolving Python relative imports (from ..a import b) against the importing module's package path"),
    ("identifiers", "Slug generation from titles: given transliteration map, collapsed separators, max length at a word boundary"),
    # text formats
    ("text-formats", "CSV field parsing with quotes, doubled quotes inside quotes, and a configurable delimiter"),
    ("text-formats", "INI files with [sections], key=value, ; comments, and duplicate keys where the last wins"),
    ("text-formats", "URL query strings: percent-decoding, '+' as space, repeated keys collected into lists"),
    ("text-formats", "HTTP Accept header with q-values: choose the best match among offered media types incl. wildcards"),
    ("text-formats", "Markdown headings to a nested, numbered table of contents (1, 1.1, 1.2, 2)"),
    ("text-formats", "Dotenv files: export prefix, single/double quotes, escapes in double quotes, inline comments"),
    ("text-formats", "Unified diff hunk headers (@@ -a,b +c,d @@) and applying one hunk to a list of lines"),
    ("text-formats", "Template strings with ${name} and ${name:-default} substitution and $$ as a literal dollar"),
    ("text-formats", "Log lines in a fixed format with optional fields, aggregated into counts by level and minute"),
    ("text-formats", "Roman numerals restricted to the strict subtractive standard (reject IIII, IC, VX)"),
    ("text-formats", "Fixed-width record layouts: slice fields by a column spec, trim padding, convert typed fields"),
    ("text-formats", "Number formatting with explicitly given locale rules (group separator, decimal mark, grouping size)"),
    # structured data
    ("structured-data", "JSON Pointer (RFC 6901) lookup including ~0 and ~1 escapes and array indices"),
    ("structured-data", "Deep merge of nested dicts where lists are replaced, None deletes a key, and conflicts follow a policy"),
    ("structured-data", "Flatten nested dicts to dotted keys and back, with list indices as [i] segments"),
    ("structured-data", "Diff two flat records into added/removed/changed key lists in sorted order"),
    ("structured-data", "Schema-lite validation: type names, required keys, numeric min/max, returning error paths"),
    ("structured-data", "Environment-variable overrides of nested config using a prefix and double-underscore nesting"),
    ("structured-data", "Ordering config files by their includes, reporting the offending chain on a cycle"),
    ("structured-data", "Feature-flag rollout: deterministic percentage bucketing of user ids via a specified hash"),
    # business rules
    ("business-rules", "Progressive income tax with brackets and a personal allowance that tapers above a threshold"),
    ("business-rules", "Splitting a bill among people by weights in integer cents, distributing leftover cents deterministically"),
    ("business-rules", "Loan amortization schedule with a fixed payment, per-period rounding, final payment absorbing drift"),
    ("business-rules", "Shipping cost from a weight/zone rate table with dimensional weight and a free-shipping threshold"),
    ("business-rules", "Loyalty points expiring first-in-first-out after N days, redeeming from the oldest batch first"),
    ("business-rules", "Discount stacking: percentage vs fixed coupons, exclusivity groups, total never below zero"),
    ("business-rules", "Currency conversion through pairwise rates, finding a path when no direct rate exists"),
    ("business-rules", "Inventory reservation: allocate orders to warehouses by priority with partial fulfilment"),
    ("business-rules", "Payroll overtime with daily and weekly thresholds, the higher rate winning per hour"),
    ("business-rules", "Invoice tax rounding per line vs per invoice and the resulting difference"),
    ("business-rules", "Subscription proration when upgrading mid-cycle, with credit for unused time"),
    ("business-rules", "Sales commission tiers applied marginally over a period"),
    # scheduling & allocation
    ("scheduling", "Meeting room assignment: minimal number of rooms and a concrete assignment preferring the lowest room index"),
    ("scheduling", "Round-robin tournament schedule (circle method) with byes for an odd number of teams"),
    ("scheduling", "Shift rotation pattern repeated over a period, counting hours per worker around holidays"),
    ("scheduling", "Job queue with priorities, FIFO within a priority, and aging that bumps long-waiting jobs"),
    ("scheduling", "Token-bucket rate limiter deciding accept/reject for timestamped requests"),
    ("scheduling", "Sliding-window rate limit per client key with a window length and a max count"),
    ("scheduling", "Elevator requests served in SCAN order from a start floor and direction"),
    ("scheduling", "Exam timetabling so no student sits two exams at once, greedy by most-constrained exam"),
    ("scheduling", "Retry schedule with exponential backoff, deterministic jitter sequence, and a cap"),
    ("scheduling", "Dependency-aware build order grouped into parallel waves"),
    # games & scoring
    ("games", "Ten-pin bowling score from a roll list including strikes, spares and the tenth-frame bonus"),
    ("games", "Tennis game/set scoring with deuce, advantage and a tie-break at 6-6"),
    ("games", "Darts checkouts for a remaining score where the last dart must be a double"),
    ("games", "Card hand ranking for a simplified deck with an explicit ranking table and tie-breakers"),
    ("games", "Elo rating updates for a sequence of results with a K-factor depending on games played"),
    ("games", "Golf Stableford points from strokes, par and handicap strokes allocated by hole index"),
    ("games", "Crossword grid validation: every across/down run of length >= 2 must be a dictionary word"),
    ("games", "Board word scoring with letter/word multiplier squares given as a board map"),
    ("games", "Sudoku-variant constraint check with an extra diagonal rule, reporting the first violated cell"),
    ("games", "League table ranking by points, goal difference, goals scored, then head-to-head"),
    # numeric
    ("numeric", "Unit conversion through a graph of factors (ft->in->cm), exact with fractions"),
    ("numeric", "Fixed-point money arithmetic in integer cents with banker's rounding on division"),
    ("numeric", "Area of the union of axis-aligned rectangles"),
    ("numeric", "Point-in-polygon (even-odd rule) where points exactly on an edge count as inside"),
    ("numeric", "Streaming mean and variance with Welford's update"),
    ("numeric", "Percentile by linear interpolation between closest ranks, following a named convention"),
    ("numeric", "Histogram binning with fixed width, edge inclusion rules and an overflow bin"),
    ("numeric", "Exact fraction simplification and mixed-number formatting ('-1 2/3')"),
    ("numeric", "Base conversion between bases 2..36 with sign and truncated fractional digits"),
    ("numeric", "Physical quantity strings like '12.5 kPa' parsed and converted to a canonical unit"),
    # networking
    ("networking", "IPv4 CIDR containment and merging overlapping/adjacent blocks into a minimal list"),
    ("networking", "IPv6 address compression and expansion (longest zero run, leftmost on ties)"),
    ("networking", "HTTP Cache-Control parsing and freshness lifetime from max-age / s-maxage"),
    ("networking", "Cookie header parsing with quoted values, filtered by path prefix"),
    ("networking", "MAC address normalization from several notations to a canonical colon form"),
    ("networking", "Bit-packed flags: decode/encode a field layout given as (name, bit offset, width)"),
    ("networking", "PackBits-style run-length encoding of byte sequences with literal runs"),
    ("networking", "16-bit one's-complement checksum with end-around carry"),
    # data cleaning
    ("data-cleaning", "Deduplicate contact records by normalized email and phone, merging non-empty fields"),
    ("data-cleaning", "Phone number normalization to E.164 for a default country code and trunk prefix"),
    ("data-cleaning", "Group-by over multiple keys with sum/min/max/count, sorted output"),
    ("data-cleaning", "Sessionize per-user events by an inactivity gap, returning session start/end/count"),
    ("data-cleaning", "Forward-fill missing time-series values, limited to N consecutive steps"),
    ("data-cleaning", "Top-k per group with ties broken by a secondary key and original order"),
    ("data-cleaning", "Pivot (row, column, value) triples into a matrix with a default value"),
    ("data-cleaning", "Reconcile two ledgers by amount and date tolerance, listing unmatched entries"),
    ("data-cleaning", "Address line normalization with an abbreviation table and casing rules"),
    ("data-cleaning", "Hex color codes (#RGB, #RRGGBB, #RRGGBBAA) validated and canonicalized to lowercase 8-digit form"),
    # text processing
    ("text", "Full justification to a width, extra spaces distributed left-first, ragged last line"),
    ("text", "Word frequency with a stop-word list, case folding, and alphabetical tie-breaks"),
    ("text", "Abbreviation expansion from a dictionary, preserving the case of the first letter"),
    ("text", "Word-level diff into keep/insert/delete operations with minimal edits (LCS based)"),
]

if __name__ == "__main__":
    out = Path(__file__).with_name("seeds.jsonl")
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for i, (category, seed) in enumerate(SEEDS, 1):
            f.write(json.dumps({"id": f"s{i:03d}", "category": category, "seed": seed}) + "\n")
    print(f"{len(SEEDS)} seeds, {len({c for c, _ in SEEDS})} categories -> {out.name}")
