#!/usr/bin/env python3
"""
ImagePro - Command-line tool for responsive image processing
"""

import argparse
import sys
from pathlib import Path
from PIL import Image
import os


__version__ = "1.0.0"


def parse_sizes(size_str):
    """Parse comma-separated list of sizes into integers."""
    try:
        sizes = [int(s.strip()) for s in size_str.split(',')]
        if any(s <= 0 for s in sizes):
            raise ValueError("Sizes must be positive integers")
        return sizes
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid size format: {e}")


def validate_jpeg(filepath):
    """Validate that the file is a JPEG."""
    valid_extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG']
    if filepath.suffix not in valid_extensions:
        return False
    return True


def get_file_size_kb(filepath):
    """Get file size in KB."""
    return os.path.getsize(filepath) / 1024


def resize_image(input_path, output_dir, sizes, dimension='width', quality=90):
    """
    Resize an image to multiple sizes.

    Args:
        input_path: Path to input image
        output_dir: Directory for output images
        sizes: List of target sizes
        dimension: 'width' or 'height'
        quality: JPEG quality (1-100)

    Returns:
        List of created files with metadata
    """
    # Open and validate image
    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"Error: Cannot read image: {input_path}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(4)

    # Get original dimensions
    orig_width, orig_height = img.size

    # Prepare output
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get base name and extension
    base_name = input_path.stem
    extension = input_path.suffix

    created_files = []
    skipped_sizes = []

    # Process each size
    for size in sizes:
        # Calculate new dimensions
        if dimension == 'width':
            if size > orig_width:
                skipped_sizes.append((size, f"original is only {orig_width}px wide"))
                continue
            new_width = size
            new_height = int((size / orig_width) * orig_height)
        else:  # height
            if size > orig_height:
                skipped_sizes.append((size, f"original is only {orig_height}px tall"))
                continue
            new_height = size
            new_width = int((size / orig_height) * orig_width)

        # Resize image using high-quality Lanczos resampling
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Prepare output filename
        output_filename = f"{base_name}_{size}{extension}"
        output_path = output_dir / output_filename

        # Strip EXIF by converting to RGB if needed and not saving exif
        if resized_img.mode in ('RGBA', 'LA', 'P'):
            # Handle transparency by converting to RGB with white background
            background = Image.new('RGB', resized_img.size, (255, 255, 255))
            if resized_img.mode == 'P':
                resized_img = resized_img.convert('RGBA')
            background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode in ('RGBA', 'LA') else None)
            resized_img = background
        elif resized_img.mode != 'RGB':
            resized_img = resized_img.convert('RGB')

        # Save without EXIF data
        resized_img.save(output_path, 'JPEG', quality=quality, optimize=True)

        # Get file size
        file_size = get_file_size_kb(output_path)

        created_files.append({
            'path': output_path,
            'filename': output_filename,
            'width': new_width,
            'height': new_height,
            'size_kb': file_size
        })

    return created_files, skipped_sizes


def cmd_resize(args):
    """Handle the resize subcommand."""
    input_path = Path(args.input)

    # Validate input file exists
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(3)

    # Validate it's a JPEG
    if not validate_jpeg(input_path):
        print(f"Error: Unsupported format. Version 1.0 supports JPEG only.", file=sys.stderr)
        print(f"Supported extensions: .jpg, .jpeg, .JPG, .JPEG", file=sys.stderr)
        sys.exit(1)

    # Determine dimension and sizes
    if args.width and args.height:
        print("Error: Cannot specify both --width and --height", file=sys.stderr)
        sys.exit(2)
    elif args.width:
        dimension = 'width'
        sizes = parse_sizes(args.width)
    elif args.height:
        dimension = 'height'
        sizes = parse_sizes(args.height)
    else:
        print("Error: Must specify either --width or --height", file=sys.stderr)
        sys.exit(2)

    # Validate quality
    if not (1 <= args.quality <= 100):
        print("Error: Quality must be between 1-100", file=sys.stderr)
        sys.exit(2)

    # Get image dimensions for output
    try:
        with Image.open(input_path) as img:
            orig_width, orig_height = img.size
    except Exception as e:
        print(f"Error: Cannot read image: {input_path}", file=sys.stderr)
        sys.exit(4)

    # Print processing info
    print(f"Processing: {input_path.name} ({orig_width}x{orig_height})")
    print(f"Output directory: {args.output}")
    print()

    # Process the image
    created_files, skipped_sizes = resize_image(
        input_path,
        args.output,
        sizes,
        dimension=dimension,
        quality=args.quality
    )

    # Print results
    for file_info in created_files:
        print(f"✓ Created: {file_info['filename']} "
              f"({file_info['width']}x{file_info['height']}, "
              f"{file_info['size_kb']:.0f} KB)")

    # Print warnings for skipped sizes
    if skipped_sizes:
        print()
        for size, reason in skipped_sizes:
            print(f"⚠ Skipped {size}px: {reason}")

    # Print summary
    print()
    if created_files:
        print(f"Successfully created {len(created_files)} image(s) from {input_path.name}")
    else:
        print(f"Warning: No images created (all sizes would require upscaling)")
        sys.exit(0)


def main():
    """Main entry point for imagepro CLI."""
    parser = argparse.ArgumentParser(
        description='ImagePro - Command-line tool for responsive image processing',
        epilog='Use "imagepro.py <command> --help" for more information about a command.'
    )

    parser.add_argument('--version', '-v', action='version', version=f'ImagePro {__version__}')

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Resize command
    resize_parser = subparsers.add_parser(
        'resize',
        help='Resize images to multiple dimensions',
        description='Resize an image to multiple widths or heights while maintaining aspect ratio'
    )

    resize_parser.add_argument(
        '--width',
        type=str,
        help='Comma-separated list of target widths (e.g., 300,600,900)'
    )

    resize_parser.add_argument(
        '--height',
        type=str,
        help='Comma-separated list of target heights (e.g., 400,800)'
    )

    resize_parser.add_argument(
        '--input',
        required=True,
        help='Path to input image file'
    )

    resize_parser.add_argument(
        '--output',
        default='./resized/',
        help='Output directory (default: ./resized/)'
    )

    resize_parser.add_argument(
        '--quality',
        type=int,
        default=90,
        help='JPEG quality 1-100 (default: 90)'
    )

    resize_parser.set_defaults(func=cmd_resize)

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute the command
    args.func(args)


if __name__ == '__main__':
    main()
