"""Author the fixed scenario documents. Run deliberately when revising the accepted baseline."""
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / 'src/scenario.json').read_text(encoding='utf-8'))
OUT = ROOT / 'public/documents'
OUT.mkdir(parents=True, exist_ok=True)
NAVY = '203D4A'
TEAL = '246E60'
SOURCE_NOTES = [
    'CSCF The Blueprint - end-to-end reference architecture, repository baseline 11 October 2026.',
    'Solution Assurance Engine Thinking Flow - supplied cognitive and control model; six domains, 30 capabilities, 30 anti-patterns and 180 primary questions.',
    'CSCF The Description - Continuous Solution Creation Flow master concept paper, October 2026.',
    'Secure Software Development Process V1.0A - supplied secure-development control reference, 29 September 2026.'
]
ARCHITECTURE = [
    ('Acquisition and intake', 'Local source parsers create a source ingestion manifest. A user reviews purpose, actors, data, autonomy and lifecycle before an immutable intake snapshot is bound to the manifest.'),
    ('Governed control layer', 'Versioned knowledge collections define criteria. Deterministic services enforce object references, evidence ceilings, finding lock, applicability, hard gates and action eligibility.'),
    ('Bounded reasoning adapters', 'The future SAE may use approved AI routes for interpretation, independent challenge and controlled synthesis. Only approved summaries and confirmed intake may cross that boundary. Provider selection and independence are governed configuration.'),
    ('Decision and presentation', 'One ReadinessPackageV2 drives the Assessment Workspace, Assurance Summary and exports. Publication integrity, readiness recommendation and formal human approval remain separate decisions.')
]
DELIVERY = [
    ('Implementation contract', 'Deliver acquisition adapters, confirmed intake, validated knowledge loading, the A-F instrument, independent claim verification, finding lock, deterministic readiness, exact tactic mapping, controlled publication and canonical views. Protect human authority and information boundaries.'),
    ('Verification contract', 'Execute SAE-VER-01 through SAE-VER-10 independently against the assessed revision. Include malformed sources, missing proof, fabricated citations, score-versus-blocker conflicts, unmapped tactics, unsupported prose and unauthorized approval attempts.'),
    ('Release conditions', 'All ten requirements must have attributable verification evidence on the assessed revision. Mandatory security failures, missing critical evidence and unresolved authority decisions remain blocking. Named humans authorize release after reviewing the package and target environment.'),
    ('Operational acceptance', 'Pre-release tests do not establish operating effectiveness. After a real deployment, collect version-linked evidence, incidents and reassessment triggers. Validate learning before changing the accepted system model.')
]
DECISIONS = [
    'Confirm the product owner, security/privacy reviewers and release approver for a real implementation. These roles are requirements, not recorded appointments or signatures.',
    'Choose the real deployment boundary, authentication model, retention periods and evidence-store controls according to actual data classification.',
    'Approve provider routes, independence rules, budgets and data-processing arrangements before any future AI integration.',
    'Validate the governed knowledge snapshot, current source editions, applicability and tactic catalogue before real activation.',
    'Set operational service levels, recovery targets and evidence retention with the accountable service owner.'
]

doc = Document()
for border in doc.styles.element.xpath('.//w:pBdr'):
    border.getparent().remove(border)
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.27), Inches(11.69)
section.top_margin, section.bottom_margin = Inches(.72), Inches(.65)
section.left_margin = section.right_margin = Inches(.76)
section.header_distance = section.footer_distance = Inches(.3)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Heading 3']:
    style = doc.styles[name]
    style.font.name = 'Calibri'
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_after = Pt(7)
doc.styles['Normal'].font.size = Pt(10.5)
doc.styles['Normal'].paragraph_format.line_spacing = 1.12
doc.styles['Title'].font.size = Pt(27)
doc.styles['Title'].paragraph_format.space_after = Pt(12)
doc.styles['Heading 1'].font.size = Pt(17)
doc.styles['Heading 1'].paragraph_format.space_before = Pt(13)
doc.styles['Heading 2'].font.size = Pt(12.5)
doc.styles['Heading 2'].paragraph_format.space_before = Pt(10)
doc.core_properties.title = 'Solution Assurance Engine CSCF New Build Brief'
doc.core_properties.subject = 'CSCF-SAE-NB-001 version 1.0'
doc.core_properties.author = 'CSCF'
doc.core_properties.keywords = 'CSCF, Solution Assurance Engine, New Build, requirements'
footer = section.footer.paragraphs[0]
footer.text = f'{S["id"]}  |  v{S["version"]}  |  New Build Brief     '
footer.runs[0].font.size = Pt(8)
field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); footer._p.append(field)

def para(text, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = bold
    return p

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for column, width in zip(t.columns, widths): column.width = Inches(width)
    for index, head in enumerate(headers): t.rows[0].cells[index].text = head
    for row in rows:
        cells = t.add_row().cells
        for i, text in enumerate(row): cells[i].text = str(text)
    for row_index, row in enumerate(t.rows):
        for i, cell in enumerate(row.cells):
            if widths: cell.width = Inches(widths[i])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr = cell._tc.get_or_add_tcPr()
            shade = OxmlElement('w:shd'); shade.set(qn('w:fill'), NAVY if row_index == 0 else ('F2F5F6' if row_index % 2 else 'FFFFFF')); tcpr.append(shade)
            margins = OxmlElement('w:tcMar')
            for tag in ['top', 'left', 'bottom', 'right']:
                item = OxmlElement(f'w:{tag}'); item.set(qn('w:w'), '110'); item.set(qn('w:type'), 'dxa'); margins.append(item)
            tcpr.append(margins)
            borders = OxmlElement('w:tcBorders')
            for edge in ['top', 'left', 'bottom', 'right']:
                b = OxmlElement(f'w:{edge}'); b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '4'); b.set(qn('w:color'), 'D9D9D9'); borders.append(b)
            tcpr.append(borders)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                for r in p.runs:
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor.from_string('FFFFFF' if row_index == 0 else '000000')
                    r.bold = row_index == 0
        no_split = OxmlElement('w:cantSplit'); row._tr.get_or_add_trPr().append(no_split)
    repeat = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t

doc.add_paragraph('Solution Assurance Engine', 'Title')
doc.add_paragraph('CSCF New Build Brief', 'Subtitle')
para('This brief defines the proposed purpose, boundaries, deliverables and acceptance basis for building Solution Assurance Engine through the Continuous Solution Creation Flow. The implementation and verification contracts must remain traceable to this baseline. Release requires evidence and a named human decision.')
table(['Control field', 'Baseline'], [('Document identity', S['id']), ('Version and date', f'{S["version"]} | {S["date"]}'), ('Entry mode', 'New Build'), ('Status', 'Proposed build specification; formal approval not recorded'), ('Solution', S['solution'])], [1.55, 5.15])
doc.add_heading('Purpose and desired outcomes', 1)
para(S['purpose'])
para('The expected outcome is a reproducible, decision-ready package that explains what the submitted evidence supports, where proof is missing and which human decisions remain necessary. Success is measured through the ten acceptance criteria in this brief; operational value must later be demonstrated using real usage and outcome evidence.')
doc.add_heading('Users and accountable roles', 1)
para('Solution owners confirm intended use and review findings. Architects and engineers provide implementation evidence. Security, privacy and governance reviewers resolve scoped questions. Release approvers authorize lifecycle transitions. Auditors reconstruct decisions from the evidence ledger. Individual appointments remain a real-project decision.')
doc.add_heading('Scope and exclusions', 1)
para('Scope includes safe source intake, confirmed case understanding, the A-F instrument, independent verification, deterministic readiness, grounded tactics, controlled publication and canonical outputs. Autonomous legal conclusions, residual-risk acceptance, production approval and automatic finding closure are excluded.')

doc.add_page_break()
doc.add_heading('Proposed architecture and boundaries', 1)
for title, text in ARCHITECTURE:
    doc.add_heading(title, 2); para(text)
doc.add_heading('Governance domains', 1)
table(['Domain', 'Assessment coverage'], [(d['id'], d['name'].replace('&', 'and')) for d in S['domains']], [.7, 6])
doc.add_heading('Dependencies and operating assumptions', 1)
para('The real Engine depends on approved source parsers, versioned knowledge collections, identity and access controls, an evidence store, a configured reasoning-adapter registry and operational monitoring. Missing evidence remains UNKNOWN. Raw source bytes and image pixels stay outside provider packets; credentials must never enter audit exports.')
para('The CSCF demonstration uses prepared deliverables and results without executing the future Engine or invoking AI. Its acceptance by document fingerprint is a demo entry rule, not a proposed real-world intake policy.')

groups = [S['requirements'][:3], S['requirements'][3:6], S['requirements'][6:]]
for group in groups:
    doc.add_page_break()
    doc.add_heading('Requirements and acceptance criteria', 1)
    para('Each requirement carries an independent verification scenario. The future implementation must produce revision-linked evidence rather than rely on its own completion claim.')
    for req in group:
        doc.add_heading(f'{req["id"]} {req["title"]}', 2)
        para(req['requirement'])
        p = doc.add_paragraph(); p.add_run('Acceptance criterion  ').bold = True; p.add_run(req['acceptance'])
        p = doc.add_paragraph(); p.add_run(f'{req["testId"]}  ').bold = True; p.add_run(req['test'])
        p = doc.add_paragraph(); p.add_run('Required deliverable  ').bold = True; p.add_run(req['deliverable'])

doc.add_page_break()
doc.add_heading('Contracts and delivery conditions', 1)
for title, text in DELIVERY:
    doc.add_heading(title, 2); para(text)
doc.add_heading('Decisions to resolve for the real build', 1)
for decision in DECISIONS: doc.add_paragraph(decision, 'List Bullet')
doc.add_heading('Reference basis', 1)
for note in SOURCE_NOTES: doc.add_paragraph(note, 'List Bullet')
para('The architecture references define intended behavior. They do not establish that a real implementation passes these criteria or satisfies legal or secure-development obligations.')
input_path = OUT / S['inputFile']
doc.save(input_path)
input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()

# The approval report is a fixed asset. It never incorporates runtime timestamps or claims live execution.
font_dir = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Body', str(font_dir / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('BodyBold', str(font_dir / 'arialbd.ttf')))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCopy', fontName='Body', fontSize=9.5, leading=14, spaceAfter=8, textColor=colors.HexColor('#314b56')))
styles.add(ParagraphStyle(name='SmallCopy', fontName='Body', fontSize=7.7, leading=11, spaceAfter=5, textColor=colors.HexColor('#46616b')))
styles.add(ParagraphStyle(name='CellCopy', fontName='Body', fontSize=7.2, leading=10, textColor=colors.HexColor('#314b56')))
styles.add(ParagraphStyle(name='CellHead', fontName='BodyBold', fontSize=7.5, leading=10, textColor=colors.white))
styles.add(ParagraphStyle(name='ReportTitle', fontName='BodyBold', fontSize=26, leading=32, spaceAfter=13, textColor=colors.HexColor('#173b48')))
styles.add(ParagraphStyle(name='ReportHeading', fontName='BodyBold', fontSize=17, leading=22, spaceAfter=12, textColor=colors.HexColor('#173b48')))
styles.add(ParagraphStyle(name='ReportSub', fontName='BodyBold', fontSize=11, leading=15, spaceBefore=8, spaceAfter=7, textColor=colors.HexColor('#246e60')))
story = []
def pp(text, style='BodyCopy'): return Paragraph(escape(str(text)), styles[style])
def add(text, style='BodyCopy'): story.append(pp(text, style))
def pdf_table(headers, rows, widths):
    data = [[pp(x, 'CellHead') for x in headers]] + [[pp(x, 'CellCopy') for x in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#203d4a')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f6f4')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9e3e1')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9)]))
    story.extend([t, Spacer(1, 14)])
W = A4[0] - 88
add('Solution Assurance Engine', 'ReportTitle')
add('Document of Approval', 'ReportHeading')
add('Approval pending', 'ReportSub')
add('The prepared CSCF scenario has reached the release gate. Its ten acceptance requirements are linked to candidate deliverables and simulated verification records. This package supports review; formal approval, residual-risk acceptance and deployment have not occurred.')
pdf_table(['Package field','Fixed scenario record'], [('Input baseline', f'{S["id"]} | version {S["version"]}'),('Scenario date', S['date']),('Document of Approval', 'CSCF-SAE-DOA-001 | version 1.0'),('Verification result','10 of 10 prepared scenarios marked PASS - SIMULATED'),('Release status','Ready for demo approval review; formal authorization pending'),('Operational evidence','Not collected; operating effectiveness remains unobserved')], [135,W-135])
add('Declared purpose', 'ReportSub'); add(S['purpose'])
add('Input document identity', 'ReportSub'); add(S['inputFile'], 'SmallCopy'); add(f'SHA-256: {input_hash}', 'SmallCopy')
add('Evidence boundary', 'ReportSub'); add('This report is the same prepared document in every demonstration. No code generation, scanners, model calls or real assurance assessment were executed to obtain these records. Scenario results must not be used as evidence about the existing SAE implementation.')
story.append(PageBreak())
add('Implementation and verification contracts', 'ReportHeading')
for title, text in DELIVERY[:3]: add(title,'ReportSub'); add(text)
add('Prepared security and integrity checks','ReportSub')
pdf_table(['Check family','Scenario verification','Result'], [('Build and dependencies','Candidate structure and dependency policy fixture','PASS - SIMULATED'),('Secrets and raw source boundary','No secrets or raw files in prepared packet fixture','PASS - SIMULATED'),('Access and authorization','Unauthorized access and automated approval denial','PASS - SIMULATED'),('Traceability and evidence integrity','Requirement, citation and package-reference checks','PASS - SIMULATED')], [120,W-225,105])
add('Verification independence','ReportSub'); add('The scenario presents separately defined implementation and verification contracts. All acceptance tests include a boundary or negative case. The report records this intended control pattern without claiming that an independent real review occurred.')
story.append(PageBreak())
add('Requirement traceability','ReportHeading')
add('The original requirement identity is preserved throughout candidate work, verification and the release conclusion. Full acceptance criteria follow this matrix.')
rows=[]
for r in S['requirements']:
    rows.append([r['id']+'\n'+r['title'],r['deliverable'],r['testId']+'\n'+r['test'],'PASS\nSIMULATED','Satisfied in scenario; approval pending'])
pdf_table(['Input requirement','Implementation deliverable','Verification scenario','Result','Release conclusion'], rows, [90,112,151,65,W-418])
story.append(PageBreak())
add('Acceptance criteria and evidence records','ReportHeading')
add('These criteria reproduce the input baseline. PASS means the prepared demonstration record satisfies its scripted criterion; it does not attest to real implementation or production effectiveness.')
for index, r in enumerate(S['requirements']):
    if index == 5:
        story.append(PageBreak())
        add('Acceptance criteria continued', 'ReportHeading')
    block=[pp(f'{r["id"]} {r["title"]}','ReportSub'),pp(r['acceptance']),pp(f'{r["testId"]} | {r["evidence"]} | PASS - SIMULATED','SmallCopy'),Spacer(1,6)]
    story.append(KeepTogether(block))
story.append(PageBreak())
add('Completed workflow and assurance scope','ReportHeading')
pdf_table(['CSCF stage','Blueprint nodes','Prepared completion record'],[(f'{s["id"]:02d} {s["name"]}',s['nodes'],'; '.join(t['title'] for t in s['tasks'])) for s in S['stages']], [145,65,W-210])
add('Assurance scope','ReportSub'); add('The prepared route covers the local change, affected source and provider boundaries, and whole-solution purpose and governance. Domains A-F are reviewed against all ten build requirements. This is assurance of the proposed SAE build scenario, not a live SAE assessment of another solution.')
add('Remediation and evidence ceilings','ReportSub'); add('No unresolved defect remains in the scripted verification route. Tests do not establish operating effectiveness. Future observations, policy changes or new evidence can reopen findings and require reassessment. Tactic completion alone never authorizes closure.')
story.append(PageBreak())
add('Human review and release decision','ReportHeading')
add('Approval pending','ReportSub'); add('A real release would require the named authorities to review the exact assessed candidate, its evidence, accepted exceptions, target environment and rollback conditions. The demo does not appoint approvers, record a signature, accept residual risk or deploy a solution.')
pdf_table(['Decision boundary','Required real-world review','Current scenario status'], [('Purpose and acceptance','Product or domain owner','Prepared owner decision only'),('Security and privacy','Named security/privacy authority as applicable','Simulated checks; no real sign-off'),('Residual risk','Authorized risk evaluator and accountable owner','NOT_DETERMINED'),('Production release','Named release approver','APPROVAL PENDING'),('Operational effectiveness','Version-linked monitoring and reassessment','UNOBSERVED')], [130,W-235,105])
add('Demo closing actions','ReportSub'); add('Approve & Deploy and Save & Continue Later both close the view and display DEMO ENDED. Neither action changes this PDF, saves a case, grants real approval or triggers deployment.')
add('Reference and compatibility notes','ReportSub')
for note in SOURCE_NOTES: add(note,'SmallCopy')
add('The supplied documents describe intended architecture. Production schemas, legal applicability, provider controls and operational thresholds require their own validated design and evidence before a real build is authorized.','SmallCopy')

def footer(canvas, pdfdoc):
    canvas.saveState(); canvas.setFont('Body',7.5); canvas.setFillColor(colors.HexColor('#80979f'))
    canvas.drawString(44,27,'CSCF-SAE-DOA-001 | v1.0 | Prepared demo evidence | Approval pending')
    canvas.drawRightString(A4[0]-44,27,str(pdfdoc.page)); canvas.restoreState()

approval_path = OUT / S['approvalFile']
SimpleDocTemplate(str(approval_path),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=45,bottomMargin=48,title='Solution Assurance Engine Document of Approval',author='CSCF',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
manifest = {'scenarioId':S['id'],'version':S['version'],'inputSha256':input_hash,'approvalSha256':hashlib.sha256(approval_path.read_bytes()).hexdigest()}
(ROOT/'src/asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'input':str(input_path),'approval':str(approval_path),'manifest':manifest},indent=2))
