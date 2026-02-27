import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom';
import API from './services/api';
import './App.css';

// ─── Auth Context ────────────────────────────────────────────────────────────
const AuthContext = createContext(null);
const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem('ums_user');
    return u ? JSON.parse(u) : null;
  });

  const login = (token, userData) => {
    localStorage.setItem('ums_token', token);
    localStorage.setItem('ums_user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('ums_token');
    localStorage.removeItem('ums_user');
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

// ─── Private Route ───────────────────────────────────────────────────────────
function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

// ─── Login Page ──────────────────────────────────────────────────────────────
function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await API.post('/auth/login', form);
      login(res.data.token, res.data.user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="login-brand">
          <div className="brand-icon">⬡</div>
          <h1>NEXUS<span>UMS</span></h1>
          <p>University Management System</p>
        </div>
        <div className="login-stats">
          <div className="stat-pill">🎓 5000+ Students</div>
          <div className="stat-pill">📚 200+ Courses</div>
          <div className="stat-pill">🏛️ 12 Departments</div>
        </div>
      </div>
      <div className="login-right">
        <div className="login-card">
          <h2>Welcome back</h2>
          <p className="login-sub">Sign in to your account</p>
          {error && <div className="error-msg">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="field-group">
              <label>Email Address</label>
              <input type="email" placeholder="admin@university.edu" value={form.email}
                onChange={e => setForm({...form, email: e.target.value})} required />
            </div>
            <div className="field-group">
              <label>Password</label>
              <input type="password" placeholder="••••••••" value={form.password}
                onChange={e => setForm({...form, password: e.target.value})} required />
            </div>
            <button type="submit" className="btn-login" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Sign In →'}
            </button>
          </form>
          <div className="demo-creds">
            <p>Demo credentials:</p>
            <code>admin@university.edu / Admin@123</code>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Sidebar Nav ─────────────────────────────────────────────────────────────
const navItems = [
  { path: '/dashboard', icon: '◈', label: 'Dashboard' },
  { path: '/students', icon: '⊡', label: 'Students' },
  { path: '/faculty', icon: '⊞', label: 'Faculty' },
  { path: '/courses', icon: '◉', label: 'Courses' },
  { path: '/departments', icon: '⬡', label: 'Departments' },
  { path: '/attendance', icon: '◷', label: 'Attendance' },
  { path: '/grades', icon: '◈', label: 'Grades' },
  { path: '/fees', icon: '◎', label: 'Fees' },
  { path: '/notices', icon: '◫', label: 'Notices' },
];

function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className={`app-layout ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand">
            <span className="brand-mark">⬡</span>
            {sidebarOpen && <span className="brand-text">NEXUS<em>UMS</em></span>}
          </div>
          <button className="toggle-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? '‹' : '›'}
          </button>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(item => (
            <Link key={item.path} to={item.path}
              className={`nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}>
              <span className="nav-icon">{item.icon}</span>
              {sidebarOpen && <span className="nav-label">{item.label}</span>}
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user?.name?.[0]?.toUpperCase()}</div>
            {sidebarOpen && (
              <div>
                <div className="user-name">{user?.name}</div>
                <div className="user-role">{user?.role}</div>
              </div>
            )}
          </div>
          {sidebarOpen && <button className="logout-btn" onClick={handleLogout}>↩</button>}
        </div>
      </aside>
      <main className="main-content">
        <header className="top-bar">
          <div className="page-title">{navItems.find(n => location.pathname.startsWith(n.path))?.label || 'Dashboard'}</div>
          <div className="top-bar-right">
            <div className="notif-bell">🔔</div>
            <button className="btn-logout-top" onClick={handleLogout}>Logout</button>
          </div>
        </header>
        <div className="page-content">{children}</div>
      </main>
    </div>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────
function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/dashboard/stats').then(r => { setStats(r.data.data); setLoading(false); })
      .catch(() => {
        // Demo data when backend is not available
        setStats({
          overview: { totalStudents: 1243, totalFaculty: 89, totalCourses: 156, totalDepts: 12, pendingFees: 234, activeEnrollments: 3847 },
          deptStats: [
            { name: 'Computer Science', code: 'CS', count: 342 },
            { name: 'Electronics', code: 'ECE', count: 287 },
            { name: 'Mechanical', code: 'ME', count: 265 },
            { name: 'Mathematics', code: 'MATH', count: 156 },
            { name: 'Physics', code: 'PHY', count: 193 }
          ],
          recentNotices: [
            { _id: '1', title: 'Semester Examination Schedule', type: 'exam', createdAt: new Date().toISOString(), postedBy: { name: 'Admin' } },
            { _id: '2', title: 'Annual Technical Symposium', type: 'academic', createdAt: new Date().toISOString(), postedBy: { name: 'Admin' } },
            { _id: '3', title: 'Fee Payment Deadline', type: 'urgent', createdAt: new Date().toISOString(), postedBy: { name: 'Admin' } },
          ]
        });
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-screen"><div className="loader" /></div>;

  const { overview, deptStats, recentNotices } = stats;
  const cards = [
    { label: 'Total Students', value: overview.totalStudents.toLocaleString(), icon: '🎓', color: '#6C63FF', change: '+12%' },
    { label: 'Faculty Members', value: overview.totalFaculty, icon: '👨‍🏫', color: '#FF6584', change: '+3%' },
    { label: 'Active Courses', value: overview.totalCourses, icon: '📚', color: '#43B89C', change: '+8%' },
    { label: 'Departments', value: overview.totalDepts, icon: '🏛️', color: '#F7B731', change: '0%' },
    { label: 'Enrollments', value: overview.activeEnrollments.toLocaleString(), icon: '📋', color: '#20BF6B', change: '+5%' },
    { label: 'Pending Fees', value: overview.pendingFees, icon: '💰', color: '#FC5C65', change: '-2%' },
  ];

  return (
    <div className="dashboard">
      <div className="stats-grid">
        {cards.map((c, i) => (
          <div className="stat-card" key={i} style={{'--accent': c.color}}>
            <div className="stat-icon">{c.icon}</div>
            <div className="stat-value">{c.value}</div>
            <div className="stat-label">{c.label}</div>
            <div className={`stat-change ${c.change.startsWith('+') ? 'pos' : c.change.startsWith('-') ? 'neg' : ''}`}>{c.change}</div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="card dept-chart">
          <h3 className="card-title">Students by Department</h3>
          <div className="bar-chart">
            {deptStats.map((d, i) => {
              const max = Math.max(...deptStats.map(x => x.count));
              const pct = (d.count / max * 100).toFixed(0);
              return (
                <div className="bar-row" key={i}>
                  <span className="bar-label">{d.code}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${pct}%`, '--delay': `${i * 0.1}s` }} />
                  </div>
                  <span className="bar-val">{d.count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card notices-panel">
          <h3 className="card-title">Recent Notices</h3>
          <div className="notice-list">
            {recentNotices.map(n => (
              <div className="notice-item" key={n._id}>
                <span className={`notice-badge ${n.type}`}>{n.type}</span>
                <div>
                  <div className="notice-title">{n.title}</div>
                  <div className="notice-meta">{n.postedBy?.name} · {new Date(n.createdAt).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card quick-actions">
          <h3 className="card-title">Quick Actions</h3>
          <div className="action-grid">
            {[
              { icon: '➕', label: 'Add Student', path: '/students' },
              { icon: '📝', label: 'Post Notice', path: '/notices' },
              { icon: '📊', label: 'Record Grades', path: '/grades' },
              { icon: '💳', label: 'Manage Fees', path: '/fees' },
            ].map((a, i) => (
              <Link key={i} to={a.path} className="action-btn">{a.icon} {a.label}</Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Generic Entity Page (Students, Faculty, etc.) ────────────────────────────
function EntityPage({ title, endpoint, columns, renderRow, canAdd = true }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await API.get(`${endpoint}?page=${page}&limit=10${search ? `&search=${search}` : ''}`);
      setData(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch { setData([]); }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [page, search, endpoint]);

  return (
    <div className="entity-page">
      <div className="entity-header">
        <div className="entity-search">
          <input placeholder={`Search ${title.toLowerCase()}...`} value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }} />
        </div>
        {canAdd && <button className="btn-primary">+ Add {title.slice(0,-1)}</button>}
      </div>
      <div className="card table-card">
        {loading ? <div className="table-loading"><div className="loader" /></div> : (
          <>
            <table className="data-table">
              <thead><tr>{columns.map((c,i) => <th key={i}>{c}</th>)}</tr></thead>
              <tbody>{data.length > 0 ? data.map(renderRow) : (
                <tr><td colSpan={columns.length} className="empty-row">No records found</td></tr>
              )}</tbody>
            </table>
            <div className="pagination">
              <span className="pagination-info">Showing {data.length} of {total} records</span>
              <div className="pagination-btns">
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>‹</button>
                <span>{page}</span>
                <button disabled={page * 10 >= total} onClick={() => setPage(p => p + 1)}>›</button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function StudentsPage() {
  return (
    <EntityPage title="Students" endpoint="/students"
      columns={['ID', 'Name', 'Email', 'Department', 'Semester', 'Program', 'CGPA', 'Status', 'Actions']}
      renderRow={s => (
        <tr key={s._id}>
          <td><code>{s.studentId}</code></td>
          <td><div className="name-cell"><div className="avatar-sm">{s.user?.name?.[0]}</div>{s.user?.name}</div></td>
          <td className="muted">{s.user?.email}</td>
          <td>{s.department?.code}</td>
          <td>Sem {s.semester}</td>
          <td>{s.program}</td>
          <td><span className="cgpa">{s.cgpa?.toFixed(1)}</span></td>
          <td><span className={`status-badge ${s.status}`}>{s.status}</span></td>
          <td><button className="btn-icon">✏️</button></td>
        </tr>
      )}
    />
  );
}

function FacultyPage() {
  return (
    <EntityPage title="Faculty" endpoint="/faculty"
      columns={['ID', 'Name', 'Department', 'Designation', 'Experience', 'Status', 'Actions']}
      renderRow={f => (
        <tr key={f._id}>
          <td><code>{f.facultyId}</code></td>
          <td><div className="name-cell"><div className="avatar-sm faculty">{f.user?.name?.[0]}</div>{f.user?.name}</div></td>
          <td>{f.department?.code}</td>
          <td>{f.designation}</td>
          <td>{f.experience} yrs</td>
          <td><span className={`status-badge ${f.status}`}>{f.status}</span></td>
          <td><button className="btn-icon">✏️</button></td>
        </tr>
      )}
    />
  );
}

function CoursesPage() {
  return (
    <EntityPage title="Courses" endpoint="/courses"
      columns={['Code', 'Title', 'Department', 'Faculty', 'Credits', 'Type', 'Semester', 'Actions']}
      renderRow={c => (
        <tr key={c._id}>
          <td><code>{c.code}</code></td>
          <td>{c.title}</td>
          <td>{c.department?.code}</td>
          <td>{c.faculty?.user?.name || '—'}</td>
          <td>{c.credits}</td>
          <td><span className={`type-badge ${c.type}`}>{c.type}</span></td>
          <td>{c.semester}</td>
          <td><button className="btn-icon">✏️</button></td>
        </tr>
      )}
    />
  );
}

function DepartmentsPage() {
  return (
    <EntityPage title="Departments" endpoint="/departments"
      columns={['Code', 'Name', 'Head', 'Programs', 'Seats', 'Status', 'Actions']}
      renderRow={d => (
        <tr key={d._id}>
          <td><code className="dept-code">{d.code}</code></td>
          <td>{d.name}</td>
          <td>{d.head?.user?.name || '—'}</td>
          <td><div className="tag-list">{d.programs?.map((p,i) => <span key={i} className="tag">{p}</span>)}</div></td>
          <td>{d.totalSeats}</td>
          <td><span className={`status-badge ${d.isActive ? 'active' : 'inactive'}`}>{d.isActive ? 'active' : 'inactive'}</span></td>
          <td><button className="btn-icon">✏️</button></td>
        </tr>
      )}
    />
  );
}

function GenericPage({ title }) {
  return (
    <div className="coming-soon">
      <div className="cs-icon">🚧</div>
      <h2>{title}</h2>
      <p>This module is fully implemented in the backend API. Connect your frontend components here!</p>
      <div className="api-hint">
        <code>GET /api/{title.toLowerCase()}</code>
      </div>
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<PrivateRoute><Layout><DashboardPage /></Layout></PrivateRoute>} />
          <Route path="/students" element={<PrivateRoute><Layout><StudentsPage /></Layout></PrivateRoute>} />
          <Route path="/faculty" element={<PrivateRoute><Layout><FacultyPage /></Layout></PrivateRoute>} />
          <Route path="/courses" element={<PrivateRoute><Layout><CoursesPage /></Layout></PrivateRoute>} />
          <Route path="/departments" element={<PrivateRoute><Layout><DepartmentsPage /></Layout></PrivateRoute>} />
          <Route path="/attendance" element={<PrivateRoute><Layout><GenericPage title="Attendance" /></Layout></PrivateRoute>} />
          <Route path="/grades" element={<PrivateRoute><Layout><GenericPage title="Grades" /></Layout></PrivateRoute>} />
          <Route path="/fees" element={<PrivateRoute><Layout><GenericPage title="Fees" /></Layout></PrivateRoute>} />
          <Route path="/notices" element={<PrivateRoute><Layout><GenericPage title="Notices" /></Layout></PrivateRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
