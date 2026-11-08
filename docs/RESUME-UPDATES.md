# Updating the resume

The resume page at `/resume/` is generated from **`src/data/resume.json`**. The downloadable PDF is **`public/resume.pdf`**. Both are deployed automatically when changes are pushed to `main`.

## For the Claude in the Job Hunt project

1. Edit `src/data/resume.json`. Fields:
   - `headline`: one line, shown as the page title
   - `summary`: two or three sentences
   - `highlights`: three or four short wins
   - `experience[]`: `role`, `org`, `location`, `start`, `end`, `bullets[]`
   - `skills[]`: `group` and `items[]`
   - `certifications[]`, `education[]`: plain strings
   - `draft`: set to `false` once the content is final (removes the "being updated" notice)
2. Regenerate the PDF with the existing `build.js` → LibreOffice pipeline and save it as `public/resume.pdf`. If there's no PDF, the download button is hidden.
3. Commit and push. The site redeploys in a minute or two.

**Keep the two in sync:** the best long-term setup is to have `build.js` read `src/data/resume.json`, so the PDF and the web page come from the same content.

The public version should not include a phone number or street address. City and state plus the site email are enough.

Jason's notes on presentation (don't present the Aveta Six Sigma certificate as a belt; call the tiered daily management system LDM/SQDCE, not MDI) apply here too.
