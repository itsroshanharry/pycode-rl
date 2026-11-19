[
    ("a package __init__ treated like a plain module", "        package = importer if is_package else importer.rpartition(\".\")[0]", "        package = importer.rpartition(\".\")[0]"),
    ("one dot climbs one level too many", "        bits = package.rsplit(\".\", level - 1)", "        bits = package.rsplit(\".\", level)"),
    ("the alias is returned instead of the imported name", "            items.append(im.group(1))", "            items.append(im.group(2) or im.group(1))"),
]
