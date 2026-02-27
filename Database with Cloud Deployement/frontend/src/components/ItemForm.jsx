import { useState, useEffect } from 'react'

const CATEGORIES = ['general', 'work', 'personal', 'shopping', 'health', 'finance']

const styles = {
  overlay: {
    position: 'fixed', inset: 0, background: 'rgba(28,28,30,0.55)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    zIndex: 100, animation: 'fadeIn 0.2s ease',
    backdropFilter: 'blur(4px)',
  },
  modal: {
    background: 'var(--paper)', width: '100%', maxWidth: 520,
    margin: '0 16px', borderRadius: 2, border: '1px solid var(--border)',
    boxShadow: '0 32px 80px rgba(28,28,30,0.18)',
    animation: 'slideIn 0.25s ease',
  },
  header: {
    padding: '28px 32px 20px',
    borderBottom: '1px solid var(--border)',
    display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
  },
  title: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 22, fontWeight: 700, color: 'var(--charcoal)',
  },
  closeBtn: {
    background: 'none', border: 'none', fontSize: 20, color: 'var(--muted)',
    lineHeight: 1, padding: '4px 8px', borderRadius: 4,
    transition: 'color 0.15s',
  },
  body: { padding: '24px 32px' },
  field: { marginBottom: 18 },
  label: {
    display: 'block', fontSize: 11, fontWeight: 500, letterSpacing: '0.1em',
    textTransform: 'uppercase', color: 'var(--muted)', marginBottom: 7,
  },
  input: {
    width: '100%', padding: '10px 14px',
    border: '1px solid var(--border2)', borderRadius: 2,
    fontSize: 14, color: 'var(--ink)', background: 'var(--paper)',
    outline: 'none', transition: 'border-color 0.2s',
  },
  textarea: {
    width: '100%', padding: '10px 14px',
    border: '1px solid var(--border2)', borderRadius: 2,
    fontSize: 14, color: 'var(--ink)', background: 'var(--paper)',
    outline: 'none', resize: 'vertical', minHeight: 80,
    transition: 'border-color 0.2s',
  },
  select: {
    width: '100%', padding: '10px 14px',
    border: '1px solid var(--border2)', borderRadius: 2,
    fontSize: 14, color: 'var(--ink)', background: 'var(--paper)',
    outline: 'none', appearance: 'none',
    backgroundImage: 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'8\' viewBox=\'0 0 12 8\'%3E%3Cpath d=\'M1 1l5 5 5-5\' stroke=\'%238a8a8e\' fill=\'none\' stroke-width=\'1.5\'/%3E%3C/svg%3E")',
    backgroundRepeat: 'no-repeat', backgroundPosition: 'right 14px center',
  },
  footer: {
    padding: '16px 32px 28px',
    display: 'flex', justifyContent: 'flex-end', gap: 10,
  },
  cancelBtn: {
    padding: '9px 20px', border: '1px solid var(--border2)', borderRadius: 2,
    background: 'none', fontSize: 14, color: 'var(--muted)', transition: 'all 0.15s',
  },
  submitBtn: {
    padding: '9px 24px', border: 'none', borderRadius: 2,
    background: 'var(--rust)', color: 'white',
    fontSize: 14, fontWeight: 500, transition: 'background 0.15s',
  },
}

export default function ItemForm({ item, onSave, onClose }) {
  const [form, setForm] = useState({
    title: '', description: '', category: 'general', completed: false,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    if (item) setForm({
      title:       item.title,
      description: item.description,
      category:    item.category,
      completed:   item.completed,
    })
  }, [item])

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.title.trim()) return setErr('Title is required.')
    setSaving(true); setErr('')
    try {
      await onSave(form)
      onClose()
    } catch (ex) {
      setErr(ex.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={styles.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <span style={styles.title}>{item ? 'Edit Item' : 'New Item'}</span>
          <button style={styles.closeBtn} onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={styles.body}>
            {err && (
              <div style={{ padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 2, marginBottom: 16, fontSize: 13, color: 'var(--rust)' }}>
                {err}
              </div>
            )}
            <div style={styles.field}>
              <label style={styles.label}>Title *</label>
              <input
                style={styles.input} value={form.title} onChange={set('title')}
                placeholder="What needs to be done?" autoFocus
                onFocus={e => e.target.style.borderColor = 'var(--rust)'}
                onBlur={e => e.target.style.borderColor = 'var(--border2)'}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Description</label>
              <textarea
                style={styles.textarea} value={form.description} onChange={set('description')}
                placeholder="Optional details..."
                onFocus={e => e.target.style.borderColor = 'var(--rust)'}
                onBlur={e => e.target.style.borderColor = 'var(--border2)'}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Category</label>
              <select style={styles.select} value={form.category} onChange={set('category')}>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>
          <div style={styles.footer}>
            <button type="button" style={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button type="submit" style={styles.submitBtn} disabled={saving}>
              {saving ? 'Saving…' : item ? 'Save Changes' : 'Create Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
