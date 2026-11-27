// Staging deploy helper (used from the Cloudflare dashboard "New deployment" upload page while the Git connection is broken).
// Loads public/ of a commit from GitHub and puts it into the folder input of the uploader, with correct content types.
window.seoproUpload = async function (sha) {
  const T = {html:'text/html',css:'text/css',js:'text/javascript',xml:'application/xml',txt:'text/plain',svg:'image/svg+xml',jpg:'image/jpeg',png:'image/png',woff2:'font/woff2'};
  const tree = await (await fetch('https://api.github.com/repos/Buyseech/seopro-site/git/trees/' + sha + '?recursive=1')).json();
  const files = tree.tree.filter(t => t.type === 'blob' && t.path.startsWith('public/')).map(t => t.path);
  const inp = [...document.querySelectorAll('input[type=file]')].find(i => i.webkitdirectory);
  const dt = new DataTransfer();
  await Promise.all(files.map(async p => {
    const r = await fetch('https://raw.githubusercontent.com/Buyseech/seopro-site/' + sha + '/' + p);
    if (!r.ok) throw new Error(p + ' ' + r.status);
    const b = await r.arrayBuffer();
    const f = new File([b], p.split('/').pop(), {type: T[p.split('.').pop()] || 'application/octet-stream'});
    Object.defineProperty(f, 'webkitRelativePath', {value: p});
    dt.items.add(f);
  }));
  inp.files = dt.files;
  inp.dispatchEvent(new Event('change', {bubbles: true}));
  return {n: files.length, types: [...inp.files].slice(0, 3).map(f => f.name + ':' + f.type)};
};
