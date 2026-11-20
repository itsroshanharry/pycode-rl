[
    ("dots removed from the local part for every domain", "    if domain in _GMAIL:\n        local = local.replace(\".\", \"\")  # dots only matter outside Gmail\n        domain = \"gmail.com\"", "    local = local.replace(\".\", \"\")\n    if domain in _GMAIL:\n        domain = \"gmail.com\""),
    ("company taken from the earliest record instead of the latest", "            if v:\n                company = v", "            if v and company is None:\n                company = v"),
    ("11-digit numbers keep their leading country-code 1", "    if len(digits) == 11 and digits[0] == \"1\":\n        digits = digits[1:]  # North American country code\n", ""),
]
