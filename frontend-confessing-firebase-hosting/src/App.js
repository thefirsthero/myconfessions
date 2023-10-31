import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AppNavbar from './components/common/Navbar';
import Post from './components/post/Post';
import Feed from './components/feed/Feed';

function App() {
  return (
    <div className="App">
      <AppNavbar />
      <Routes>
        <Route path="/make-confession" element={<Post />} />
        <Route path="/feed" element={<Feed />} />
        {/* Define the root ("/") route to use the Feed component */}
        <Route path="/" element={<Feed />} />
      </Routes>
    </div>
  );
}

export default App;
