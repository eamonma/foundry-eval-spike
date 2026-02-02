#!/usr/bin/env python3
"""
Strip Foundry Classic content from Microsoft Foundry documentation files.

This script removes:
- 'foundry-classic' from monikerRange in YAML frontmatter
- All content within ::: moniker range="foundry-classic" blocks
- Optionally unwraps ::: moniker range="foundry" blocks (keeps content, removes markers)
"""

import re
import argparse
from pathlib import Path


def strip_foundry_classic(content: str, unwrap_foundry: bool = True) -> str:
    """
    Remove Foundry Classic content from a markdown document.

    Args:
        content: The markdown content to process
        unwrap_foundry: If True, remove the moniker markers around 'foundry' content
                       while keeping the content itself

    Returns:
        The processed markdown content
    """
    lines = content.split('\n')
    result_lines = []

    # State tracking
    in_frontmatter = False
    frontmatter_count = 0
    in_classic_block = False
    in_foundry_block = False
    classic_block_depth = 0
    foundry_block_depth = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle YAML frontmatter
        if line.strip() == '---':
            frontmatter_count += 1
            if frontmatter_count == 1:
                in_frontmatter = True
                result_lines.append(line)
                i += 1
                continue
            elif frontmatter_count == 2:
                in_frontmatter = False
                result_lines.append(line)
                i += 1
                continue

        # Process frontmatter lines
        if in_frontmatter:
            # Handle monikerRange - remove foundry-classic
            if line.strip().startswith('monikerRange:'):
                # Parse the moniker range value
                match = re.match(r"^(\s*monikerRange:\s*)(['\"]?)(.+?)(['\"]?)\s*$", line)
                if match:
                    prefix, quote_start, value, quote_end = match.groups()
                    # Remove foundry-classic from the range
                    monikers = [m.strip() for m in value.split('||')]
                    monikers = [m for m in monikers if m != 'foundry-classic']

                    if monikers:
                        new_value = ' || '.join(monikers)
                        line = f"{prefix}{quote_start}{new_value}{quote_end}"
                    else:
                        # If no monikers left, skip the line entirely
                        i += 1
                        continue
            result_lines.append(line)
            i += 1
            continue

        # Check for moniker block start
        classic_match = re.match(r'^::: moniker range=["\']foundry-classic["\']', line.strip())
        foundry_match = re.match(r'^::: moniker range=["\']foundry["\']', line.strip())
        moniker_end = line.strip() == '::: moniker-end'

        if classic_match:
            in_classic_block = True
            classic_block_depth = 1
            i += 1
            continue

        if foundry_match:
            in_foundry_block = True
            foundry_block_depth = 1
            if not unwrap_foundry:
                result_lines.append(line)
            i += 1
            continue

        if in_classic_block:
            if moniker_end:
                classic_block_depth -= 1
                if classic_block_depth == 0:
                    in_classic_block = False
            # Skip all content in classic block
            i += 1
            continue

        if in_foundry_block:
            if moniker_end:
                foundry_block_depth -= 1
                if foundry_block_depth == 0:
                    in_foundry_block = False
                    if not unwrap_foundry:
                        result_lines.append(line)
                    i += 1
                    continue
            # Keep content in foundry block
            result_lines.append(line)
            i += 1
            continue

        # Regular content outside any moniker block
        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)


def process_file(input_path: Path, output_path: Path | None = None, unwrap_foundry: bool = True) -> str:
    """
    Process a single markdown file.

    Args:
        input_path: Path to the input file
        output_path: Path to write output (if None, returns content only)
        unwrap_foundry: Whether to unwrap foundry moniker blocks

    Returns:
        The processed content
    """
    content = input_path.read_text(encoding='utf-8')
    processed = strip_foundry_classic(content, unwrap_foundry)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(processed, encoding='utf-8')

    return processed


def main():
    parser = argparse.ArgumentParser(
        description='Strip Foundry Classic content from Microsoft Foundry documentation'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Input markdown file or directory'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file or directory (default: print to stdout for files, required for directories)'
    )
    parser.add_argument(
        '--keep-foundry-markers',
        action='store_true',
        help='Keep the ::: moniker range="foundry" markers (default: remove them)'
    )
    parser.add_argument(
        '--in-place',
        action='store_true',
        help='Modify files in place (use with caution)'
    )

    args = parser.parse_args()

    unwrap_foundry = not args.keep_foundry_markers

    if args.input.is_file():
        if args.in_place:
            output_path = args.input
        else:
            output_path = args.output

        result = process_file(args.input, output_path, unwrap_foundry)

        if not output_path:
            print(result)

    elif args.input.is_dir():
        if not args.output and not args.in_place:
            parser.error('--output is required when processing a directory (or use --in-place)')

        for md_file in args.input.rglob('*.md'):
            if args.in_place:
                output_path = md_file
            else:
                relative = md_file.relative_to(args.input)
                output_path = args.output / relative

            print(f'Processing: {md_file}')
            process_file(md_file, output_path, unwrap_foundry)

    else:
        parser.error(f'Input path does not exist: {args.input}')


if __name__ == '__main__':
    main()
