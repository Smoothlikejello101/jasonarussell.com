// Builds public/resume.pdf from src/data/resume.json (the same file the /resume page uses).
// Usage: npm run resume:pdf      (needs LibreOffice installed: soffice)
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  Document, Packer, Paragraph, TextRun, AlignmentType, TabStopType, LevelFormat, BorderStyle,
} from "docx";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const resume = JSON.parse(fs.readFileSync(path.join(root, "src/data/resume.json"), "utf8"));
const site = JSON.parse(fs.readFileSync(path.join(root, "src/data/site.json"), "utf8"));

const FONT = "Calibri";
const BODY = 21;          // 10.5 pt
const MARGIN = 1008;      // 0.7 in
const PAGE_W = 12240;
const TEXT_W = PAGE_W - 2 * MARGIN;

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: BODY, ...o });
const dates = (j) => [j.start, j.end].filter(Boolean).join(" – ");

const sectionHeader = (text) => new Paragraph({
  spacing: { before: 180, after: 70 },
  keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "808080", space: 1 } },
  children: [run(text, { bold: true, size: 23 })],
});
const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 30 },
  children: [run(text)],
});

const out = [];
const P = (...x) => out.push(...x);

// Header: city/state and site email only. No phone, no street address.
P(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 },
    children: [run(site.name.toUpperCase(), { bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [run(`${site.location}  |  ${site.email}  |  jasonarussell.com`)] }),
);

P(
  sectionHeader("SUMMARY"),
  new Paragraph({ spacing: { after: 40 }, children: [run(resume.summary)] }),
);

if (resume.highlights?.length) {
  P(sectionHeader("HIGHLIGHTS"), ...resume.highlights.map(bullet));
}

P(sectionHeader("PROFESSIONAL EXPERIENCE"));
resume.experience.forEach((job, i) => {
  P(
    new Paragraph({
      spacing: { before: i === 0 ? 60 : 140, after: 0 },
      keepNext: true,
      tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W }],
      children: [run(job.role, { bold: true }), run("\t" + dates(job))],
    }),
    new Paragraph({
      spacing: { after: 40 },
      keepNext: true,
      children: [run(job.org, { italics: true }), ...(job.location ? [run("  |  " + job.location)] : [])],
    }),
    ...job.bullets.map(bullet),
  );
});

if (resume.earlier?.length) {
  P(sectionHeader("EARLIER EXPERIENCE"), ...resume.earlier.map(bullet));
}
if (resume.education?.length) {
  P(sectionHeader("EDUCATION"), ...resume.education.map(bullet));
}
if (resume.certifications?.length) {
  P(sectionHeader("TRAINING & CREDENTIALS"), ...resume.certifications.map(bullet));
}
if (resume.skills?.length) {
  P(sectionHeader("SKILLS"), ...resume.skills.map((s) => new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 30 },
    children: [run(s.group + ": ", { bold: true }), run(s.items.join(", "))],
  })));
}

const doc = new Document({
  creator: site.name,
  title: `${site.name} – Resume`,
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ],
    }],
  },
  sections: [{
    properties: { page: {
      size: { width: PAGE_W, height: 15840 },
      margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
    } },
    children: out,
  }],
});

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "resume-"));
const docx = path.join(tmp, "resume.docx");
fs.writeFileSync(docx, await Packer.toBuffer(doc));
execFileSync("soffice", ["--headless", "--convert-to", "pdf", "--outdir", tmp, docx], { stdio: "ignore" });
fs.copyFileSync(path.join(tmp, "resume.pdf"), path.join(root, "public/resume.pdf"));
console.log("wrote public/resume.pdf");
