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

        social_links = []

        if person.get("orcid"):
            social_links.append(
                f"""
                        <li class="wp-social-link wp-block-social-link">
                            <a href="https://orcid.org/{person['orcid']}" class="wp-block-social-link-anchor">
                              <svg width="24" height="24" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                                <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.306v7.419h2.438c1.938 0 2.969-1.031 2.969-2.969 0-2.094-1.156-4.45-3.081-4.45h-2.325z"></path>
                              </svg>
                              <span class="wp-block-social-link-label screen-reader-text">ORCID</span>
                            </a>
                        </li>"""
            )

        if person.get("email"):
            social_links.append(
                f"""
                        <li class="wp-social-link wp-social-link-mail wp-block-social-link">
                          <a href="mailto:{person['email']}" class="wp-block-social-link-anchor">
                            <svg
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              version="1.1"
                              xmlns="http://www.w3.org/2000/svg"
                              aria-hidden="true"
                              focusable="false"
                            >
                              <path
                                d="M19,5H5c-1.1,0-2,.9-2,2v10c0,1.1.9,2,2,2h14c1.1,0,2-.9,2-2V7c0-1.1-.9-2-2-2zm.5,12c0,.3-.2.5-.5.5H5c-.3,0-.5-.2-.5-.5V9.8l7.5,5.6,7.5-5.6V17zm0-9.1L12,13.6,4.5,7.9V7c0-.3.2-.5.5-.5h14c.3,0,.5.2.5.5v.9z"
                              ></path></svg>
                            <span class="wp-block-social-link-label screen-reader-text">Mail</span>
                          </a>
                        </li>"""
            )

        if person.get("linkedin"):
            social_links.append(
                f"""
                        <li class="wp-social-link wp-social-link-linkedin wp-block-social-link" style="background-color: #f0f0f0 !important; color: #444 !important;">
                          <a href="{person['linkedin']}" class="wp-block-social-link-anchor">
                            <svg
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              version="1.1"
                              xmlns="http://www.w3.org/2000/svg"
                              aria-hidden="true"
                              focusable="false"
                            >
                              <path
                                d="M19.7,3H4.3C3.582,3,3,3.582,3,4.3v15.4C3,20.418,3.582,21,4.3,21h15.4c0.718,0,1.3-0.582,1.3-1.3V4.3 C21,3.582,20.418,3,19.7,3z M8.339,18.338H5.667v-8.59h2.672V18.338z M7.004,8.574c-0.857,0-1.549-0.694-1.549-1.548 c0-0.855,0.691-1.548,1.549-1.548c0.854,0,1.547,0.694,1.547,1.548C8.551,7.881,7.858,8.574,7.004,8.574z M18.339,18.338h-2.669 v-4.177c0-0.996-0.017-2.278-1.387-2.278c-1.389,0-1.601,1.086-1.601,2.206v4.249h-2.667v-8.59h2.559v1.174h0.037 c0.356-0.675,1.227-1.387,2.526-1.387c2.703,0,3.203,1.779,3.203,4.092V18.338z"
                              ></path></svg>
                            <span class="wp-block-social-link-label screen-reader-text">LinkedIn</span>
                          </a>
                        </li>"""
            )

        if person.get("website"):
            social_links.append(
                f"""
                        <li class="wp-social-link wp-social-link-url wp-block-social-link">
                          <a href="{person['website']}" class="wp-block-social-link-anchor">
                            <svg width="24" height="24" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path>
                            </svg>
                            <span class="wp-block-social-link-label screen-reader-text">Website</span>
                          </a>
                        </li>"""
            )

        social_links_html = ""
        if social_links:
            social_links_html = f"""
                      <ul class="wp-block-social-links is-layout-flex wp-block-social-links-is-layout-flex" style="display: flex; flex-direction: row; gap: 10px; list-style: none; padding: 0; margin: 0 0 1em 0;">
{''.join(social_links)}
                      </ul>"""

        title = person.get("title", "")
        title_line = f"<p><strong>{person.get('name', '')}</strong> – {title}</p>" if title else f"<p><strong>{person.get('name', '')}</strong></p>"
        bio = person.get("bio", "")
        expertise = person.get("expertise", "")

        replacements = {
            "name": person.get("name", ""),
            "image": person.get("image", ""),
            "title_line": title_line,
            "social_links_block": social_links_html,
            "bio_block": f"<p>{bio}</p>" if bio else "",
            "expertise_block": f"<p><strong>Expertise:</strong> {expertise}</p>" if expertise else "",
        }

        for key, value in replacements.items():
            person_block = person_block.replace(f"{{{key}}}", str(value))

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
