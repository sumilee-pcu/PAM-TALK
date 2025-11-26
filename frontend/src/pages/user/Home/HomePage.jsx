/**
 * HomePage - PAM-TALK Landing Page
 * 프로페셔널 랜딩 페이지
 */

import React, { useEffect } from 'react';
import HeroSection from './HeroSection';
import FeaturesSection from './FeaturesSection';
import StatsSection from './StatsSection';
import HowItWorksSection from './HowItWorksSection';
import BlockchainSection from './BlockchainSection';
import TestimonialsSection from './TestimonialsSection';
import PartnersSection from './PartnersSection';
import CTASection from './CTASection';
import LSTMDemoSection from './LSTMDemoSection';
import './HomePage.css';

function HomePage() {
  useEffect(() => {
    // 페이지 로드 시 스크롤 최상단으로
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="home-page">
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <LSTMDemoSection />
      {/* HowItWorksSection - 내부 운영 프로세스, 위원회 페이지에서만 표시 */}
      {/* BlockchainSection - 내부 운영 프로세스, 위원회 페이지에서만 표시 */}
      <TestimonialsSection />
      <PartnersSection />
      <CTASection />
    </div>
  );
}

export default HomePage;
