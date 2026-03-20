import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
NAV_CLASSES = [
    "class_home",
    "class_about",
    "class_projects",
    "class_people",
    "class_initiatives",
]


def read_text(path):
    return path.read_text(encoding="utf-8")


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path):
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def load_yaml(path):
    with path.open("r", encoding="utf-8") as file_obj:
        return yaml.safe_load(file_obj)


def render_placeholders(template, context):
    def replace(match):
        key = match.group(1)
        return str(context.get(key, match.group(0)))

    return PLACEHOLDER_PATTERN.sub(replace, template)


def build_sidebar_initiatives_html(initiatives_data):
    items = []

    for index, initiative in enumerate(initiatives_data):
        style = 'style="font-weight: bold; color: #ff7700;"' if index == 0 else ""
        items.append(
            f"""
            <li>
                <a class="wp-block-latest-posts__post-title" href="{{{{ relative_root }}}}/initiatives/{initiative['slug']}.html" {style}>
                    {initiative['title']}
                </a>
            </li>
            """
        )

    return "".join(items)


def canonical_url(base_url, output_path):
    if output_path == "index.htm":
        return f"{base_url}/"
    return f"{base_url}/{output_path}"


def build_page_metadata(site_metadata, page_key, output_path):
    page_data = dict(site_metadata["pages"][page_key])
    page_data["url"] = canonical_url(site_metadata["site"]["base_url"], output_path)
    return page_data


def build_initiative_metadata(site_metadata, initiative):
    initiative_config = site_metadata["initiative_page"]
    description = initiative.get("description")

    if description:
        page_description = initiative_config["description_template"].format(
            title=initiative["title"],
            description=description,
        )
    else:
        page_description = initiative_config["fallback_description"].format(
            title=initiative["title"],
        )

    return {
        "title": initiative_config["title_template"].format(title=initiative["title"]),
        "description": page_description,
        "keywords": initiative_config["keywords_template"].format(title=initiative["title"]),
        "url": f"{site_metadata['site']['base_url']}/initiatives/{initiative['slug']}.html",
    }


def build_layout_context(site_metadata, page_metadata, relative_root, active_class):
    site = site_metadata["site"]
    open_graph = site["open_graph"]
    twitter = site["twitter"]

    context = {
        "page_title": page_metadata["title"],
        "page_description": page_metadata["description"],
        "page_keywords": page_metadata["keywords"],
        "canonical_url": page_metadata["url"],
        "meta_author": site["author"],
        "meta_robots": site["robots"],
        "og_type": open_graph["type"],
        "og_image": open_graph["image"],
        "og_image_width": open_graph["image_width"],
        "og_image_height": open_graph["image_height"],
        "og_site_name": site["name"],
        "og_locale": site["locale"],
        "twitter_card": twitter["card"],
        "twitter_image": twitter["image"],
        "twitter_image_alt": twitter["image_alt"],
        "structured_data": json.dumps(
            site["structured_data"],
            ensure_ascii=False,
            indent=6,
        ),
        "site_name": site["name"],
        "site_tagline": site["tagline"],
        "home_link_title": site["home_link_title"],
        "footer_tagline": site["footer_tagline"],
        "relative_root": relative_root,
    }

    for nav_class in NAV_CLASSES:
        context[nav_class] = "current-menu-item" if nav_class == active_class else ""

    return context


def render_layout(
    layout,
    content,
    sidebar_initiatives_html,
    site_metadata,
    page_metadata,
    relative_root,
    active_class,
):
    page_html = layout.replace("<!-- CONTENT -->", content)
    page_html = page_html.replace(
        "<!-- SIDEBAR_INITIATIVES -->",
        sidebar_initiatives_html,
    )
    return render_placeholders(
        page_html,
        build_layout_context(site_metadata, page_metadata, relative_root, active_class),
    )


def build_people_page():
    people_data = load_json(ROOT / "data" / "people.json")
    person_template = read_text(ROOT / "templates" / "person_block.html")
    people_page_template = read_text(ROOT / "templates" / "people_page.html")

    people_html = ""

    for person in people_data:
        person_block = person_template

        for key, value in person.items():
            person_block = person_block.replace(f"{{{key}}}", str(value))

        if person.get("website"):
            website_html = f"""
                        <li class="wp-social-link wp-social-link-url wp-block-social-link">
                          <a href="{person['website']}" class="wp-block-social-link-anchor">
                            <svg width="24" height="24" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path>
                            </svg>
                            <span class="wp-block-social-link-label screen-reader-text">Website</span>
                          </a>
                        </li>"""
            person_block = person_block.replace("{website_block}", website_html)
        else:
            person_block = person_block.replace("{website_block}", "")

        people_html += person_block

    return people_page_template.replace("<!-- PEOPLE_LIST -->", people_html)


def build_initiatives_page(initiatives_data):
    initiative_item_template = read_text(ROOT / "templates" / "initiative_list_item.html")
    initiatives_list_template = read_text(ROOT / "templates" / "initiatives_list.html")

    initiatives_html = ""

    for initiative in initiatives_data:
        item_block = initiative_item_template
        for key, value in initiative.items():
            if key != "content_file":
                item_block = item_block.replace(f"{{{key}}}", str(value))
        initiatives_html += item_block

    return initiatives_list_template.replace("<!-- INITIATIVES_LIST -->", initiatives_html)


def generate_initiative_pages(
    initiatives_data,
    layout,
    output_dir,
    sidebar_initiatives_html,
    site_metadata,
):
    page_template = read_text(ROOT / "templates" / "initiative_page.html")
    initiatives_dir = output_dir / "initiatives"

    for initiative in initiatives_data:
        slug = initiative["slug"]
        output_path = initiatives_dir / f"{slug}.html"
        content_path = ROOT / initiative.get("content_file", "")

        if initiative.get("content_file") and content_path.exists():
            initiative_content = read_text(content_path)
        else:
            initiative_content = initiative.get("content", "")

        page_content = page_template.replace("{title}", initiative["title"])
        page_content = page_content.replace("{content}", initiative_content)

        page_html = render_layout(
            layout,
            page_content,
            sidebar_initiatives_html,
            site_metadata,
            build_initiative_metadata(site_metadata, initiative),
            "..",
            "class_initiatives",
        )

        write_text(output_path, page_html)
        print(f"Generated {output_path}")


def build_site(output_dir):
    site_metadata = load_yaml(ROOT / "data" / "site_metadata.yaml")
    layout = read_text(ROOT / "templates" / "layout.html")
    content_dir = ROOT / "content"

    pages = {
        "index.html": {"output": "index.htm", "class": "class_home"},
        "about.html": {"output": "about.htm", "class": "class_about"},
        "projects.htm": {"output": "projects.htm", "class": "class_projects"},
        "people.html": {"output": "people.htm", "class": "class_people"},
        "initiatives.html": {"output": "Initiatives.htm", "class": "class_initiatives"},
    }

    initiatives_path = ROOT / "data" / "initiatives.json"
    initiatives_data = load_json(initiatives_path) if initiatives_path.exists() else []
    sidebar_initiatives_html = build_sidebar_initiatives_html(initiatives_data)

    for content_file, config in pages.items():
        active_class = config["class"]
        output_path = output_dir / config["output"]
        page_metadata = build_page_metadata(site_metadata, content_file, config["output"])

        if content_file == "people.html" and (ROOT / "data" / "people.json").exists():
            print("Generating people page from data/people.json...")
            content = build_people_page()
        elif content_file == "initiatives.html":
            content = build_initiatives_page(initiatives_data)
            generate_initiative_pages(
                initiatives_data,
                layout,
                output_dir,
                sidebar_initiatives_html,
                site_metadata,
            )
        else:
            content_path = content_dir / content_file
            if not content_path.exists():
                print(f"Warning: Content file {content_path} not found. Skipping.")
                continue
            content = read_text(content_path)

        page_html = render_layout(
            layout,
            content,
            sidebar_initiatives_html,
            site_metadata,
            page_metadata,
            ".",
            active_class,
        )

        write_text(output_path, page_html)
        print(f"Generated {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the static site.")
    parser.add_argument(
        "--output",
        default="dist",
        help="Directory where the built site will be written.",
    )
    args = parser.parse_args()
    build_site((ROOT / args.output).resolve())
