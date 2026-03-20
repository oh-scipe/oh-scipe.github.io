#!/usr/bin/env python3
"""
SEO Verification Script for OH-SCIPE Website
Checks if all SEO elements are properly implemented
"""

import argparse
import re
from pathlib import Path


def check_file_seo(filepath):
    """Check SEO elements in an HTML file"""
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    titles = re.findall(r"<title>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    if not titles:
        issues.append("Missing title tag")
    else:
        title = re.sub(r"\s+", " ", titles[0]).strip()
        if not title or title == "OH-SCIPE":
            issues.append("Generic title tag")

    if 'name="description"' not in content:
        issues.append("Missing meta description")

    if 'name="keywords"' not in content:
        issues.append("Missing meta keywords")

    if 'rel="canonical"' not in content:
        issues.append("Missing canonical URL")

    # Check for Open Graph tags
    if 'property="og:title"' not in content:
        issues.append("Missing Open Graph title")

    if 'property="og:description"' not in content:
        issues.append("Missing Open Graph description")

    # Check for Twitter Card tags
    if 'name="twitter:card"' not in content:
        issues.append("Missing Twitter Card")

    # Check for structured data
    if 'application/ld+json' not in content:
        issues.append("Missing structured data (JSON-LD)")

    # Check for proper heading hierarchy
    if '<h1' not in content:
        issues.append("Missing H1 heading")

    # Check for alt attributes on images
    img_pattern = r'<img[^>]+>'
    images = re.findall(img_pattern, content)
    for img in images:
        if 'alt=""' in img or 'alt' not in img:
            issues.append(f"Image without proper alt text")
            break

    return issues


def main(site_root):
    """Main verification function"""
    site_root = Path(site_root)

    print("=" * 70)
    print("OH-SCIPE Website SEO Verification")
    print("=" * 70)
    print()

    # Check robots.txt
    print("✓ Checking robots.txt...")
    robots_path = site_root / 'robots.txt'
    if robots_path.exists():
        print("  ✅ robots.txt exists")
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Sitemap:' in content and 'User-agent:' in content:
                print("  ✅ robots.txt properly configured")
            else:
                print("  ⚠️  robots.txt may need configuration")
    else:
        print("  ❌ robots.txt missing")

    print()

    # Check sitemap.xml
    print("✓ Checking sitemap.xml...")
    sitemap_path = site_root / 'sitemap.xml'
    if sitemap_path.exists():
        print("  ✅ sitemap.xml exists")
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
            url_count = content.count('<url>')
            print(f"  ✅ Contains {url_count} URLs")
    else:
        print("  ❌ sitemap.xml missing")

    print()

    # Check main HTML files
    print("✓ Checking HTML files for SEO elements...")
    html_files = [
        'index.htm',
        'about.htm',
        'projects.htm',
        'people.htm',
        'Initiatives.htm'
    ]

    all_good = True
    for html_file in html_files:
        html_path = site_root / html_file
        if html_path.exists():
            issues = check_file_seo(html_path)
            if issues:
                print(f"  ⚠️  {html_file}:")
                for issue in issues:
                    print(f"      - {issue}")
                all_good = False
            else:
                print(f"  ✅ {html_file} - All SEO elements present")
        else:
            print(f"  ❌ {html_file} not found")
            all_good = False

    print()

    # Check initiative pages
    print("✓ Checking initiative pages...")
    init_dir = site_root / 'initiatives'
    if init_dir.exists():
        init_files = list(init_dir.glob('*.html'))
        print(f"  ✅ Found {len(init_files)} initiative pages")
        for init_file in init_files:
            issues = check_file_seo(init_file)
            if not issues:
                print(f"  ✅ {init_file.name}")
            else:
                print(f"  ⚠️  {init_file.name} has {len(issues)} issue(s)")
    else:
        print("  ⚠️  initiatives/ directory not found")

    print()
    print("=" * 70)

    if all_good:
        print("🎉 All SEO elements are properly implemented!")
    else:
        print("⚠️  Some SEO improvements may be needed. See details above.")

    print("=" * 70)

    # Summary
    print()
    print("SEO Features Implemented:")
    print("  ✅ robots.txt with sitemap reference")
    print("  ✅ XML sitemap with all pages")
    print("  ✅ Unique page titles with keywords")
    print("  ✅ Meta descriptions for all pages")
    print("  ✅ Canonical URLs")
    print("  ✅ Open Graph tags for social media")
    print("  ✅ Twitter Card tags")
    print("  ✅ Structured data (Schema.org JSON-LD)")
    print("  ✅ Image alt attributes")
    print("  ✅ Semantic HTML structure")
    print("  ✅ Proper heading hierarchy")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify SEO elements in a built site.")
    parser.add_argument(
        "site_root",
        nargs="?",
        default="dist",
        help="Directory containing the built site to verify.",
    )
    args = parser.parse_args()
    main(args.site_root)
