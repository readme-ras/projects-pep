import { useState } from 'react'

const CAT_COLORS = {
  general:  { bg: '#f1f1f1', text: '#555' },
  work:     { bg: '#e8f0fe', text: '#1a56db' },
  personal: { bg: '#fce8e6', text: '#c0392b' },
  shopping: { bg: '#e6f4ea', text: '#2e7d32' },
  health:   { bg: '#fff3e0', text: '#e65100' },
  finance:  { bg: '#f3e5f5', text: '#6a1b9a' },
}

export default function ItemCard({ item, onEdit, onDelete, onToggle }) {
  const [deleting, setDeleting] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const cat = CAT_COLORS[item.category] || CAT_COLORS.general

  async function handleDelete() {
    if (!confirming) return setConfirming(true)
    setDeleting(true)
    await onDelete(item.id)
  }

  const date = new Date(item.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })

  return (
    <div style={{
      background: 'var(--paper)',
      border: '1px solid var(--border)',
      borderLeft: `3px solid ${item.completed ? 'var(--sage)' : 'var(--rust)'}`,
      borderRadius: 2,
      padding: '18px 20px',
      display: 'flex',
      gap: 14,
      alignItems: 'flex-start',
      transition: 'box-shadow 0.2s, transform 0.2s',
      animation: 'fadeUp 0.3s ease',
      opacity: item.completed ? 0.65 : 1,
    }}
    onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 4px 20px rgba(28,28,30,0.08)'; e.currentTarget.style.transform = 'translateY(-1px)' }}
    onMouseLeave={e => { e.currentTarget.style.boxShadow = ''; e.currentTarget.style.transform = '' }}
    >
      {/* Checkbox */}
      <button
        onClick={() => onToggle(item.id, !item.completed)}
        style={{
          width: 20, height: 20, borderRadius: '50%', flexShrink: 0, marginTop: 2,
          border: `2px solid ${item.completed ? 'var(--sage)' : 'var(--border2)'}`,
          background: item.completed ? 'var(--sage)' : 'transparent',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.2s', cursor: 'pointer',
        }}
      >
        {item.completed && <span style={{ color: 'white', fontSize: 11, lineHeight: 1 }}>✓</span>}
      </button>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
          <span style={{
            fontSize: 15, fontWeight: 500, color: 'var(--charcoal)',
            textDecoration: item.completed ? 'line-through' : 'none',
          }}>
            {item.title}
          </span>
          <span style={{
            padding: '2px 8px', borderRadius: 20, fontSize: 10,
            fontWeight: 500, letterSpacing: '0.06em', textTransform: 'uppercase',
            background: cat.bg, color: cat.text,
          }}>
            {item.category}
          </span>
        </div>
        {item.description && (
          <p style={{ fontSize: 13, color: 'var(--muted)', lineHeight: 1.5, marginBottom: 6 }}>
            {item.description}
          </p>
        )}
        <span style={{ fontSize: 11, color: 'var(--border2)' }}>{date}</span>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
        <button onClick={() => onEdit(item)} style={{
          padding: '5px 12px', border: '1px solid var(--border2)', borderRadius: 2,
          background: 'none', fontSize: 12, color: 'var(--muted)',
          transition: 'all 0.15s',
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--charcoal)'; e.currentTarget.style.color = 'var(--charcoal)' }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--muted)' }}
        >
          Edit
        </button>
        <button onClick={handleDelete} disabled={deleting} style={{
          padding: '5px 12px', border: '1px solid transparent', borderRadius: 2,
          background: confirming ? 'var(--rust)' : 'none',
          color: confirming ? 'white' : 'var(--muted)',
          fontSize: 12, transition: 'all 0.15s',
        }}
        onMouseEnter={e => !confirming && (e.currentTarget.style.color = 'var(--rust)')}
        onMouseLeave={e => { if (!confirming) { e.currentTarget.style.color = 'var(--muted)'; setConfirming(false) } }}
        >
          {deleting ? '…' : confirming ? 'Confirm' : 'Delete'}
        </button>
      </div>
    </div>
  )
}
