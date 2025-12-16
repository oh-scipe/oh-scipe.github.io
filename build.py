import os
import json

def generate_initiative_pages(initiatives_data, layout, output_dir, sidebar_initiatives_html):
    initiatives_dir = os.path.join(output_dir, 'initiatives')
    if not os.path.exists(initiatives_dir):
        os.makedirs(initiatives_dir)
        
    with open('templates/initiative_page.html', 'r') as f:
        page_template = f.read()
    
    base_url = 'https://oh-scipe.github.io'
        
    for initiative in initiatives_data:
        slug = initiative['slug']
        output_path = os.path.join(initiatives_dir, f'{slug}.html')
        relative_root = '..'
        
        # Read content file
        content_file = initiative.get('content_file')
        if content_file and os.path.exists(content_file):
            with open(content_file, 'r') as f:
                initiative_content = f.read()
        else:
            initiative_content = initiative.get('content', '')
            
        # Prepare page content
        page_content = page_template.replace('{title}', initiative['title'])
        page_content = page_content.replace('{content}', initiative_content)
        
        # Apply layout
        page_html = layout.replace('<!-- CONTENT -->', page_content)
        page_html = page_html.replace('<!-- SIDEBAR_INITIATIVES -->', sidebar_initiatives_html)
        page_html = page_html.replace('{{ relative_root }}', relative_root)
        
        # SEO metadata for initiative pages
        page_title = f"{initiative['title']} - OH-SCIPE Initiative"
        page_description = initiative.get('description', f"Learn about {initiative['title']}, an OH-SCIPE initiative in AI and machine learning research.")
        page_keywords = f"AI research, machine learning, {initiative['title']}, research opportunities, NSF initiative, computational science"
        canonical_url = f"{base_url}/initiatives/{slug}.html"
        
        page_html = page_html.replace('{{ page_title }}', page_title)
        page_html = page_html.replace('{{ page_description }}', page_description)
        page_html = page_html.replace('{{ page_keywords }}', page_keywords)
        page_html = page_html.replace('{{ canonical_url }}', canonical_url)
        
        # Set active class (initiatives)
        for cls in ['class_home', 'class_about', 'class_projects', 'class_people', 'class_initiatives']:
            page_html = page_html.replace(f'{{{{ {cls} }}}}', 'current-menu-item' if cls == 'class_initiatives' else '')
            
        with open(output_path, 'w') as f:
            f.write(page_html)
        print(f"Generated {output_path}")

def build_site():
    # Configuration
    layout_file = 'templates/layout.html'
    content_dir = 'content'
    output_dir = '.'
    base_url = 'https://oh-scipe.github.io'
    
    # SEO metadata for each page
    page_metadata = {
        'index.html': {
            'title': 'OH-SCIPE - Revolutionizing Research with AI and ML Integration',
            'description': 'NSF-funded initiative empowering science and engineering through advanced artificial intelligence and machine learning. Collaborative research across Case Western Reserve University, Ohio Supercomputer Center, and University of Cincinnati.',
            'keywords': 'AI research, machine learning, NSF funded, computational infrastructure, HPC, artificial intelligence, science engineering, Ohio research, AI integration, ML engineering',
            'url': base_url + '/'
        },
        'about.html': {
            'title': 'About OH-SCIPE - Team & Mission | AI Research Initiative',
            'description': 'Meet the interdisciplinary OH-SCIPE team of AI/ML experts from leading Ohio institutions. Learn about our mission to integrate machine learning engineering into science and engineering research.',
            'keywords': 'AI research team, machine learning experts, NSF research, computational scientists, HPC experts, research collaboration, Ohio universities',
            'url': base_url + '/about.htm'
        },
        'projects.htm': {
            'title': 'OH-SCIPE Projects - AI & ML Research Applications',
            'description': 'Explore OH-SCIPE research projects integrating artificial intelligence and machine learning into science and engineering. Discover cutting-edge computational research applications.',
            'keywords': 'AI projects, ML research, computational science projects, research applications, HPC applications, AI engineering',
            'url': base_url + '/projects.htm'
        },
        'people.html': {
            'title': 'OH-SCIPE Team - Researchers & Principal Investigators',
            'description': 'Meet the principal investigators, machine learning engineers, and AI scientists driving OH-SCIPE research. Expert team from Case Western, OSC, and University of Cincinnati.',
            'keywords': 'AI researchers, ML engineers, principal investigators, computational scientists, research team, AI experts, Ohio researchers',
            'url': base_url + '/people.htm'
        },
        'initiatives.html': {
            'title': 'OH-SCIPE Initiatives - Internships & Research Opportunities',
            'description': 'Discover OH-SCIPE research initiatives including summer internships, AI research opportunities for undergraduates, and collaborative programs in machine learning and computational science.',
            'keywords': 'research internships, AI opportunities, undergraduate research, summer programs, ML internships, research experience, NSF opportunities',
            'url': base_url + '/Initiatives.htm'
        }
    }
    
    # Map content files to output files and active menu classes
    pages = {
        'index.html': {'output': 'index.htm', 'class': 'class_home'},
        'about.html': {'output': 'about.htm', 'class': 'class_about'},
        'projects.htm': {'output': 'projects.htm', 'class': 'class_projects'},
        'people.html': {'output': 'people.htm', 'class': 'class_people'},
        'initiatives.html': {'output': 'Initiatives.htm', 'class': 'class_initiatives'},
    }
    
    # Read layout
    with open(layout_file, 'r') as f:
        layout = f.read()

    # Load initiatives data for sidebar
    sidebar_initiatives_html = ""
    initiatives_data = []
    if os.path.exists('data/initiatives.json'):
        with open('data/initiatives.json', 'r') as f:
            initiatives_data = json.load(f)
        
        for i, initiative in enumerate(initiatives_data):
            # Highlight the first item
            style = 'style="font-weight: bold; color: #ff7700;"' if i == 0 else ''
            
            sidebar_initiatives_html += f'''
            <li>
                <a class="wp-block-latest-posts__post-title" href="{{{{ relative_root }}}}/initiatives/{initiative['slug']}.html" {style}>
                    {initiative['title']}
                </a>
            </li>
            '''
    
    # Process each page
    for content_file, config in pages.items():
        output_path = os.path.join(output_dir, config['output'])
        active_class = config['class']
        relative_root = '.'
        
        content = ""
        
        # Special handling for people page if data exists
        if content_file == 'people.html' and os.path.exists('data/people.json'):
            print("Generating people page from data/people.json...")
            with open('data/people.json', 'r') as f:
                people_data = json.load(f)
            
            with open('templates/person_block.html', 'r') as f:
                person_template = f.read()
                
            with open('templates/people_page.html', 'r') as f:
                people_page_template = f.read()
            
            people_html = ""
            for person in people_data:
                # Simple string replacement
                person_block = person_template
                for key, value in person.items():
                    person_block = person_block.replace(f'{{{key}}}', str(value))
                
                # Handle website block
                if 'website' in person and person['website']:
                    website_html = f'''
                        <li class="wp-social-link wp-social-link-url wp-block-social-link">
                          <a href="{person['website']}" class="wp-block-social-link-anchor">
                            <svg width="24" height="24" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path>
                            </svg>
                            <span class="wp-block-social-link-label screen-reader-text">Website</span>
                          </a>
                        </li>'''
                    person_block = person_block.replace('{website_block}', website_html)
                else:
                    person_block = person_block.replace('{website_block}', '')
                
                people_html += person_block
            
            content = people_page_template.replace('<!-- PEOPLE_LIST -->', people_html)

        # Special handling for initiatives page
        elif content_file == 'initiatives.html':
            # We already loaded initiatives_data above
            
            with open('templates/initiative_list_item.html', 'r') as f:
                initiative_item_template = f.read()
                
            with open('templates/initiatives_list.html', 'r') as f:
                initiatives_list_template = f.read()
            
            initiatives_html = ""
            for initiative in initiatives_data:
                item_block = initiative_item_template
                for key, value in initiative.items():
                    if key != 'content_file':
                        item_block = item_block.replace(f'{{{key}}}', str(value))
                initiatives_html += item_block
            
            content = initiatives_list_template.replace('<!-- INITIATIVES_LIST -->', initiatives_html)
            
            # Also generate individual initiative pages
            generate_initiative_pages(initiatives_data, layout, output_dir, sidebar_initiatives_html)

        else:
            content_path = os.path.join(content_dir, content_file)
            if not os.path.exists(content_path):
                print(f"Warning: Content file {content_path} not found. Skipping.")
                continue
                
            with open(content_path, 'r') as f:
                content = f.read()
        
        # Replace placeholders
        page_html = layout.replace('<!-- CONTENT -->', content)
        page_html = page_html.replace('<!-- SIDEBAR_INITIATIVES -->', sidebar_initiatives_html)
        page_html = page_html.replace('{{ relative_root }}', relative_root)
        
        # Replace SEO metadata
        metadata = page_metadata.get(content_file, page_metadata['index.html'])
        page_html = page_html.replace('{{ page_title }}', metadata['title'])
        page_html = page_html.replace('{{ page_description }}', metadata['description'])
        page_html = page_html.replace('{{ page_keywords }}', metadata['keywords'])
        page_html = page_html.replace('{{ canonical_url }}', metadata['url'])
        
        # Reset all classes
        for cls in ['class_home', 'class_about', 'class_projects', 'class_people', 'class_initiatives']:
            page_html = page_html.replace(f'{{{{ {cls} }}}}', 'current-menu-item' if cls == active_class else '')
            
        # Write output
        with open(output_path, 'w') as f:
            f.write(page_html)
        
        print(f"Generated {output_path}")

if __name__ == "__main__":
    build_site()
