# Product Requirements Document: Responsive Image Resizer

**Version:** 1.0  
**Date:** November 12, 2024  
**Status:** Draft  

---

## 1. Executive Summary

A command-line tool for generating multiple resolutions of images to support responsive web design workflows, specifically for static site generators like 11ty. The tool enables developers to create `srcset`-ready images from source files with configurable dimensions and quality settings.

### Primary Use Case
Generate thumbnail and full-resolution variants of images for lightbox galleries and responsive image displays, creating multiple width-based resolutions from a single source image.

---

## 2. Goals & Objectives

### Goals
- Simplify the creation of responsive image sets for web development
- Provide a scriptable, automation-friendly CLI tool
- Support modern web image optimization workflows
- Enable batch processing through standard Unix pipelines

### Non-Goals (Future Versions)
- Real-time image processing
- GUI or web interface (covered in separate PRD section)
- Advanced image manipulation (filters, effects, compositing)
- Cloud storage integration

---

## 3. User Personas

### Primary: Web Developer
- Works with static site generators (11ty, Hugo, Jekyll)
- Needs to generate responsive image sets regularly
- Comfortable with command-line tools
- Values automation and scriptability

### Secondary: Content Manager
- Prepares images for web publishing
- May use the tool through wrapper scripts
- Needs consistent, predictable output

---

## 4. Functional Requirements

### 4.1 Core Functionality

#### 4.1.1 Image Resizing
- **Requirement:** Resize images to specified dimensions while maintaining aspect ratio
- **Acceptance Criteria:**
  - Support `--width` parameter with comma-separated list of target widths
  - Support `--height` parameter with comma-separated list of target heights
  - Width and height modes are mutually exclusive (cannot specify both in same invocation)
  - Aspect ratio is always preserved
  - Output dimensions are exact for the specified axis (width or height)

#### 4.1.2 Skip Upscaling
- **Requirement:** Do not upscale images beyond their original dimensions
- **Acceptance Criteria:**
  - If target size exceeds original dimension, skip that size
  - Log skipped sizes with reason (e.g., "Skipped 1200px: original is only 800px wide")
  - Continue processing remaining sizes in the list

#### 4.1.3 Input Handling (Version 1.0)
- **Requirement:** Process single image file per invocation
- **Acceptance Criteria:**
  - Accept `--input <filepath>` parameter
  - Validate file exists and is readable
  - Support absolute and relative paths
  - Error if file is not a supported format

**Future Versions:**
- Multiple files: `--input file1.jpg file2.jpg`
- Glob patterns: `--input *.jpg`
- Directory processing: `--input ./photos/`

#### 4.1.4 Output Organization
- **Requirement:** Save resized images to organized output location
- **Acceptance Criteria:**
  - Default output directory: `./resized/` (relative to current working directory)
  - Support `--output <path>` to specify custom output directory
  - Create output directory if it doesn't exist
  - Preserve original file extension
  - Naming pattern: `{basename}_{size}.{ext}`
    - Example: `photo.jpg` at 300px → `photo_300.jpg`
    - Example: `vacation.jpeg` at 600px → `vacation_600.jpeg`

#### 4.1.5 Quality Control
- **Requirement:** Control JPEG compression quality
- **Acceptance Criteria:**
  - Support `--quality <1-100>` parameter
  - Default quality: 90
  - Validate quality is integer between 1-100
  - Apply quality setting to all output images

#### 4.1.6 EXIF Metadata Handling
- **Requirement:** Strip EXIF metadata by default for web optimization
- **Acceptance Criteria:**
  - Remove all EXIF data from output images
  - Reduce file size by removing camera metadata
  - Maintain color profile information (ICC)

**Future Versions:**
- `--preserve-exif` flag to keep metadata
- `--strip-all` to remove ICC profiles too
- Selective EXIF preservation (orientation only, etc.)

---

### 4.2 Format Support

#### 4.2.1 Version 1.0 Format Support
- **Input:** JPEG/JPG only
- **Output:** JPEG/JPG only
- **Acceptance Criteria:**
  - Accept files with `.jpg`, `.jpeg`, `.JPG`, `.JPEG` extensions
  - Output files maintain input extension case
  - Reject non-JPEG files with clear error message

#### 4.2.2 Future Format Support
- **Input:** All Pillow-supported formats (PNG, WebP, TIFF, BMP, GIF, etc.)
- **Output:** Configurable format conversion
  - `--format webp` to convert JPEG → WebP
  - `--format png` for lossless output
  - Auto-detect optimal format based on content

---

### 4.3 Command-Line Interface

#### 4.3.1 Basic Syntax
```bash
scale_image --width <sizes> --input <file> [options]
scale_image --height <sizes> --input <file> [options]
```

#### 4.3.2 Required Parameters
- `--width <sizes>` OR `--height <sizes>` (mutually exclusive)
  - Comma-separated list of integers
  - Example: `--width 300,600,900,1200`
- `--input <filepath>`
  - Path to source image file

#### 4.3.3 Optional Parameters
- `--quality <1-100>` (default: 90)
- `--output <directory>` (default: `./resized/`)
- `--help` / `-h` - Display usage information
- `--version` / `-v` - Display version number

#### 4.3.4 Usage Examples
```bash
# Basic usage - resize to multiple widths
scale_image --width 300,600,900,1200 --input photo.jpg

# Custom quality
scale_image --width 300,600 --input photo.jpg --quality 85

# Custom output directory
scale_image --width 300,600 --input photo.jpg --output ~/web/images/

# Resize by height instead of width
scale_image --height 400,800 --input banner.jpg

# Batch processing via shell loop
for img in *.jpg; do
  scale_image --width 300,600,900 --input "$img"
done

# Process with absolute paths
find /photos -name "*.jpg" | while read img; do
  scale_image --width 300,600 --input "$img" --output /web/resized/
done
```

---

### 4.4 Error Handling

#### 4.4.1 Input Validation Errors
- Missing required parameters → Exit with error message and usage hint
- Invalid file path → "Error: File not found: <path>"
- Unsupported format → "Error: Unsupported format. Version 1.0 supports JPEG only."
- Invalid quality value → "Error: Quality must be between 1-100"
- Both width and height specified → "Error: Cannot specify both --width and --height"

#### 4.4.2 Processing Errors
- Corrupt image file → "Error: Cannot read image: <file>"
- Permission denied → "Error: Cannot write to output directory: <path>"
- Disk space issues → "Error: Insufficient disk space"
- All sizes skipped (upscaling) → Warning, exit successfully with message

#### 4.4.3 Error Behavior
- Exit with non-zero status code on errors
- Print errors to stderr
- Print normal output to stdout
- Continue processing is NOT applicable (single file mode in v1.0)

---

### 4.5 Output & Feedback

#### 4.5.1 Standard Output
- Summary of operations performed
- List of created files with dimensions and file sizes
- Warnings for skipped sizes

#### 4.5.2 Example Output
```
Processing: photo.jpg (2400x1600)
Output directory: ./resized/

✓ Created: photo_300.jpg (300x200, 45 KB)
✓ Created: photo_600.jpg (600x400, 128 KB)
✓ Created: photo_900.jpg (900x600, 256 KB)
✓ Created: photo_1200.jpg (1200x800, 412 KB)

Successfully created 4 images from photo.jpg
```

#### 4.5.3 Verbose Mode (Future)
- `--verbose` flag for detailed processing information
- Show processing time per image
- Display compression ratios

#### 4.5.4 Quiet Mode (Future)
- `--quiet` flag to suppress all output except errors
- Useful for scripting and automation

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Process a single 4000x3000 JPEG in < 5 seconds on modern hardware
- Memory usage should scale with image size (load one image at a time)
- No memory leaks during batch processing

### 5.2 Compatibility
- **Operating Systems:** macOS, Linux, Windows
- **Python Version:** Python 3.8+
- **Dependencies:** Pillow (PIL) library only

### 5.3 Reliability
- Graceful handling of corrupt images
- Atomic file writes (temp file + rename) to prevent partial outputs
- No data loss on interruption (Ctrl+C)

### 5.4 Usability
- Clear, actionable error messages
- Help text accessible via `--help`
- Follows Unix conventions (exit codes, stdin/stdout/stderr)

### 5.5 Maintainability
- Well-documented code with docstrings
- Unit tests for core functions
- Integration tests for CLI interface
- Semantic versioning

---

## 6. Technical Constraints

### 6.1 Dependencies
- **Pillow:** For image processing (resize, quality, format handling)
- **argparse:** For CLI argument parsing (Python stdlib)
- **pathlib:** For path handling (Python stdlib)

### 6.2 File System
- Must handle spaces and special characters in filenames
- Support Unicode filenames
- Work with relative and absolute paths

### 6.3 Image Processing
- Use Pillow's high-quality resampling (Lanczos filter)
- Maintain color accuracy during resize
- Handle both RGB and RGBA images appropriately

---

## 7. Future Enhancements (Post-V1.0)

### 7.1 Batch Processing (v1.1)
- Multiple input files
- Glob pattern support
- Directory recursion
- Progress bar for batch operations

### 7.2 Advanced Resizing (v1.2)
- Crop modes (center, smart, focal point)
- Fit modes (contain, cover, fill)
- Simultaneous width AND height with aspect ratio options

### 7.3 Format Support (v1.3)
- PNG input/output
- WebP support (modern web format)
- AVIF support (next-gen format)
- Format conversion capabilities

### 7.4 Metadata & Optimization (v1.4)
- Preserve EXIF option
- Progressive JPEG encoding
- Optimize PNG with pngquant
- Edit EXIF fields (copyright, author)

### 7.5 Responsive Web Features (v1.5)
- Generate HTML `<img>` tags with srcset
- Generate `<picture>` elements with multiple formats
- Output JSON manifest for static site generators
- Validate srcset size ordering

### 7.6 Configuration (v1.6)
- Config file support (`.imagerc`, `pyproject.toml`)
- Named presets (`--preset thumbnail`)
- Per-project configuration
- Environment variable support

### 7.7 Advanced Features (v2.0)
- Watermarking
- Image filters (grayscale, blur, sharpen)
- Smart cropping with face detection
- Parallel processing for batch operations
- Dry-run mode (`--dry-run`)

---

## 8. Success Metrics

### 8.1 Adoption Metrics
- GitHub stars and forks
- PyPI download count
- Community contributions

### 8.2 Quality Metrics
- Test coverage > 80%
- Zero critical bugs in production
- Average issue resolution time < 7 days

### 8.3 Performance Metrics
- Processing time per megapixel
- Memory usage benchmarks
- User-reported performance issues

---

## 9. Open Questions

1. **File Overwrite Behavior:** What should happen if output file already exists?
   - Overwrite silently?
   - Skip with warning?
   - Prompt user (breaks automation)?
   - Add `--force` flag?

2. **Dry-Run Mode:** Should v1.0 include `--dry-run` to preview operations?

3. **Progress Feedback:** For single-file mode, is progress output needed?

4. **Exit Codes:** Define specific exit codes for different error types?
   - 0 = success
   - 1 = general error
   - 2 = invalid arguments
   - 3 = file not found
   - 4 = processing error

5. **Color Output:** Should terminal output use colors (like the bash script)?
   - Requires colorama or similar library
   - Auto-detect TTY vs pipe

6. **Logging:** Should the tool support logging to file for debugging?

7. **Size Validation:** Should we validate that sizes are in ascending order for srcset?

---

## 10. Web Interface (Separate Section - TBD)

**Note:** Web interface requirements will be documented separately after CLI specification is finalized.

### Planned Features:
- Drag-and-drop file upload
- Visual configuration of resize parameters
- Real-time preview of resized images
- Batch processing with progress bar
- Download individual or zip all outputs
- Localhost web server (Flask/FastAPI)

**Status:** Requirements gathering in progress

---

## 11. Appendix

### 11.1 Related Tools
- ImageMagick (CLI tool, external dependency)
- sharp (Node.js library)
- Pillow (Python library - our foundation)
- libvips (high-performance C library)

### 11.2 References
- [Responsive Images - MDN](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [11ty Image Plugin](https://www.11ty.dev/docs/plugins/image/)

### 11.3 Glossary
- **srcset:** HTML attribute for specifying multiple image sources at different resolutions
- **Aspect Ratio:** Proportional relationship between width and height
- **Upscaling:** Enlarging an image beyond its original dimensions
- **EXIF:** Metadata embedded in image files (camera settings, GPS, etc.)
- **Lanczos:** High-quality image resampling algorithm

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-11-12 | Initial | First draft based on requirements gathering |

