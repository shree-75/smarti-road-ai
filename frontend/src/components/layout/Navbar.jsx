import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Shield } from 'lucide-react';
import './Navbar.css';
// Reusable navigation configuration using anchors for single-page design
const NAV_ITEMS = [
  { name: 'Home', path: '/', isHash: false },
  { name: 'Features', path: '/#features', isHash: true, hash: 'features' },
  { name: 'About', path: '/#about', isHash: true, hash: 'about' }
];
const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  // Scroll detection for shrinking header style
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  // Prevent background scrolling when mobile menu is active
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);
  // Automatically close mobile menu on screen resize (>768px)
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setIsOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  // Smooth scroll hash links when location changes (local page clicks or page loads)
  useEffect(() => {
    if (location.hash) {
      const id = location.hash.replace('#', '');
      const element = document.getElementById(id);
      if (element) {
        const timer = setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth' });
        }, 100);
        return () => clearTimeout(timer);
      }
    }
  }, [location.pathname, location.hash]);
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };
  const closeMenu = () => {
    setIsOpen(false);
  };
  const handleNavClick = (e, item) => {
    if (item.isHash) {
      if (location.pathname === '/') {
        e.preventDefault();
        const element = document.getElementById(item.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
        // Update URL hash in the browser bar
        navigate(`/#${item.hash}`, { replace: true });
        closeMenu();
      } else {
        closeMenu();
      }
    } else {
      // Home button logic - scrolls to top if already on Home
      if (location.pathname === '/') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        navigate('/', { replace: true });
      }
      closeMenu();
    }
  };
  const handleLogoClick = (e) => {
    if (location.pathname === '/') {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      navigate('/', { replace: true });
    }
    closeMenu();
  };
  // Determine active status manually based on current hash to avoid double-matching
  const isItemActive = (item) => {
    if (item.isHash) {
      return location.pathname === '/' && location.hash === `#${item.hash}`;
    }
    return location.pathname === '/' && !location.hash;
  };
  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`} role="navigation">
      <div className="navbar-container">
        {/* Clickable Logo navigating to Home "/" */}
        <Link to="/" className="navbar-logo" onClick={handleLogoClick}>
          <Shield className="logo-icon" size={24} />
          <span className="logo-text">
            SmartRoad <span className="highlight">AI</span>
          </span>
        </Link>
        {/* Desktop Menu */}
        <ul className="navbar-links">
          {NAV_ITEMS.map((item) => (
            <li key={item.name}>
              <Link 
                to={item.path} 
                className={`nav-link ${isItemActive(item) ? 'active' : ''}`}
                onClick={(e) => handleNavClick(e, item)}
              >
                {item.name}
              </Link>
            </li>
          ))}
          <li>
            <Link to="/login" className="btn-login">
              Login
            </Link>
          </li>
        </ul>
        {/* Mobile Menu Button with improved accessibility */}
        <button 
          className="mobile-menu-btn" 
          onClick={toggleMenu} 
          aria-expanded={isOpen}
          aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-controls="mobile-nav-menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        {/* Mobile Menu Dropdown */}
        <div 
          id="mobile-nav-menu" 
          className={`mobile-menu ${isOpen ? 'active' : ''}`}
        >
          <ul className="mobile-links">
            {NAV_ITEMS.map((item) => (
              <li key={item.name}>
                <Link 
                  to={item.path} 
                  className={`mobile-link ${isItemActive(item) ? 'active' : ''}`}
                  onClick={(e) => handleNavClick(e, item)}
                >
                  {item.name}
                </Link>
              </li>
            ))}
            <li>
              <Link 
                to="/login" 
                className="mobile-btn-login" 
                onClick={closeMenu}
              >
                Login
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};
export default Navbar;
