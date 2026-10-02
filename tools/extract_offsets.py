#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys


def run(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.stdout
    except Exception:
        return ""


def parse_dynamic_symbols(path):
    output = run([
        "nm",
        "-D",
        "--defined-only",
        path,
    ])

    symbols = []

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split(None, 2)

        if len(parts) != 3:
            continue

        address, symbol_type, name = parts

        if not re.fullmatch(r"[0-9a-fA-F]+", address):
            continue

        offset = int(address, 16)

        symbols.append({
            "address": "0x" + address,
            "type": symbol_type,
            "name": name,
            "offset": offset,
            "hex_offset": hex(offset),
            "decimal_offset": offset,
        })

    return symbols


def parse_elf_header(path):
    output = run([
        "readelf",
        "-h",
        path,
    ])

    result = {}

    interesting_fields = {
        "Class",
        "Data",
        "Type",
        "Machine",
        "Entry point address",
        "Start of program headers",
        "Start of section headers",
        "Number of program headers",
        "Number of section headers",
    }

    for line in output.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        if key in interesting_fields:
            result[key] = value

    return result


def parse_build_id(path):
    output = run([
        "readelf",
        "-n",
        path,
    ])

    match = re.search(
        r"Build ID:\s*([0-9a-fA-F]+)",
        output,
    )

    if match:
        return match.group(1)

    return None


def get_file_size(path):
    return os.path.getsize(path)


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: extract_offsets.py "
            "<libminecraftpe.so> <output.json>"
        )
        sys.exit(1)

    library = os.path.abspath(sys.argv[1])
    output_file = os.path.abspath(sys.argv[2])

    if not os.path.isfile(library):
        print("Library does not exist:", library)
        sys.exit(1)

    elf = parse_elf_header(library)
    symbols = parse_dynamic_symbols(library)
    build_id = parse_build_id(library)

    result = {
        "library": os.path.basename(library),
        "size": get_file_size(library),
        "build_id": build_id,
        "elf": elf,
        "dynamic_symbol_count": len(symbols),
        "dynamic_symbols": symbols,
    }

    output_directory = os.path.dirname(output_file)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True,
        )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("========================================")
    print(" Minecraft Offset Extraction")
    print("========================================")
    print()
    print("Library:", library)
    print("Size:", get_file_size(library), "bytes")
    print("Build ID:", build_id or "not found")
    print("Dynamic symbols:", len(symbols))
    print()
    print("Output:", output_file)


if __name__ == "__main__":
    main()
