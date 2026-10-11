"""Rasterize the finalized approval PDF for a reliable static browser preview."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--pdftoppm', default='pdftoppm')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
scenario = json.loads((root / 'src/scenario.json').read_text())
manifest_path = root / 'src/asset-manifest.json'
manifest = json.loads(manifest_path.read_text())
pdf = root / 'public/documents' / scenario['approvalFile']
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == manifest['approvalSha256']
titles = ['Approval pending and input identity', 'Implementation and verification contracts',
          'Requirement traceability', 'Acceptance criteria and evidence records',
          'Acceptance criteria continued', 'Completed workflow and assurance scope',
          'Human review and release decision']
out = root / 'public/documents/approval-preview'
out.mkdir(parents=True, exist_ok=True)
pages = []
scratch = root / '.qa/temp'
scratch.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch, prefix='preview-') as folder:
    assert Path(folder).resolve().is_relative_to(scratch.resolve())
    subprocess.run([args.pdftoppm, '-scale-to', '2000', '-png', str(pdf), str(Path(folder) / 'page')], check=True)
    rendered = sorted(Path(folder).glob('page-*.png'))
    assert len(rendered) == len(titles)
    for index, (source, title) in enumerate(zip(rendered, titles), 1):
        target = out / f'page-{index}.webp'
        with Image.open(source) as page:
            page.convert('RGB').save(target, 'WEBP', lossless=True, method=6)
        pages.append({'file': f'approval-preview/{target.name}', 'title': title,
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
manifest['previewSourceSha256'] = manifest['approvalSha256']
manifest['approvalPages'] = pages
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Prepared {len(pages)} fixed PDF preview pages. Original document fingerprints unchanged.')
