import React, { useState } from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import { NavLink } from 'react-router-dom';
// Import the TikTok logo image or use the image URL
import tiktokLogo from './assets/tiktok-logo.png';
// const tiktokLogo = 'https://i.imgur.com/xxxxxx.png';
import './Navbar.css';

function AppNavbar() {
  const [expanded, setExpanded] = useState(false);

  const closeNav = () => {
    setExpanded(false);
  };

  // Function to open your TikTok account page in a new tab/window
  const openTikTokPage = () => {
    // Replace 'YOUR_TIKTOK_PROFILE_URL' with your actual TikTok profile URL
    window.open('https://www.tiktok.com/@zaconfessions', '_blank');
  };

  return (
    <Navbar expand="lg" bg="dark" variant="dark" expanded={expanded}>
      <Container>
        <Navbar.Brand href="#home">Welcome to My Confessions</Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" onClick={() => setExpanded(!expanded)} />
        <Navbar.Collapse id="responsive-navbar-nav" className="justify-content-end">
          <Nav className="ml-auto">
            <Nav.Item className="d-flex align-items-center">
              <img src={tiktokLogo} alt="TikTok" className="tiktok-logo me-2" onClick={openTikTokPage} />
            </Nav.Item>
            <Nav.Item>
              <NavLink to="/make-confession" className="nav-link" onClick={closeNav}>
                Make Confession
              </NavLink>
            </Nav.Item>
            <Nav.Item>
              <NavLink to="/feed" className="nav-link" onClick={closeNav}>
                Feed
              </NavLink>
            </Nav.Item>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default AppNavbar;
