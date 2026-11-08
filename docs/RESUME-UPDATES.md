# Updating the resume

One file drives everything: **`src/data/resume.json`**.

- The page at `/resume/` is built from it on every deploy.
- The downloadable PDF, **`public/resume.pdf`**, is built from it by `npm run resume:pdf` (`tools/resume/build.mjs`, which uses `docx` + LibreOffice). The PDF is committed, because Cloudflare's build doesn't have LibreOffice. **After any edit to `resume.json`, rerun `npm run resume:pdf` and commit the new PDF too.** If the PDF is missing, the download button is hidden.

## Fields

- `headline`: one line, shown as the page title
- `summary`: two or three sentences, first person
- `highlights`: three or four short wins
- `experience[]`: `role`, `org`, `location`, `start`, `end`, `bullets[]`
- `earlier[]`: one-line strings for older jobs (shown as a single "Earlier:" line)
- `skills[]`: `group` and `items[]`
- `certifications[]`, `education[]`: plain strings
- `draft`: `true` shows a "being updated" notice on the page

## What goes in the public version

This is the general-audience version. Tailored resumes for specific applications live in the Job Hunt project and are **not** copied here wholesale.

- No phone number or street address. City/state and `jason@jasonarussell.com` only (both come from `site.json`).
- No company dollar figures (e.g. scrap savings in $). Use percentages and counts.
- Leave out angles specific to one application (internal-candidate framing, role-specific emphasis).
- Call the tiered daily management system **LDM/SQDCE**, not MDI.
- Don't present the Aveta Six Sigma certificate as a belt.
- Don't claim coordinating R&D trials or writing the trials procedure; the contribution was getting R&D and plant ops communicating.

## Monthly check

A scheduled task reviews this file once a month against Jason's latest resume work and asks him whether anything new should be added. Changes go through a pull request for him to approve, never straight to `main`.
