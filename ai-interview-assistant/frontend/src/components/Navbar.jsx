function Navbar({ onNavigate, activePage }) {
  const links = [
    { key: 'home', label: 'Home' },
    { key: 'setup', label: 'Interview Setup' },
    { key: 'history', label: 'History' },
    { key: 'dashboard', label: 'Dashboard' },
  ];

  return (
    <nav className="navbar">
      <div className="brand" onClick={() => onNavigate('home')}>
        AI Interview Prep
      </div>
      <div className="nav-links">
        {links.map((link) => (
          <button
            key={link.key}
            className={activePage === link.key ? 'nav-button active' : 'nav-button'}
            onClick={() => onNavigate(link.key)}
          >
            {link.label}
          </button>
        ))}
      </div>
    </nav>
  );
}

export default Navbar;
