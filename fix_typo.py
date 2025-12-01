#!/usr/bin/env python3
"""
Simple script to fix monogr title typo in MEI files
"""

import glob
from lxml import etree


def fix_typo_in_file(file_path):
    """Fix the typo in a single MEI file"""
    try:
        # Parse XML
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Find monogr/title element
        namespaces = {"mei": "http://www.music-encoding.org/ns/mei"}
        monogr_titles = root.xpath(
            "//mei:monogr/mei:title", namespaces=namespaces
        )

        if not monogr_titles:
            return False, "No monogr/title found"

        title = monogr_titles[0]
        if title.text and "kustliche vnerweisung" in title.text:
            # Fix typo
            title.text = title.text.replace(
                "kustliche vnerweisung", "kunstliche vnderweisung"
            )

            # Save
            tree.write(
                file_path,
                encoding="UTF-8",
                xml_declaration=True,
                pretty_print=True,
            )
            return True, "Fixed typo"

        return False, "No typo found"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    # Process all MEI files, excluding the "converted" folder
    mei_files = glob.glob("**/*.mei", recursive=True)
    mei_files = [f for f in mei_files if not f.startswith("converted/")]

    print(f"Processing {len(mei_files)} MEI files (excluding converted folder)")

    fixed = 0
    for file_path in mei_files:
        success, message = fix_typo_in_file(file_path)
        if success:
            fixed += 1
        elif (
            "No typo found" not in message
            and "No monogr/title found" not in message
        ):
            print(f"✗ {file_path}: {message}")

    print(f"\nFixed {fixed} files total")


if __name__ == "__main__":
    main()
