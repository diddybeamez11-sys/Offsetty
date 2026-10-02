#!/usr/bin/env python3

import re
import subprocess
import sys


INTERESTING = re.compile(
    r"(Actor|Player|Mob|LocalPlayer|"
    r"GameMode|Level|BlockSource|"
    r"MinecraftClient|MinecraftGame|"
    r"Move|Jump|Attack|Inventory|"
    r"Item|Block)",
    re.IGNORECASE,
)


def run(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    return result.stdout


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: make_offset_report.py "
            "<libminecraftpe.so> <output.txt>"
        )
        sys.exit(1)

    library = sys.argv[1]
    output = sys.argv[2]

    symbols = run([
        "nm",
        "-D",
        "--defined-only",
        library,
    ])

    strings = run([
        "strings",
        "-a",
        "-n",
        "4",
        library,
    ])

    with open(
        output,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "Minecraft Bedrock ARM64 Offset Report\n"
        )
        f.write("=" * 60)
        f.write("\n\n")

        f.write("LIBRARY\n")
        f.write("-" * 60)
        f.write(f"{library}\n\n")

        f.write(
            "INTERESTING EXPORTED SYMBOLS\n"
        )
        f.write("-" * 60)
        f.write("\n")

        count = 0

        for line in symbols.splitlines():
            if INTERESTING.search(line):
                f.write(line + "\n")
                count += 1

        f.write("\n")
        f.write(
            f"Matching exported symbols: {count}\n\n"
        )

        f.write("INTERESTING STRINGS\n")
        f.write("-" * 60)
        f.write("\n")

        string_count = 0

        for line in strings.splitlines():
            if INTERESTING.search(line):
                f.write(line + "\n")
                string_count += 1

        f.write("\n")
        f.write(
            f"Matching strings: {string_count}\n"
        )


if __name__ == "__main__":
    main()
