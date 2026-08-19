import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">NormaExtractor</div>
        <nav className="sidebar-nav">
          <NavLink to="/upload">Upload</NavLink>
          <NavLink to="/documents" end>
            Documentos
          </NavLink>
          <NavLink to="/chat">Chat</NavLink>
        </nav>
        <button type="button" className="btn btn-logout" onClick={handleLogout}>
          Sair
        </button>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
