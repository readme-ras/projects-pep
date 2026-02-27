import { useState, useEffect, useCallback } from 'react'
import { api } from './api.js'

const S = {
  app: { maxWidth: 860, margin: '0 auto', padding: '0 24px 60px', minHeight: '100vh' },
  header: { padding: '40px 0 32px', borderBottom: '2px solid var(--ink)', marginBottom: 36, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' },
  logo: { fontSize: 38, fontWeight: 800, letterSpacing: '-0.02em', lineHeight: 1, color: 'var(--ink)' },
  logoSub: { fontFamily: "'DM Mono', monospace", fontSize: 11, fontWeight: 300, color: 'var(--ink3)', letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: 6 },
  statsRow: { display: 'flex', gap: 24, fontFamily: "'DM Mono', monospace", fontSize: 12, color: 'var(--ink3)', textAlign: 'right' },
  statItem: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2 },
  statVal: { fontSize: 22, fontWeight: 600, color: 'var(--ink)', lineHeight: 1 },
  toolbar: { display: 'flex', gap: 12, marginBottom: 28, flexWrap: 'wrap', alignItems: 'center' },
  filterBtn: (active) => ({ padding: '6px 14px', borderRadius: 40, border: active ? '1.5px solid var(--ink)' : '1.5px solid var(--border)', background: active ? 'var(--ink)' : 'transparent', color: active ? 'var(--cream)' : 'var(--ink2)', fontFamily: "'DM Mono', monospace", fontSize: 11, letterSpacing: '0.06em', cursor: 'pointer' }),
  addBtn: { marginLeft: 'auto', padding: '10px 22px', background: 'var(--gold)', color: '#fff', border: 'none', borderRadius: 6, fontSize: 14, fontWeight: 600, boxShadow: '0 2px 8px rgba(201,146,42,0.25)' },
  card: (done) => ({ background: done ? 'var(--parchment)' : '#fff', border: '1px solid var(--border)', borderRadius: 10, padding: '20px 22px', marginBottom: 12, display: 'flex', gap: 16, alignItems: 'flex-start', boxShadow: 'var(--shadow)', opacity: done ? 0.65 : 1, transition: 'all 0.15s' }),
  checkbox: { width: 20, height: 20, borderRadius: 4, border: '2px solid var(--border)', flexShrink: 0, marginTop: 3, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.15s' },
  checkDone: { background: 'var(--sage)', borderColor: 'var(--sage)' },
  cardBody: { flex: 1, minWidth: 0 },
  cardTitle: (done) => ({ fontSize: 17, fontWeight: 600, color: 'var(--ink)', textDecoration: done ? 'line-through' : 'none', marginBottom: 4 }),
  cardDesc: { fontSize: 14, color: 'var(--ink2)', marginBottom: 10, fontStyle: 'italic', fontWeight: 300 },
  cardMeta: { display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' },
  tag: { padding: '2px 8px', borderRadius: 40, background: 'var(--gold-bg)', border: '1px solid rgba(201,146,42,0.2)', fontFamily: "'DM Mono', monospace", fontSize: 10, color: 'var(--gold2)' },
  prio: (p) => ({ padding: '2px 8px', borderRadius: 40, fontFamily: "'DM Mono', monospace", fontSize: 10, background: p==='high'?'rgba(201,74,42,0.08)':p==='medium'?'rgba(201,146,42,0.08)':'rgba(74,127,90,0.08)', color: p==='high'?'var(--rust)':p==='medium'?'var(--gold)':'var(--sage)', border: `1px solid ${p==='high'?'rgba(201,74,42,0.2)':p==='medium'?'rgba(201,146,42,0.2)':'rgba(74,127,90,0.2)'}` }),
  date: { fontFamily: "'DM Mono', monospace", fontSize: 10, color: 'var(--ink3)' },
  actions: { display: 'flex', gap: 6, flexShrink: 0 },
  iconBtn: { background: 'none', border: 'none', padding: '4px 6px', borderRadius: 4, color: 'var(--ink3)', fontSize: 14, cursor: 'pointer' },
  overlay: { position: 'fixed', inset: 0, background: 'rgba(26,18,8,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 24, backdropFilter: 'blur(4px)' },
  modal: { background: 'var(--cream)', borderRadius: 14, padding: '36px 32px', width: '100%', maxWidth: 480, boxShadow: '0 24px 60px rgba(26,18,8,0.2)', border: '1px solid var(--border)' },
  modalTitle: { fontSize: 24, fontWeight: 800, marginBottom: 24 },
  field: { marginBottom: 18 },
  label: { display: 'block', fontFamily: "'DM Mono', monospace", fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--ink3)', marginBottom: 6 },
  input: { width: '100%', padding: '10px 13px', border: '1.5px solid var(--border)', borderRadius: 7, background: '#fff', fontSize: 15, color: 'var(--ink)', outline: 'none' },
  select: { width: '100%', padding: '10px 13px', border: '1.5px solid var(--border)', borderRadius: 7, background: '#fff', fontSize: 14, color: 'var(--ink)', outline: 'none' },
  modalBtns: { display: 'flex', gap: 10, marginTop: 28, justifyContent: 'flex-end' },
  cancelBtn: { padding: '10px 20px', border: '1.5px solid var(--border)', borderRadius: 7, background: 'transparent', color: 'var(--ink2)', fontSize: 14, cursor: 'pointer' },
  saveBtn: { padding: '10px 24px', background: 'var(--gold)', border: 'none', borderRadius: 7, color: '#fff', fontSize: 14, fontWeight: 600, cursor: 'pointer' },
  empty: { textAlign: 'center', padding: '60px 0', color: 'var(--ink3)', fontStyle: 'italic', fontWeight: 300, fontSize: 18 },
  error: { padding: '12px 16px', background: 'rgba(201,74,42,0.08)', border: '1px solid rgba(201,74,42,0.2)', borderRadius: 7, color: 'var(--rust)', fontFamily: "'DM Mono', monospace", fontSize: 12, marginBottom: 20 },
}

const PRIORITIES = ['low', 'medium', 'high']
const FILTERS = [
  { label: 'All', value: null },
  { label: 'Pending', value: 'pending' },
  { label: 'Done', value: 'done' },
  { label: '🔴 High', value: 'high' },
  { label: '🟡 Medium', value: 'medium' },
  { label: '🟢 Low', value: 'low' },
]
const emptyForm = { title: '', description: '', priority: 'medium', due_date: '', tags: '' }

function TaskCard({ task, onToggle, onEdit, onDelete }) {
  return (
    <div style={S.card(task.completed)}>
      <div style={{ ...S.checkbox, ...(task.completed ? S.checkDone : {}) }} onClick={() => onToggle(task.id)}>
        {task.completed && <span style={{ color: '#fff', fontSize: 12 }}>✓</span>}
      </div>
      <div style={S.cardBody}>
        <div style={S.cardTitle(task.completed)}>{task.title}</div>
        {task.description && <div style={S.cardDesc}>{task.description}</div>}
        <div style={S.cardMeta}>
          <span style={S.prio(task.priority)}>{task.priority}</span>
          {task.tags.map(t => <span key={t} style={S.tag}>{t}</span>)}
          {task.due_date && <span style={S.date}>📅 {task.due_date}</span>}
          <span style={{ ...S.date, marginLeft: 'auto' }}>{new Date(task.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      <div style={S.actions}>
        <button style={S.iconBtn} onClick={() => onEdit(task)}>✎</button>
        <button style={S.iconBtn} onClick={() => onDelete(task.id)}>✕</button>
      </div>
    </div>
  )
}

function TaskModal({ task, onClose, onSave }) {
  const [form, setForm] = useState(task ? { ...task, tags: task.tags.join(', ') } : emptyForm)
  const [saving, setSaving] = useState(false)
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    if (!form.title.trim()) return
    setSaving(true)
    const payload = { title: form.title.trim(), description: form.description.trim(), priority: form.priority, due_date: form.due_date || null, tags: form.tags.split(',').map(t => t.trim()).filter(Boolean) }
    try { task ? await onSave(task.id, payload) : await onSave(payload); onClose() }
    finally { setSaving(false) }
  }

  return (
    <div style={S.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={S.modal}>
        <div style={S.modalTitle}>{task ? 'Edit Task' : 'New Task'}</div>
        <form onSubmit={submit}>
          <div style={S.field}><label style={S.label}>Title *</label><input style={S.input} value={form.title} onChange={e => set('title', e.target.value)} placeholder="What needs to be done?" autoFocus required /></div>
          <div style={S.field}><label style={S.label}>Description</label><textarea style={{ ...S.input, minHeight: 80, resize: 'vertical' }} value={form.description} onChange={e => set('description', e.target.value)} placeholder="Additional details..." /></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={S.field}><label style={S.label}>Priority</label><select style={S.select} value={form.priority} onChange={e => set('priority', e.target.value)}>{PRIORITIES.map(p => <option key={p} value={p}>{p[0].toUpperCase() + p.slice(1)}</option>)}</select></div>
            <div style={S.field}><label style={S.label}>Due Date</label><input style={S.input} type="date" value={form.due_date || ''} onChange={e => set('due_date', e.target.value)} /></div>
          </div>
          <div style={S.field}><label style={S.label}>Tags (comma-separated)</label><input style={S.input} value={form.tags} onChange={e => set('tags', e.target.value)} placeholder="design, backend, urgent" /></div>
          <div style={S.modalBtns}>
            <button type="button" style={S.cancelBtn} onClick={onClose}>Cancel</button>
            <button type="submit" style={S.saveBtn} disabled={saving}>{saving ? 'Saving…' : task ? 'Save Changes' : 'Create Task'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function App() {
  const [tasks, setTasks] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState(null)
  const [modal, setModal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const params = {}
      if (filter === 'done') params.completed = true
      if (filter === 'pending') params.completed = false
      if (['low','medium','high'].includes(filter)) params.priority = filter
      const [ts, st] = await Promise.all([api.listTasks(params), api.stats()])
      setTasks(ts); setStats(st)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }, [filter])

  useEffect(() => { load() }, [load])

  return (
    <div style={S.app}>
      <header style={S.header}>
        <div>
          <div style={S.logo}>TaskFlow</div>
          <div style={S.logoSub}>Cloud Run · Firestore · React</div>
        </div>
        {stats && (
          <div style={S.statsRow}>
            <div style={S.statItem}><span style={S.statVal}>{stats.total}</span><span>total</span></div>
            <div style={S.statItem}><span style={{ ...S.statVal, color: 'var(--sage)' }}>{stats.completed}</span><span>done</span></div>
            <div style={S.statItem}><span style={{ ...S.statVal, color: 'var(--rust)' }}>{stats.by_priority?.high || 0}</span><span>urgent</span></div>
          </div>
        )}
      </header>

      {error && <div style={S.error}>⚠ {error} — Is the backend running?</div>}

      <div style={S.toolbar}>
        {FILTERS.map(f => <button key={String(f.value)} style={S.filterBtn(filter === f.value)} onClick={() => setFilter(f.value)}>{f.label}</button>)}
        <button style={S.addBtn} onClick={() => setModal('new')}>+ New Task</button>
      </div>

      {loading ? <div style={S.empty}>Loading…</div> : tasks.length === 0 ? <div style={S.empty}>{filter ? 'No tasks match this filter.' : 'No tasks yet.'}</div> :
        tasks.map(t => <TaskCard key={t.id} task={t} onToggle={async id => { await api.toggleComplete(id); load() }} onEdit={t => setModal(t)} onDelete={async id => { if(confirm('Delete?')) { await api.deleteTask(id); load() } }} />)
      }

      {modal && <TaskModal task={modal === 'new' ? null : modal} onClose={() => setModal(null)} onSave={modal === 'new' ? async p => { await api.createTask(p); load() } : async (id, p) => { await api.updateTask(id, p); load() }} />}
    </div>
  )
}
