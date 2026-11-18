def parse_csv_line(line: str, delimiter: str = ",") -> list[str]:
    if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter in '"\r\n':
        raise ValueError("delimiter must be one character other than a quote or newline")
    fields: list[str] = []
    i, n = 0, len(line)
    while True:
        if i < n and line[i] == '"':
            i += 1
            buf = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = line[i]
                if c == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        buf.append('"')
                        i += 2
                        continue
                    i += 1
                    break
                buf.append(c)
                i += 1
            fields.append("".join(buf))
            if i == n:
                return fields
            if line[i] != delimiter:
                raise ValueError("unexpected character after a closing quote")
            i += 1
        else:
            j = line.find(delimiter, i)
            end = n if j == -1 else j
            field = line[i:end]
            if '"' in field:
                raise ValueError("double quote inside an unquoted field")
            fields.append(field)
            if j == -1:
                return fields
            i = j + 1
