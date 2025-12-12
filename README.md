# OH-SCIPE

## Build
Run `make build` to:
1. Install dependencies (`npm install`).
2. Optimize images (`src/images` -> `assets/images`).
3. Generate HTML pages (`build.py`).

Run `make clean` to remove generated files.

## Directory Structure

### Core
- **`build.py`**: Main Python script. Reads templates/data and generates `.htm` files.
- **`Makefile`**: Orchestrates the build pipeline.

### Data & Content
- **`data/people.json`**: Source of truth for the "People" page.
- **`data/initiatives.json`**: Source of truth for the "Initiatives" page and sidebar.
- **`templates/`**: HTML fragments (e.g., `person_block.html`, `initiative_page.html`).
- **`content/`**: HTML content for static pages (e.g., `about.html`).
- **`content/initiatives/`**: HTML content for individual initiative pages.

### Assets
- **`src/images/`**: **Source** for images. Add new images here.
- **`assets/`**: **Destination** for compiled assets (CSS, JS, optimized images). Do not edit images here directly.
- **`scripts/copyOptimizeImages.js`**: Node.js script using `sharp` to optimize and copy images from `src` to `assets`.

### Generated Output (Do not edit directly)
- **`*.htm`**: Generated main pages (e.g., `index.htm`, `Initiatives.htm`).
- **`initiatives/`**: Generated individual initiative pages.

## Workflow
1. **Update Content**: 
   - Edit `data/people.json` for people.
   - Edit `data/initiatives.json` and files in `content/initiatives/` for initiatives.
   - Edit files in `content/` for other static pages.
2. **Update Design**: Edit `templates/*.html` or `assets/css/`.
3. **Add Images**: Place in `src/images/`.
4. **Build**: Run `make build`.
5. **Deploy**: Commit and push generated files.
