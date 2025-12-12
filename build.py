
import os
import json

def build_site():
    # Configuration
    layout_file = 'templates/layout.html'
    content_dir = 'content'
    output_dir = '.'
    
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
    
    # Process each page
    for content_file, config in pages.items():
        output_path = os.path.join(output_dir, config['output'])
        active_class = config['class']
        
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
            
        else:
            content_path = os.path.join(content_dir, content_file)
            if not os.path.exists(content_path):
                print(f"Warning: Content file {content_path} not found. Skipping.")
                continue
                
            with open(content_path, 'r') as f:
                content = f.read()
        
        # Replace placeholders
        page_html = layout.replace('<!-- CONTENT -->', content)
        
        # Reset all classes
        for cls in ['class_home', 'class_about', 'class_projects', 'class_people', 'class_initiatives']:
            page_html = page_html.replace(f'{{{{ {cls} }}}}', 'current-menu-item' if cls == active_class else '')
            
        # Write output
        with open(output_path, 'w') as f:
            f.write(page_html)
        
        print(f"Generated {output_path}")

if __name__ == "__main__":
    build_site()
