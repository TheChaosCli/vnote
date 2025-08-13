import React, { useEffect, useState } from 'react'

const api = {
  async login(email: string, password: string) {
    const r = await fetch('/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
    if (!r.ok) throw new Error('login failed')
    return r.json()
  },
  async register(email: string, password: string) {
    const r = await fetch('/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
    if (!r.ok) throw new Error('register failed')
    return r.json()
  },
  async notes(token: string) {
    const r = await fetch('/notes', { headers: { Authorization: `Bearer ${token}` } })
    if (!r.ok) throw new Error('notes failed')
    return r.json()
  },
  async createNote(token: string, title: string, body?: string) {
    const r = await fetch('/notes', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ title, body }) })
    if (!r.ok) throw new Error('create failed')
    return r.json()
  },
}

export function App() {
  const [email, setEmail] = useState('you@example.com')
  const [password, setPassword] = useState('pass')
  const [token, setToken] = useState<string | null>(null)
  const [notes, setNotes] = useState<any[]>([])
  const [title, setTitle] = useState('Hello')
  const [tags, setTags] = useState<any[]>([])
  const [newTag, setNewTag] = useState('')
  const [folders, setFolders] = useState<any[]>([])
  const [folderName, setFolderName] = useState('New Folder')
  const [file, setFile] = useState<File | null>(null)
  const [attachmentId, setAttachmentId] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  // Notes editor state
  const [selectedNote, setSelectedNote] = useState<any | null>(null)
  const [noteBody, setNoteBody] = useState('')
  const [backlinks, setBacklinks] = useState<any[]>([])
  // Graph
  const [graph, setGraph] = useState<{nodes:any[];edges:any[]}>({nodes:[],edges:[]})
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  // Repos
  const [repos, setRepos] = useState<any[]>([])
  const [repoName, setRepoName] = useState('my-repo')
  const [currentRepo, setCurrentRepo] = useState<string | null>(null)
  const [files, setFiles] = useState<any[]>([])
  const [filePath, setFilePath] = useState('README.md')
  const [fileContent, setFileContent] = useState('Hello repo')
  const [commits, setCommits] = useState<any[]>([])
  const [commitA, setCommitA] = useState<string>('')
  const [commitB, setCommitB] = useState<string>('')
  const [diff, setDiff] = useState<string[]>([])

  const onRegister = async () => {
    const res = await api.register(email, password)
    setToken(res.accessToken)
  }
  const onLogin = async () => {
    const res = await api.login(email, password)
    setToken(res.accessToken)
  }
  const refreshNotes = async () => {
    if (!token) return
    const res = await api.notes(token)
    setNotes(res)
  }
  const openNote = async (id: string) => {
    if (!token) return
    const r = await fetch(`/notes/${id}`, { headers: { Authorization: `Bearer ${token}` }})
    if (r.ok) {
      const n = await r.json()
      setSelectedNote(n)
      setNoteBody(n.body || '')
      const bl = await fetch(`/notes/${id}/backlinks`, { headers: { Authorization: `Bearer ${token}` }})
      setBacklinks(bl.ok ? await bl.json() : [])
    }
  }
  const saveNote = async () => {
    if (!token || !selectedNote) return
    const r = await fetch(`/notes/${selectedNote.id}`, { method:'PATCH', headers: { 'Content-Type':'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ title: selectedNote.title, body: noteBody }) })
    if (r.ok) { await openNote(selectedNote.id) }
  }
  const loadGraph = async () => {
    if (!token) return
    const r = await fetch('/graph', { headers: { Authorization: `Bearer ${token}` }})
    if (r.ok) setGraph(await r.json())
  }
  const onSelectNode = async (id: string) => {
    setSelectedNodeId(id)
    await openNote(id)
  }
  const refreshTags = async () => {
    if (!token) return
    const r = await fetch('/tags', { headers: { Authorization: `Bearer ${token}` }})
    setTags(await r.json())
  }
  const refreshFolders = async () => {
    if (!token) return
    const r = await fetch('/folders/tree', { headers: { Authorization: `Bearer ${token}` }})
    const data = await r.json()
    setFolders(data.roots || [])
  }
  const onCreate = async () => {
    if (!token) return
    await api.createNote(token, title, 'This is a note with a link to [[Welcome]]')
    await refreshNotes()
  }
  const onCreateTag = async () => {
    if (!token || !newTag.trim()) return
    await fetch('/tags', { method: 'POST', headers: { 'Content-Type':'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ name: newTag }) })
    setNewTag('')
    await refreshTags()
  }
  const onCreateFolder = async () => {
    if (!token || !folderName.trim()) return
    await fetch('/folders', { method: 'POST', headers: { 'Content-Type':'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ name: folderName }) })
    setFolderName('New Folder')
    await refreshFolders()
  }
  const onUpload = async () => {
    if (!token || !file) return
    const fd = new FormData()
    fd.append('file', file)
    const r = await fetch('/attachments', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
    const data = await r.json()
    setAttachmentId(data.id)
  }
  const onSearch = async () => {
    if (!token || !query.trim()) return
    const r = await fetch(`/search?q=${encodeURIComponent(query)}`, { headers: { Authorization: `Bearer ${token}` }})
    setResults(await r.json())
  }
  const refreshRepos = async () => {
    if (!token) return
    const r = await fetch('/repos', { headers: { Authorization: `Bearer ${token}` }})
    setRepos(await r.json())
  }
  const onCreateRepo = async () => {
    if (!token || !repoName.trim()) return
    const r = await fetch(`/repos?name=${encodeURIComponent(repoName)}`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }})
    if (r.ok) { setRepoName('my-repo'); await refreshRepos() }
  }
  const selectRepo = async (id: string) => {
    setCurrentRepo(id)
    const r = await fetch(`/repos/${id}/files`, { headers: { Authorization: `Bearer ${token}` }})
    setFiles(await r.json())
    const c = await fetch(`/repos/${id}/commits`, { headers: { Authorization: `Bearer ${token}` }})
    setCommits(await c.json())
  }
  const loadFile = async () => {
    if (!token || !currentRepo || !filePath) return
    const r = await fetch(`/repos/${currentRepo}/files/${encodeURIComponent(filePath)}`, { headers: { Authorization: `Bearer ${token}` }})
    if (r.ok) {
      const data = await r.json()
      setFileContent(data.content)
    }
  }
  const saveFile = async () => {
    if (!token || !currentRepo || !filePath) return
    const r = await fetch(`/repos/${currentRepo}/files?path=${encodeURIComponent(filePath)}&message=${encodeURIComponent('update via UI')}`, {
      method: 'POST', headers: { 'Content-Type':'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ content: fileContent })
    })
    if (r.ok) { await selectRepo(currentRepo) }
  }
  const makeMultiCommit = async () => {
    if (!token || !currentRepo) return
    const body = { message: 'multi update', files: [{ path: filePath, content: fileContent }] }
    const r = await fetch(`/repos/${currentRepo}/commit`, { method: 'POST', headers: { 'Content-Type':'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify(body) })
    if (r.ok) { await selectRepo(currentRepo) }
  }
  const loadDiff = async () => {
    if (!token || !currentRepo || !commitA || !commitB || !filePath) return
    const r = await fetch(`/repos/${currentRepo}/diff?commitA=${encodeURIComponent(commitA)}&commitB=${encodeURIComponent(commitB)}&path=${encodeURIComponent(filePath)}`, { headers: { Authorization: `Bearer ${token}` }})
    if (r.ok) { const d = await r.json(); setDiff(d.diff || []) }
  }

  useEffect(() => {
    if (token) {
      refreshNotes(); refreshTags(); refreshFolders(); refreshRepos()
    }
  }, [token])

  return (
    <div style={{ fontFamily: 'system-ui', padding: 16 }}>
      <h1>VNote</h1>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} />
        <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <button onClick={onRegister}>Register</button>
        <button onClick={onLogin}>Login</button>
      </div>
      {token && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input placeholder="New note title" value={title} onChange={e => setTitle(e.target.value)} />
            <button onClick={onCreate}>Create</button>
            <button onClick={refreshNotes}>Refresh</button>
          </div>
          <ul>
            {notes.map((n: any) => (
              <li key={n.id}>
                <button onClick={()=>openNote(n.id)} style={{ marginRight:8 }}>Open</button>
                <strong>{n.title}</strong> <small>{n.excerpt}</small>
              </li>
            ))}
          </ul>
          {selectedNote && (
            <div style={{ border:'1px solid #ddd', padding:8, marginTop:8 }}>
              <h3>Edit: {selectedNote.title}</h3>
              <Editor value={noteBody} onChange={setNoteBody} />
              <div style={{ display:'flex', gap:8, marginTop:8 }}>
                <button onClick={saveNote}>Save</button>
              </div>
              <div>
                <h4>Backlinks</h4>
                <ul>
                  {backlinks.map((b:any)=>(<li key={b.id}>{b.title} ({b.count})</li>))}
                </ul>
              </div>
            </div>
          )}
          <hr />
          <h3>Tags</h3>
          <div style={{ display:'flex', gap:8 }}>
            <input placeholder="new tag" value={newTag} onChange={e=>setNewTag(e.target.value)} />
            <button onClick={onCreateTag}>Add Tag</button>
          </div>
          <ul>
            {tags.map((t:any)=>(<li key={t.id}>{t.name} {t.color?`(${t.color})`:''} — {t.count}</li>))}
          </ul>
          <hr />
          <h3>Folders</h3>
          <div style={{ display:'flex', gap:8 }}>
            <input placeholder="folder name" value={folderName} onChange={e=>setFolderName(e.target.value)} />
            <button onClick={onCreateFolder}>Add Folder</button>
          </div>
          <pre>{JSON.stringify(folders, null, 2)}</pre>
          <hr />
          <h3>Attachments</h3>
          <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
          <button onClick={onUpload}>Upload</button>
          {attachmentId && (
            <div>
              Uploaded attachment: {attachmentId}
              <button style={{ marginLeft: 8 }} onClick={async ()=>{
                if (!token || !attachmentId) return
                const r = await fetch(`/attachments/${attachmentId}/download`, { headers: { Authorization: `Bearer ${token}` }})
                const blob = await r.blob()
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url; a.download = 'download'
                document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
              }}>Download</button>
            </div>
          )}
          <hr />
          <h3>Search</h3>
          <div style={{ display:'flex', gap:8 }}>
            <input placeholder="query" value={query} onChange={e=>setQuery(e.target.value)} />
            <button onClick={onSearch}>Search</button>
          </div>
          <ul>
            {results.map((r:any)=>(<li key={r.id || r.path}><strong>{r.title || r.path}</strong> <span dangerouslySetInnerHTML={{__html:r.snippet||''}} /></li>))}
          </ul>
          <hr />
          <h3>Graph</h3>
          <button onClick={loadGraph}>Load Graph</button>
          <GraphView data={graph} selectedId={selectedNodeId} onSelect={onSelectNode} />
          <hr />
          <h3>Repos</h3>
          <div style={{ display:'flex', gap:8 }}>
            <input placeholder="repo name" value={repoName} onChange={e=>setRepoName(e.target.value)} />
            <button onClick={onCreateRepo}>Create Repo</button>
          </div>
          <div style={{ display:'flex', gap:8, marginTop: 8 }}>
            <select onChange={e=>selectRepo(e.target.value)} value={currentRepo || ''}>
              <option value="">Select repo…</option>
              {repos.map((r:any)=>(<option key={r.id} value={r.id}>{r.name}</option>))}
            </select>
            <button onClick={()=> currentRepo && selectRepo(currentRepo)}>Refresh</button>
          </div>
          {currentRepo && (
            <div>
              <div style={{ display:'flex', gap:8, marginTop:8 }}>
                <input placeholder="path" value={filePath} onChange={e=>setFilePath(e.target.value)} />
                <button onClick={loadFile}>Load</button>
                <button onClick={saveFile}>Save (single)</button>
                <button onClick={makeMultiCommit}>Commit (multi)</button>
              </div>
              <textarea style={{ width:'100%', height:200, marginTop:8 }} value={fileContent} onChange={e=>setFileContent(e.target.value)} />
              <div style={{ display:'flex', gap:8, marginTop:8 }}>
                <input placeholder="search in repo" value={query} onChange={e=>setQuery(e.target.value)} />
                <button onClick={async ()=>{
                  if (!token || !currentRepo || !query.trim()) return
                  const r = await fetch(`/repos/${currentRepo}/search?q=${encodeURIComponent(query)}`, { headers: { Authorization: `Bearer ${token}` }})
                  setResults(await r.json())
                }}>Search</button>
              </div>
              <ul>
                {results.map((r:any)=>(<li key={r.path}><strong>{r.path}</strong> <em>{r.language}</em><pre style={{whiteSpace:'pre-wrap'}}>{r.snippet}</pre></li>))}
              </ul>
              <div style={{ display:'flex', gap:8, marginTop:8 }}>
                <select value={commitA} onChange={e=>setCommitA(e.target.value)}>
                  <option value="">Commit A</option>
                  {commits.map((c:any)=>(<option key={c.id} value={c.id}>{c.id.slice(0,8)} {c.message}</option>))}
                </select>
                <select value={commitB} onChange={e=>setCommitB(e.target.value)}>
                  <option value="">Commit B</option>
                  {commits.map((c:any)=>(<option key={c.id} value={c.id}>{c.id.slice(0,8)} {c.message}</option>))}
                </select>
                <button onClick={loadDiff}>Diff</button>
              </div>
              <pre>{diff.join('\n')}</pre>
              <h4>Files</h4>
              <ul>
                {files.map((f:any)=>(<li key={f.id}>{f.path}</li>))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Editor({ value, onChange }: { value: string; onChange: (v:string)=>void }) {
  const [local, setLocal] = useState(value)
  useEffect(()=>{ setLocal(value) }, [value])
  const apply = () => onChange(local)
  const renderMarkdown = (md: string) => {
    let html = md
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    html = html.replace(/^###\s(.+)$/gm,'<h3>$1</h3>')
      .replace(/^##\s(.+)$/gm,'<h2>$1</h2>')
      .replace(/^#\s(.+)$/gm,'<h1>$1</h1>')
      .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
      .replace(/\*(.+?)\*/g,'<em>$1</em>')
      .replace(/`{3}([\s\S]*?)`{3}/g,'<pre><code>$1</code></pre>')
      .replace(/`([^`]+)`/g,'<code>$1</code>')
      .replace(/\n\n/g,'<br/><br/>')
    return { __html: html }
  }
  return (
    <div>
      <div style={{ display:'flex', gap:8, marginBottom:8 }}>
        <button onClick={()=>setLocal(l=>`# ${l}`)}>H1</button>
        <button onClick={()=>setLocal(l=>`## ${l}`)}>H2</button>
        <button onClick={()=>setLocal(l=>`### ${l}`)}>H3</button>
        <button onClick={()=>setLocal(l=>`**${l}**`)}>Bold</button>
        <button onClick={()=>setLocal(l=>`*${l}*`)}>Italic</button>
        <button onClick={()=>setLocal(l=>`${l}\n\n
\
\
`)}>Code</button>
        <button onClick={apply}>Apply</button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8 }}>
        <textarea style={{ width:'100%', height:200 }} value={local} onChange={e=>setLocal(e.target.value)} />
        <div style={{ border:'1px solid #eee', padding:8 }} dangerouslySetInnerHTML={renderMarkdown(local)} />
      </div>
    </div>
  )
}

function GraphView({ data, selectedId, onSelect }: { data: { nodes:any[]; edges:any[] }, selectedId?: string | null, onSelect?: (id:string)=>void }) {
  const size = 400
  const radius = 160
  const cx = size/2, cy = size/2
  const nodes = data.nodes || []
  const edges = data.edges || []
  // Position nodes: selected in center, others in circle
  let positioned: any[] = []
  const others = nodes.filter((n:any)=> n.id !== selectedId)
  if (selectedId && nodes.find((n:any)=>n.id===selectedId)) {
    const sel = nodes.find((n:any)=>n.id===selectedId)
    positioned.push({ id: selectedId, label: sel?.label, x: cx, y: cy, selected: true })
    const count = Math.max(1, others.length)
    for (let i=0;i<others.length;i++) {
      const angle = (2*Math.PI*i)/count
      positioned.push({ id: others[i].id, label: others[i].label, x: cx + radius*Math.cos(angle), y: cy + radius*Math.sin(angle) })
    }
  } else {
    positioned = nodes.map((n:any, i:number) => {
      const angle = (2*Math.PI*i)/Math.max(1,nodes.length)
      return { id: n.id, label: n.label, x: cx + radius*Math.cos(angle), y: cy + radius*Math.sin(angle) }
    })
  }
  const posMap = Object.fromEntries(positioned.map(p=>[p.id,p]))
  return (
    <svg width={size} height={size} style={{ border:'1px solid #eee', marginTop:8 }}>
      {edges.map((e:any,i:number)=>{
        const s = posMap[e.source], t = posMap[e.target]
        if (!s || !t) return null
        return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#aaa" />
      })}
      {positioned.map((p:any)=> (
        <g key={p.id}>
          <circle onClick={()=> onSelect && onSelect(p.id)} cx={p.x} cy={p.y} r={p.selected?14:12} fill={p.selected?"#16a34a":"#4f46e5"} style={{ cursor:'pointer' }} />
          <text x={p.x+14} y={p.y+4} fontSize={12}>{p.label}</text>
        </g>
      ))}
    </svg>
  )
}
