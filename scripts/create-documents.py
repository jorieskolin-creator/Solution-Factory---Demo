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
doc.core_properties.subject = f'{S["id"]} version {S["version"]}'
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
doc.add_heading('Register change intent and entry mode', 1)
para('Blueprint Step 01 intake establishes the declared request before classification, contract creation or execution. The proposed new solution starts with a target-state hypothesis; unknowns remain visible until the accountable owner resolves them.')
fields = [('changeIdentity','Change identity'),('entryMode','Entry mode'),('triggerType','Demand or trigger'),('targetSystem','Target solution'),('accountableOwner','Accountable owner'),('priority','Priority'),('deliveryContext','Delivery context')]
table(['Intake field','Declared value'], [(label,S['intake'][key]) for key,label in fields],[1.6,5.1])
for key,title in [('demand','User demand'),('targetStateHypothesis','Target state hypothesis'),('declaredFacts','Declared facts'),('unknowns','Unresolved information')]:
    doc.add_heading(title,2); para(S['intake'][key])
para('Registration checks: mandatory fields and types, identity and timestamp assignment, ownership validation, duplicate checks and initial scope classification. Missing identifiable purpose or target prevents creation of an executable contract.')

doc.add_page_break()
doc.add_heading('Proposed architecture and boundaries', 1)
for title, text in ARCHITECTURE:
    doc.add_heading(title, 2); para(text)
doc.add_heading('Governance domains', 1)
table(['Domain', 'Assessment coverage'], [(d['id'], d['name'].replace('&', 'and')) for d in S['domains']], [.7, 6])
doc.add_heading('Dependencies and operating assumptions', 1)
para('The real Engine depends on approved source parsers, versioned knowledge collections, identity and access controls, an evidence store, a configured reasoning-adapter registry and operational monitoring. Missing evidence remains UNKNOWN. Raw source bytes and image pixels stay outside provider packets; credentials must never enter audit exports.')
para('The build intake must preserve declared facts and unknowns. Executable contracts require confirmed purpose, target boundary and accountable ownership. Evidence remains distinct from governing knowledge and approval authority.')

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
doc.add_heading('Test selection from intake and governed knowledge', 1)
para(S['testSelection']['method'])
para('The proposed rule snapshot is ' + S['testSelection']['knowledgeSnapshot'] + '. Rules must be governed and independently approved before activation in an implementation. A cognitive model may propose tests or gaps; it cannot remove mandatory checks, infer successful execution or clear blockers.')
table(['Rule pack','Blueprint','Selection basis'],[(p['id'],p['nodes'],p['name']) for p in S['testSelection']['packs']],[1.45,.8,4.45])
doc.add_heading('Required verification scope',2)
para('The registered facts activate 23 knowledge-pack tests and three Additional Tests, producing 26 applicable tests. SAE-TST-08 is recorded as NOT_APPLICABLE because no container target is confirmed. A later container decision reopens classification and makes the image check mandatory.')
para('Structural checks include build, types, lint, schemas, authorized paths, SAST, SCA, secrets, configuration, dependency policy, SBOM and artifact integrity. Behavioral checks include unit, integration, API, end-to-end, negative and adversarial cases, authentication, authorization, recovery, privacy, accessibility, dynamic security and regression. Differential comparison is required; mutation testing is not mandated by this baseline.')
para('Impact review covers candidate changes, dependencies, data flows, permissions and trust boundaries. Evidence checks cover exact citations, revisions, contradictions and finding lock. Policy traces connect source authority to enforced controls, tests, findings and gates. A new solution with changed purpose and trust boundaries requires local, affected-system and whole-solution assurance.')
doc.add_heading('Verification evidence and release rules',2)
para('Record the assessed candidate revision, runner and configuration versions, check identity, actual result, evidence locator, independence limitations and uncovered criteria. Missing execution or decision-critical evidence stays UNKNOWN; documentation alone cannot satisfy a control.')
para(S['testSelection']['gatePolicy'])

doc.add_page_break()
doc.add_heading('Additional Tests (if not included to KB)',1)
para('These owner-requested tests supplement the governed catalogue. They must enter the Verification Contract with an accountable requester, requirement links, measurable pass condition and retained result. They do not replace mandatory knowledge-pack checks.')
for test in S['additionalTests']:
    doc.add_heading(test['id'] + ' ' + test['title'],2)
    para('Requested by: ' + test['requestedBy'] + '. ' + test['reason'])
    para('Requirements: ' + ', '.join(test['requirements']) + '. Blueprint Step ' + test['blueprintNode'] + '.')
    para('Procedure: ' + test['procedure'])
    para('Acceptance criterion: ' + test['acceptance'])
doc.add_heading('Owner confirmation and required output',2)
para(S['intake']['stakeholderAuthority'])
para(S['intake']['expectedOutcome'])

doc.add_page_break()
doc.add_heading('Implementation contract derivation basis', 1)
basis=S['contractBasis']
para(basis['purpose']); para(basis['scope']); para(basis['components'])
doc.add_heading('Protected architecture invariants',2)
for index,boundary in enumerate(basis['boundaries']):
    if index==3:
        doc.add_page_break()
        doc.add_heading('Architecture invariants and output obligations',1)
    doc.add_heading(boundary['id']+' '+boundary['title'],2)
    para(boundary['constraint'])
    para('Requirements: '+', '.join(boundary['requirements'])+'. Verification: '+', '.join(boundary['tests'])+'.')

doc.add_heading('Prohibited changes',2); para(basis['prohibited'])
doc.add_heading('Required output contract',2); para(basis['output']); para(basis['schemaGate']); para(basis['implementationResult'])
doc.add_page_break()
doc.add_heading('Unresolved decisions and activation gates',1)
para('Open intake information is permitted while understanding the request. It must not become an implicit permission or successful check. Each decision has a named role and a gate where it must be resolved.')
for decision in basis['decisions']:
    doc.add_heading(decision['id']+' '+decision['gate'],2)
    para(decision['question']+' Owner: '+decision['owner']+'. '+decision['resolution'])

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
page_titles = ['Approval pending and registered intent']
def next_page(title):
    page_titles.append(title)
    story.append(PageBreak())
    add(title, 'ReportHeading')

add('Solution Assurance Engine', 'ReportTitle')
add('Document of Approval', 'ReportHeading')
add('Approval pending', 'ReportSub')
add('Review the registered intent, requirement traces, selected tests and verification conclusions before authorizing release. Purpose, risk acceptance and deployment require named human authority. The test register retains applicability reasons and exclusions alongside its results.')
pdf_table(['Package field','Reference case record'], [
 ('Input baseline', f'{S["id"]} | version {S["version"]}'),
 ('Approval document', f'CSCF-SAE-DOA-001 | version {S["version"]}'),
 ('Candidate and knowledge snapshot', S['candidateId'] + ' | ' + S['testSelection']['knowledgeSnapshot']),
 ('Date', S['date']),('Test register','26 applicable tests: 23 from rule packs and 3 owner requests; 1 explicit exclusion'),
 ('Release status','APPROVAL PENDING'),('Accountable owner', S['intake']['accountableOwner'])], [142,W-142])
add('Declared purpose', 'ReportSub'); add(S['purpose'])
add('Demand and target state', 'ReportSub'); add(S['intake']['demand']); add(S['intake']['targetStateHypothesis'])
add('Evidence basis', 'ReportSub'); add(S['recordBasis'], 'SmallCopy')
add('Accepted input', 'ReportSub'); add(S['inputFile'], 'SmallCopy'); add(f'SHA-256: {input_hash}', 'SmallCopy')

next_page('Intake and test selection')
pdf_table(['Registered intake field','Declared value'],[(label,S['intake'][key]) for key,label in [('entryMode','Entry mode'),('triggerType','Trigger'),('priority','Priority'),('deliveryContext','Delivery context'),('expectedOutcome','Expected outcome'),('declaredFacts','Facts'),('unknowns','Unresolved information')]], [120,W-120])
add('Selection from governed rules', 'ReportSub'); add(S['testSelection']['method'])
pdf_table(['Pack','Blueprint','Activated coverage'],[(p['id'],p['nodes'],p['name']) for p in S['testSelection']['packs']], [100,60,W-160])
add('Independent review and gate rules', 'ReportSub'); add(S['testSelection']['gatePolicy'], 'SmallCopy')

def test_page(title, records):
    next_page(title)
    add('Results are attached to ' + S['candidateId'] + ' and the input baseline. Requirement references, selection rules and expected behavior are retained for every case.', 'SmallCopy')
    for test in records:
        trigger=', '.join(test['when'])
        block=[pp(test['id'] + ' ' + test['title'], 'ReportSub'),
          pp('Blueprint ' + test['blueprintNode'] + ' | ' + test['ruleId'] + ' | ' + test['result'] + ' | ' + test['evidenceId'], 'SmallCopy'),
          pp('Selected by: ' + trigger + '. Requirements: ' + ', '.join(test['requirements']) + '.', 'SmallCopy'),
          pp('Check: ' + test['procedure']),
          pp('Pass condition: ' + test['acceptance']),
          pp('Result record: ' + test['record']),
          pp('Release conclusion: ' + ('Excluded for this baseline; reselect if the target changes.' if test['result']=='NOT_APPLICABLE' else 'Requirement proof satisfied within the reference case; human release approval pending.'), 'SmallCopy')]
        story.append(KeepTogether(block))

catalog=S['testCatalog']
test_page('Structural and supply chain tests',catalog[:4])
test_page('Supply chain and source integrity continued',catalog[4:8])
test_page('Behavioral and adversarial tests',catalog[8:12])
test_page('Recovery privacy and dynamic security tests',catalog[12:16])
test_page('Regression impact and semantic evidence tests',catalog[16:20])
test_page('Evidence policy and authority tests',catalog[20:23])
test_page('Assurance scope and additional tests',[catalog[23]]+S['additionalTests'])
add('Additional test origin', 'SmallCopy'); add('SAE-ADD-01 through 03 were requested by the solution owner because the generic rule packs do not cover these SAE-specific cross-control interactions. Their procedures and pass conditions repeat the input brief.', 'SmallCopy')

next_page('Response to implementation boundaries')
basis=S['contractBasis']
add(basis['scope']); add('The logical component scope and repository allowlist obligations are retained from the input. Authorized candidate paths still require SAE-DEC-02 resolution before a real executor may run.', 'SmallCopy')
for index,boundary in enumerate(basis['boundaries']):
    if index==3: next_page('Implementation boundaries continued')
    story.append(KeepTogether([pp(boundary['id']+' '+boundary['title'],'ReportSub'),pp(boundary['constraint']),pp('Requirement links: '+', '.join(boundary['requirements'])+'. Checks: '+', '.join(boundary['tests'])+'.','SmallCopy'),pp('Response: '+boundary['response'],'SmallCopy')]))
add('Prohibited changes','ReportSub'); add(basis['prohibited'])
add('Boundary conclusion','ReportSub'); add('The reference records address each invariant. Candidate-specific diffs, enforcement locators and independent runner outputs remain required for an actual execution and release decision. Prohibited changes and an incomplete contract cannot be cleared by these reference results.','SmallCopy')

next_page('Implementation and verification contracts')
for title,text in DELIVERY:
    add(title,'ReportSub'); add(text)
add('Verification Contract scope','ReportSub')
add('The contract binds the 26 applicable test identities and one explicit applicability exclusion to the ten original acceptance scenarios. It records independent verification, negative cases, exact requirement IDs and the mandatory blocker rules. Container selection or other material scope changes reopen impact, applicability and both contracts.')
add('Execution evidence required for authorization','ReportSub')
add('A production candidate requires version-linked runner output, configuration and scanner versions, artifact hashes, evidence locators, independent reviewer records and resolved coverage gaps. No mandatory UNKNOWN can be promoted to PASS. The reference case is not a production candidate release authorization.')
add('Information boundaries and security','ReportSub')
add('Source files remain local to acquisition. Approved summaries and confirmed intake define the reasoning boundary. Access controls protect intake, findings and approval actions. Credential exclusion, dependencies, provenance and publication checks map to the explicit test register.')

next_page('Requirement traceability')
add('Input requirements retain their identity through deliverables, acceptance scenarios, additional test selection and release conclusions. The next pages reproduce the original acceptance criteria.')
rows=[]
for r in S['requirements']:
    rows.append([r['id']+'\n'+r['title'],r['deliverable'],r['testId']+'\n'+r['test'],'PASS','Reference case satisfied; approval pending'])
pdf_table(['Input requirement','Implementation deliverable','Verification scenario','Result','Release conclusion'],rows,[90,112,151,45,W-398])

next_page('Acceptance criteria and evidence records')
add('These criteria repeat the accepted input baseline. The test register above supplies structural, behavioral, impact, evidence and policy coverage in addition to the original acceptance scenarios.', 'SmallCopy')
for index,r in enumerate(S['requirements']):
    if index==5: next_page('Acceptance criteria continued')
    related=[x['id'] for x in S['testCatalog']+S['additionalTests'] if r['id'] in x['requirements'] and x['id'] in S['selectedTestIds']]
    story.append(KeepTogether([pp(r['id']+' '+r['title'],'ReportSub'),pp(r['acceptance']),pp(r['testId']+' | '+r['evidence']+' | PASS','SmallCopy'),pp('Selected tests: '+', '.join(related),'SmallCopy'),Spacer(1,4)]))

next_page('Completed activities and assurance scope')
pdf_table(['CSCF stage','Blueprint','Completion record'],[(f'{s["id"]:02d} {s["name"]}',s['nodes'],'; '.join(x['title'] for x in s['tasks'])) for s in S['stages']],[145,55,W-200])
add('Scope selection','ReportSub')
pdf_table(['Scope','Trigger and coverage','Conclusion'],[
 ('Local change','Required for every change; all ten requirements and direct controls.','SELECTED'),
 ('Affected system','Evidence intake, provider packets, identities, dependencies and canonical views touch trust boundaries.','SELECTED'),
 ('Whole solution','New solution, target purpose, bounded reasoning and lifecycle authority activate A-F assurance.','SELECTED')],[100,W-180,80])
add('Coverage and limitations','ReportSub'); add('All 180 primary work items are accounted for by SAE-TST-17. Operating effectiveness is UNOBSERVED until version-linked operational evidence exists. Mutation testing is not mandated; the unconfirmed container target is an explicit applicability exclusion. New evidence or changed boundaries can reopen findings and the assurance scope.','SmallCopy')

next_page('Output obligations and unresolved decisions')
add('Canonical output response','ReportSub'); add(basis['output']); add(basis['schemaGate'], 'SmallCopy')
add('Verification response: SAE-TST-02, SAE-TST-18 and SAE-ADD-03 cover schema integrity, authorized impact and identical canonical views. A complete approved schema and a repository-linked ImplementationResult are required deliverables, not attached production evidence.', 'SmallCopy')
add('Decision questions from the intake','ReportSub')
for decision in basis['decisions']:
    story.append(KeepTogether([pp(decision['id']+' '+decision['gate'],'ReportSub'),pp(decision['question']),pp('Authority: '+decision['owner']+'. Status: OPEN. '+decision['resolution'],'SmallCopy')]))
add('Answer to the new build starting question','ReportSub'); add(basis['releaseAnswer'])

next_page('Human review and release decision')
add('Approval pending','ReportSub')
add('Review the exact candidate, execution evidence, accepted exceptions, target environment and rollback conditions before authorization. The reference package preserves the release decision for named human authorities.')
pdf_table(['Decision boundary','Required authority or evidence','Status'],[
 ('Purpose and scope','Accountable solution owner; confirmed intake and accepted criteria.','REVIEW REQUIRED'),
 ('Security and privacy','Named security and privacy authority; attributable enforced-control proof.','REVIEW REQUIRED'),
 ('Risk acceptance','Authorized evaluator and accountable owner.','NOT_DETERMINED'),
 ('Production release','Named release approver; assessed revision and target environment.','APPROVAL PENDING'),
 ('Operating effectiveness','Version-linked observations and reassessment.','UNOBSERVED')],[110,W-215,105])
add('Open decisions','ReportSub')
for decision in DECISIONS: add(decision,'SmallCopy')
add('Reference basis','ReportSub')
for note in SOURCE_NOTES: add(note,'SmallCopy')

def footer(canvas,pdfdoc):
    canvas.saveState(); canvas.setFont('Body',7.5); canvas.setFillColor(colors.HexColor('#80979f'))
    canvas.drawString(44,27,f'CSCF-SAE-DOA-001 | v{S["version"]} | Reference verification record | Approval pending')
    canvas.drawRightString(A4[0]-44,27,str(pdfdoc.page)); canvas.restoreState()

approval_path = OUT / S['approvalFile']
SimpleDocTemplate(str(approval_path),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=45,bottomMargin=48,title='Solution Assurance Engine Document of Approval',author='CSCF',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
manifest = {'scenarioId':S['id'],'version':S['version'],'inputSha256':input_hash,'approvalSha256':hashlib.sha256(approval_path.read_bytes()).hexdigest(), 'approvalPageTitles':page_titles}
(ROOT/'src/asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'input':str(input_path),'approval':str(approval_path),'manifest':manifest},indent=2))
