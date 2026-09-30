from runtime import EnvScope, FdTriple


def _count_bytes(data: bytes) -> tuple[int, int, int]:
    return data.count(b"\n"), len(data.split()), len(data)


def wc(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    in_fd = fds.get_in()
    out_fd = fds.get_out()
    err_fd = fds.get_err()

    names: list[str] = args[1:]

    if len(names) == 0:
        data: bytes = in_fd.read().encode("utf-8", "surrogateescape")

        lines, words, size = _count_bytes(data)
        out_fd.write(f"{lines} {words} {size}\n")
        return 0

    status = 0
    total = [0, 0, 0]

    for name in names:
        try:
            with open(name, "rb") as file:
                counts = _count_bytes(file.read())
        except OSError as e:
            err_fd.write(f"wc: {name}: {e.strerror}\n")
            status = 1
            continue

        lines, words, size = counts
        out_fd.write(f"{lines} {words} {size} {name}\n")
        total = [t + c for t, c in zip(total, counts)]

    if len(names) > 1:
        lines, words, size = total
        out_fd.write(f"{lines} {words} {size} total\n")

    return status
