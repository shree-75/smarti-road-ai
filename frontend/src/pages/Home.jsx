import React from 'react';
import Navbar from '../components/layout/Navbar';
import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import About from '../components/home/About';
import Footer from '../components/layout/Footer';

const Home = () => {
  return (
    <div className="home-page">
      <Navbar />

      <main id="main-content">
        <Hero />
        <Features />
        <About />
      </main>

      <Footer />
    </div>
  );
};

export default Home;