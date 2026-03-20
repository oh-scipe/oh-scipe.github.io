# OH-SCIPE

## Build
Run `make install` once to install both Node and Python dependencies.

Run `npm run build` or `make build` to:
1. Prepare a clean `dist/` directory.
2. Optimize images (`src/images` -> `dist/assets/images`).
3. Generate HTML pages into `dist/` (`build.py`).
4. Copy deployable static files such as `robots.txt` and `sitemap.xml` into `dist/`.

Run `npm run preview` or `make serve` to preview the built site locally from `dist/`.

Run `npm run verify` to check the generated site in `dist/` for the expected SEO tags.

Run `make clean` to remove `dist/`.

## Directory Structure

### Core
- **`build.py`**: Main Python script. Reads templates/data and generates the site into `dist/`.
- **`Makefile`**: Thin wrapper around the npm build commands.
- **`.github/workflows/deploy.yml`**: GitHub Pages deployment workflow. Builds `dist/` and publishes it.

### Data & Content
- **`data/people.json`**: Source of truth for the "People" page.
- **`data/initiatives.json`**: Source of truth for the "Initiatives" page and sidebar.
- **`data/site_metadata.yaml`**: Source of truth for site-wide HTML metadata, social metadata, and page SEO copy.
- **`templates/`**: HTML fragments (e.g., `person_block.html`, `initiative_page.html`).
- **`content/`**: HTML content for static pages (e.g., `about.html`).
- **`content/initiatives/`**: HTML content for individual initiative pages.

### Assets
- **`src/images/`**: **Source** for images. Add new images here.
- **`assets/`**: Source for static CSS/JS assets copied into `dist/assets/` during the build.
- **`scripts/copyOptimizeImages.js`**: Node.js script using `sharp` to optimize and copy images from `src` into the build output.
- **`scripts/prepareDist.js`**: Cleans `dist/` and copies non-image static assets plus top-level deploy files.
- **`assets/js/site.js`**: Minimal client-side behavior for the site shell.

### Generated Output (Do not edit directly)
- **`dist/`**: Deployable site artifact for GitHub Pages.
- **`dist/*.htm`**: Generated main pages (e.g., `index.htm`, `Initiatives.htm`).
- **`dist/initiatives/`**: Generated individual initiative pages.

## Workflow
1. **Update Content**: 
   - Edit `data/people.json` for people.
   - Edit `data/initiatives.json` and files in `content/initiatives/` for initiatives.
   - Edit `data/site_metadata.yaml` for site-wide metadata and page SEO text.
   - Edit files in `content/` for other static pages.
2. **Update Design**: Edit `templates/*.html` or `assets/css/`.
3. **Add Images**: Place in `src/images/`.
4. **Build**: Run `npm run build`.
5. **Preview/Verify**: Run `npm run preview` and `npm run verify`.
6. **Deploy**: Push to `main`. GitHub Actions builds and deploys `dist/` to GitHub Pages.

## GitHub Pages Setup
In the repository settings, switch **Pages** to **GitHub Actions** as the build and deployment source. The workflow at `.github/workflows/deploy.yml` will publish the contents of `dist/`.

## Notes
Legacy generated HTML and image output from the old deployment model are not part of source control anymore. The automated deployment path uses `dist/` instead of committing generated output.
