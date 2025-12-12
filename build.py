
import os

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
        content_path = os.path.join(content_dir, content_file)
        output_path = os.path.join(output_dir, config['output'])
        active_class = config['class']
        
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
