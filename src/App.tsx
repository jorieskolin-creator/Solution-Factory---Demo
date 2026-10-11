import { useEffect, useReducer, useRef, useState } from 'react';
import { Activity, ArrowDownToLine, ArrowRight, BookOpen, Check, ChevronRight, CircleCheck, Clock3, FileCheck2, FileText, Fingerprint, Layers3, LockKeyhole, Pause, Play, RotateCcw, ShieldCheck, Upload, X, XCircle } from 'lucide-react';
import scenario from './scenario.json' with { type: 'json' };
import manifest from './asset-manifest.json';
import ApprovalPreview from './ApprovalPreview';
import TestRegister from './TestRegister';
import { acceptsInput, currentTask, formatTime, initialRun, runReducer, taskTimeline, TOTAL_SECONDS, WRONG_INPUT } from './engine';

const inputURL = `/documents/${scenario.inputFile}`;
const approvalURL = `/documents/${scenario.approvalFile}`;
const stageIcons = [Layers3, ShieldCheck, FileCheck2, FileText, Play, CircleCheck, Layers3, LockKeyhole];
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
type UploadState = { checking: boolean; error: boolean; filename: string };
const emptyUpload: UploadState = { checking: false, error: false, filename: '' };

export default function App() {
  const [run, dispatch] = useReducer(runReducer, initialRun);
  const [uploads, setUploads] = useState<UploadState[]>([{ ...emptyUpload }, { ...emptyUpload }, { ...emptyUpload }]);
  const [inspection, setInspection] = useState<number | null>(null);
  const [view, setView] = useState<'factory' | 'requirements' | 'tests'>('factory');
  const [showReport, setShowReport] = useState(true);
  const uploadGenerations = useRef([0, 0, 0]);
  const reviewRef = useRef<HTMLDialogElement>(null);
  const detailRef = useRef<HTMLElement>(null);
  const reviewButton = useRef<HTMLButtonElement>(null);
  const activeStage = useRef<HTMLButtonElement>(null);
  const task = currentTask(run.elapsed);
  const completed = taskTimeline.filter(t => t.end <= run.elapsed);
  const ready = run.mode === 'ready';
  const activeRun = ['running', 'paused', 'review'].includes(run.mode);
  const buildStarted = activeRun || run.mode === 'ended';
  const inspectionStage = inspection === null ? null : scenario.stages[inspection];

  useEffect(() => {
    const stage = activeStage.current;
    const strip = stage?.closest('.pipeline-scroll');
    if (stage && strip) strip.scrollTo({ left: stage.offsetLeft - (strip as HTMLElement).offsetLeft - strip.clientWidth / 2 + stage.clientWidth / 2, behavior: 'smooth' });
  }, [task.stageIndex, run.mode]);

  useEffect(() => {
    if (run.mode !== 'running') return;
    let last = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now(); const delta = (now - last) / 1000; last = now;
      if (document.hidden) dispatch({ type: 'HIDE' }); else dispatch({ type: 'TICK', delta });
    }, 100);
    const hidden = () => { if (document.hidden) dispatch({ type: 'HIDE' }); };
    document.addEventListener('visibilitychange', hidden);
    return () => { clearInterval(timer); document.removeEventListener('visibilitychange', hidden); };
  }, [run.mode]);
  useEffect(() => {
    const dialog = reviewRef.current;
    if (run.mode === 'review' && showReport && dialog && !dialog.open) dialog.showModal();
    else if (dialog?.open) dialog.close();
  }, [run.mode, showReport]);

  async function upload(line: number, file?: File) {
    if (!file || (line === 1 && run.mode !== 'idle')) return;
    const generation = ++uploadGenerations.current[line - 1];
    setUploads(previous => previous.map((item, index) => index === line - 1 ? { checking: true, error: false, filename: file.name } : item));
    const [accepted] = await Promise.all([acceptsInput(line, file, manifest.inputSha256), sleep(1000)]);
    if (generation !== uploadGenerations.current[line - 1]) return;
    setUploads(previous => previous.map((item, index) => index === line - 1 ? { ...item, checking: false, error: !accepted } : item));
    if (accepted) { dispatch({ type: 'ACCEPT' }); setInspection(null); }
  }
  function reset() {
    uploadGenerations.current = uploadGenerations.current.map(value => value + 1);
    setUploads([{ ...emptyUpload }, { ...emptyUpload }, { ...emptyUpload }]);
    setInspection(null); setShowReport(true); dispatch({ type: 'RESET' });
  }
  function inspect(index: number) {
    if (run.elapsed < taskTimeline.find(t => t.stageIndex === index)!.start && run.mode !== 'ended') return;
    if (!activeRun && run.mode !== 'ended') return;
    setInspection(index);
    requestAnimationFrame(() => detailRef.current?.focus());
  }
  function endDemo() { setShowReport(false); setInspection(null); dispatch({ type: 'END' }); }

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" aria-label="CSCF home"><span className="brand-mark"><Layers3 size={24}/></span><span>CSCF<span className="brand-sub">SOLUTION FACTORY</span></span></a>
      <div className="workspace-label">WORKSPACE</div>
      <button className={`nav-item ${view === 'factory' ? 'selected' : ''}`} onClick={() => setView('factory')}><Layers3 size={19}/> Factory overview <span className="nav-count">3</span></button>
      <button className={`nav-item ${view === 'requirements' ? 'selected' : ''}`} onClick={() => setView('requirements')}><BookOpen size={19}/> Build requirements</button>
      <button className={`nav-item ${view === 'tests' ? 'selected' : ''}`} onClick={() => setView('tests')}><ShieldCheck size={19}/> Test register</button>
      <a className="nav-item" href={inputURL} download><FileText size={19}/> Input document <ArrowDownToLine size={15}/></a>
      <div className="sidebar-bottom"><div className="environment-dot"/> CONTROLLED WORKSPACE<p>Governed requirements<br/>Human release authority</p><div className="sidebar-profile"><span>JS</span><div>Jori Eskolin<small>Solution owner</small></div></div></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb">Workspace <ChevronRight size={14}/> <strong>{view === 'factory' ? 'Factory overview' : view === 'tests' ? 'Test register' : 'Build requirements'}</strong></div><span className="demo-badge"><span/> Release workspace</span></header>
      <main>
        <section className="page-heading"><div><div className="eyebrow">CONTINUOUS SOLUTION CREATION FLOW</div><h1>{view === 'factory' ? 'Solution Creation Factory' : 'Solution Assurance Engine'}</h1><p>{view === 'factory' ? 'From approved intent to evidence-backed release readiness.' : 'One declared baseline. Ten requirements. A traceable approval package.'}</p></div><a className="button primary download-input" href={inputURL} download><ArrowDownToLine size={18}/> Download Input Document</a></section>
        {view === 'tests' ? <TestRegister complete={run.mode === 'review' || run.mode === 'ended'}/> : view === 'requirements' ? <section className="requirements-page"><div className="baseline-header"><FileText/><div><h2>New Build Brief</h2><p>{scenario.id} · Version {scenario.version}</p></div><span className="tag">CONTROLLED BASELINE</span></div><p className="purpose">{scenario.purpose}</p><div className="requirements-grid">{scenario.requirements.map(req => <article className="requirement-card" key={req.id}><span className="mono">{req.id}</span><h3>{req.title}</h3><p>{req.requirement}</p><strong>Acceptance criterion</strong><p>{req.acceptance}</p><div className="requirement-test"><ShieldCheck size={16}/>{req.testId}<span>Domains {req.domain}</span></div></article>)}</div></section> : <>
          <section className="summary-grid" aria-label="Factory status"><div><span className="stat-icon"><Layers3/></span><div><small>Production lines</small><strong>03 <span>one active route</span></strong></div></div><div><span className="stat-icon"><Activity/></span><div><small>Current build</small><strong>{activeRun || ready ? '01' : '00'} <span>{run.mode === 'ended' ? 'workflow complete' : activeRun || ready ? 'Solution Assurance Engine' : 'ready for intake'}</span></strong></div></div>{buildStarted && <div><span className="stat-icon"><Clock3/></span><div><small>Workflow duration</small><strong>2:30 <span>pause at any time</span></strong></div></div>}</section>
          <section className="factory-board" aria-label="Production lines"><div className="section-heading"><h2><span className="live-dot"/> Production floor</h2><span className="foundation"><ShieldCheck size={14}/> Governed foundation configured</span></div>
            {[1, 2, 3].map(line => {
              const item = uploads[line - 1]; const isMain = line === 1;
              const status = item.checking ? 'Checking input' : item.error ? 'Input rejected' : isMain && run.mode !== 'idle' ? ({ ready: 'Ready to build', running: 'Build in progress', paused: 'Build paused', review: 'Awaiting approval', ended: 'Demo ended' } as const)[run.mode as Exclude<typeof run.mode, 'idle'>] : 'Awaiting input';
              return <article className={`production-line ${isMain ? 'main-line' : 'secondary-line'} ${item.error ? 'rejected-line' : ''}`} key={line}>
                <div className="line-top"><div className="line-name"><span className="line-number">0{line}</span><div><h3>Solution line {line}</h3><p>{isMain && run.mode !== 'idle' ? 'Solution Assurance Engine' : isMain ? 'New build intake' : 'Contract validation'}</p></div>{isMain && <span className="tag line-demo">FULL WORKFLOW</span>}</div><span className={`status-pill ${item.error ? 'danger' : isMain && activeRun ? 'teal' : ''}`}><span className={item.checking || isMain && run.mode === 'running' ? 'pulse-dot' : ''}/>{status}</span></div>
                {isMain ? <>
                  <div className="pipeline-scroll"><div className="pipeline">{scenario.stages.map((stage, index) => {
                    const Icon = stageIcons[index]; const start = taskTimeline.find(t => t.stageIndex === index)!.start;
                    const done = index < 7 && run.elapsed >= start + stage.duration; const current = activeRun && task.stageIndex === index;
                    return <button key={stage.id} ref={current ? activeStage : null} className={`stage ${done ? 'done' : ''} ${current ? 'current' : ''} ${inspection === index ? 'inspecting' : ''}`} onClick={() => inspect(index)} disabled={(!activeRun && run.mode !== 'ended') || run.elapsed < start} aria-label={`${stage.name}, ${done ? 'complete' : current ? 'active' : run.mode === 'ended' && index === 7 ? 'demo ended' : 'pending'}`}><div className="stage-top"><span>0{stage.id}</span>{done ? <Check size={14}/> : <Icon size={15}/>}</div><span className="stage-name">{stage.name}</span><span className="stage-state">{done ? 'Complete' : current ? run.mode === 'review' ? 'Approval pending' : run.mode === 'paused' ? 'Paused' : 'In progress' : run.mode === 'ended' && index === 7 ? 'Demo ended' : 'Pending'}</span>{index === 7 && <small className="deployment-inactive">Deployment inactive</small>}</button>;
                  })}<div className="stage beyond"><div className="stage-top"><span>09</span><LockKeyhole size={15}/></div><span className="stage-name">Production & Monitoring</span><span className="stage-state">Awaiting release</span></div></div></div>
                  <div className="line-footer"><div className="line-help">{item.error ? <><XCircle size={17}/><span role="alert">{WRONG_INPUT}</span></> : item.checking ? <><Fingerprint size={17}/><span>Checking document fingerprint locally…</span></> : run.mode === 'idle' ? <><FileText size={17}/><span>Use the prepared SAE brief to start this line.</span></> : <><FileCheck2 size={17}/><span>{scenario.id} · v{scenario.version} <span className="verified-label">Verified input</span></span></>}</div>
                    {run.mode === 'idle' ? <UploadButton line={line} checking={item.checking} upload={upload}/> : ready ? <button className="button primary small" onClick={() => dispatch({ type: 'START' })}><Play size={15}/> Start Build</button> : run.mode === 'running' ? <button className="button secondary small" onClick={() => dispatch({ type: 'PAUSE' })}><Pause size={15}/> Pause build</button> : run.mode === 'paused' ? <button className="button primary small" onClick={() => { if (!document.hidden) dispatch({ type: 'RESUME' }); }}><Play size={15}/> Resume build</button> : run.mode === 'review' ? <button ref={reviewButton} className="button primary small" onClick={() => setShowReport(true)}><FileCheck2 size={15}/> Review approval</button> : <button className="button secondary small" onClick={reset}><RotateCcw size={15}/> Restart demo</button>}
                  </div>
                </> : <div className="secondary-body"><div className="idle-track">{Array.from({ length: 8 }, (_, i) => <span key={i}/>)}</div><div className="secondary-actions">{item.error ? <p className="rejection" role="alert"><XCircle size={16}/>{WRONG_INPUT}</p> : <p>{item.checking ? 'Checking contract material…' : 'Upload material for contract validation.'}</p>}<UploadButton line={line} checking={item.checking} upload={upload}/></div></div>}
              </article>;
            })}
          </section>
          <section className="workspace-grid">
            <section className="activity-panel" ref={detailRef} tabIndex={-1} aria-label="Build activity">
              <div className="section-heading"><h2><Activity size={18}/> {inspectionStage ? 'Stage inspection' : 'Build activity'}</h2>{inspectionStage && <button className="text-button" onClick={() => setInspection(null)}>Return to live activity <ArrowRight size={14}/></button>}{buildStarted && <span className="muted mono">{formatTime(run.elapsed)} / 2:30</span>}</div>
              {run.mode === 'ended' ? <div className="ended-state" role="status"><CircleCheck size={38}/><div className="eyebrow">WORKFLOW COMPLETE</div><h2>DEMO ENDED.</h2><p>Your Solution Assurance Engine walkthrough is complete.</p><button className="button primary" onClick={reset}><RotateCcw size={16}/> Start a new demonstration</button></div> : inspectionStage ? <div className="inspection-content"><span className="eyebrow">STAGE 0{inspectionStage.id} · BLUEPRINT {inspectionStage.nodes}</span><h3>{inspectionStage.name}</h3>{inspectionStage.tasks.map((t, i) => <div className="inspection-task" key={i}><CircleCheck size={17}/><div><h4>{t.title}</h4><p>{t.detail}</p><Refs refs={[...t.refs, ...t.testRefs]}/></div></div>)}</div> : activeRun ? <>
                <div className="current-task"><div className="task-title-row"><span className={`task-icon ${run.mode === 'running' ? 'working' : ''}`}>{run.mode === 'paused' ? <Pause size={22}/> : run.mode === 'review' ? <LockKeyhole size={22}/> : <Activity size={22}/>}</span><div><span className="eyebrow">STAGE 0{task.stageIndex + 1} · {run.mode === 'review' ? 'HUMAN DECISION' : run.mode === 'paused' ? 'PAUSED' : 'ONGOING TASK'}</span><h3>{run.mode === 'review' ? 'Ready for approval review' : task.title}</h3></div></div><p>{run.mode === 'review' ? 'The evidence package is ready for review. Check test coverage, results and release conditions before your decision.' : task.detail}</p><Refs refs={[...task.refs, ...task.testRefs]}/>{run.hiddenPause && <p className="pause-note">The build paused while this tab was hidden. Resume when you are ready.</p>}<div className="progress-meta"><span>{completed.length} of {taskTimeline.length} tasks complete</span><span>{Math.floor(run.elapsed / TOTAL_SECONDS * 100)}%</span></div><progress value={run.elapsed} max={TOTAL_SECONDS} aria-label="Build progress"/></div>
                <div className="activity-log"><div className="log-heading">COMPLETED ACTIVITIES <span>{completed.length}</span></div>{[...completed].reverse().map(t => <div className="log-item" key={`${t.stageIndex}-${t.taskIndex}`}><Check size={15}/><div><strong>{t.title}</strong><small>Stage 0{t.stageIndex + 1} · {t.refs.join(' / ')}</small></div><time>{formatTime(t.end)}</time></div>)}{completed.length === 0 && <p className="muted">Completed tasks will appear here as the build progresses.</p>}</div>
              </> : ready ? <div className="intake-summary"><span className="intake-check"><CircleCheck/></span><div className="eyebrow">INPUT VERIFIED</div><h3>Solution Assurance Engine</h3><p>{scenario.purpose}</p><div className="intake-facts"><div><small>Baseline</small><strong>{scenario.id}</strong></div><div><small>Requirements</small><strong>10 acceptance criteria</strong></div><div><small>Governance</small><strong>Six domains A–F</strong></div></div><p className="intake-note"><Fingerprint size={15}/> This document matches the controlled v{scenario.version} baseline.</p><button className="button primary" onClick={() => dispatch({ type: 'START' })}><Play size={16}/> Start Build <ArrowRight size={16}/></button></div> : <div className="empty-activity"><span className="empty-icon"><Upload size={28}/></span><h3>Your next solution starts here</h3><p>Download the New Build Brief, then add it to Solution line 1.<br/>Follow the work from intake to the release gate.</p><div className="onboarding-steps"><span><b>1</b> Download brief</span><ChevronRight size={14}/><span><b>2</b> Add New Build</span><ChevronRight size={14}/><span><b>3</b> Review approval</span></div></div>}
            </section>
            <aside className="context-panel"><div className="section-heading"><h2><FileText size={18}/> Build context</h2></div><div className="context-body"><span className="tag">NEW BUILD · VERSION {scenario.version}</span><h3>Solution Assurance<br/>Engine</h3><p>Evidence-gated readiness analysis with deterministic controls and named human decision authority.</p><dl><div><dt>Document</dt><dd>{scenario.id}</dd></div><div><dt>Workflow</dt><dd>8 stages · 21 tasks</dd></div><div><dt>Acceptance</dt><dd>10 traceable requirements</dd></div><div><dt>Evidence</dt><dd>Verification register</dd></div></dl><div className="domain-list"><span className="eyebrow">GOVERNANCE DOMAINS</span>{scenario.domains.map(d => <div key={d.id}><b>{d.id}</b><span>{d.name}</span></div>)}</div><button className="text-button" onClick={() => setView('requirements')}>Explore the requirements <ArrowRight size={15}/></button></div><div className="context-foot"><LockKeyhole size={16}/><span>Approval remains a human decision.</span></div></aside>
          </section>
        </>}
        <footer className="page-footer"><span>CSCF · Standardized flow. Adaptive solutions.</span><span>Requirements · Verification · Human approval</span></footer>
      </main>
    </div>
    <dialog ref={reviewRef} className="approval-dialog" onCancel={event => { event.preventDefault(); setShowReport(false); reviewButton.current?.focus(); }} aria-labelledby="approval-title">
      <div className="approval-header"><div><div className="eyebrow">RELEASE GATE · HUMAN DECISION</div><h2 id="approval-title">Document of Approval</h2><p>Solution Assurance Engine · {scenario.id} · v{scenario.version}</p></div><button className="icon-button" aria-label="Close approval review" onClick={() => { setShowReport(false); reviewButton.current?.focus(); }}><X/></button></div>
      <div className="approval-summary"><span><CircleCheck size={18}/> Verification register complete</span><span><LockKeyhole size={18}/> Approval pending</span><a className="button secondary small" href={approvalURL} download><ArrowDownToLine size={16}/> Download approval PDF</a></div>
      {run.mode === 'review' && <ApprovalPreview/>}
      <div className="approval-fallback"><a href={approvalURL} target="_blank" rel="noreferrer">Open the full approval PDF</a>. Review selected tests, results, exclusions and release conditions.</div>
      <div className="approval-actions"><p>Either choice ends this demonstration.</p><button className="button secondary" onClick={endDemo}>Save &amp; Continue Later</button><button className="button primary" onClick={endDemo}><Check size={17}/> Approve &amp; Deploy</button></div>
    </dialog>
  </div>;
}
function Refs({ refs }: { refs: string[] }) { return <div className="refs">{refs.map(ref => <span key={ref}>{ref}</span>)}</div>; }
function UploadButton({ line, checking, upload }: { line: number; checking: boolean; upload: (line: number, file?: File) => void }) {
  const input = useRef<HTMLInputElement>(null);
  return <><input ref={input} className="file-input" type="file" aria-label={`Upload New Build document to Solution line ${line}`} disabled={checking} onChange={event => { void upload(line, event.target.files?.[0]); event.target.value = ''; }}/><button className="button secondary small" disabled={checking} onClick={() => input.current?.click()}><Upload size={15}/>{checking ? 'Checking…' : 'New Build'}</button></>;
}
