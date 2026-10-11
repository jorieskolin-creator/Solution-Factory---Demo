import { useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, Minus, Plus } from 'lucide-react';
import manifest from './asset-manifest.json';

export default function ApprovalPreview() {
  const [page, setPage] = useState(0);
  const [zoom, setZoom] = useState(1);
  const viewport = useRef<HTMLDivElement>(null);
  const record = manifest.approvalPages[page];

  function move(next: number) {
    setPage(next);
    viewport.current?.scrollTo({ top: 0, left: 0 });
  }

  return <section className="pdf-preview" aria-label="Prepared approval PDF page preview">
    <div className="pdf-toolbar">
      <button className="icon-button" aria-label="Previous PDF page" disabled={page === 0} onClick={() => move(page - 1)}><ChevronLeft size={18}/></button>
      <span aria-live="polite">Page {page + 1} of {manifest.approvalPages.length}</span>
      <button className="icon-button" aria-label="Next PDF page" disabled={page === manifest.approvalPages.length - 1} onClick={() => move(page + 1)}><ChevronRight size={18}/></button>
      <span className="pdf-page-title">{record.title}</span>
      <button className="icon-button" aria-label="Zoom out PDF preview" disabled={zoom <= 1} onClick={() => setZoom(value => value - .25)}><Minus size={16}/></button>
      <span className="pdf-zoom">{Math.round(zoom * 100)}%</span>
      <button className="icon-button" aria-label="Zoom in PDF preview" disabled={zoom >= 2} onClick={() => setZoom(value => value + .25)}><Plus size={16}/></button>
    </div>
    <div className="pdf-page-viewport" ref={viewport} tabIndex={0} role="region" aria-label={`Approval PDF page ${page + 1}, ${record.title}. Scroll to read.`}>
      <div className="pdf-page-sheet" style={{ width: `${zoom * 100}%` }}>
        <img src={`/documents/${record.file}`} alt={`Prepared Document of Approval, page ${page + 1}: ${record.title}. Full text is available in the downloadable PDF.`}/>
      </div>
    </div>
  </section>;
}
