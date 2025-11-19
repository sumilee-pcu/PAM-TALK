/**
 * How It Works Section
 * 작동 방식 섹션
 */

import React from 'react';

function HowItWorksSection() {
  const steps = [
    {
      number: '01',
      title: '가입 & 지갑 연결',
      description: '무료로 가입하고 Pera Wallet을 연결하세요. 간단한 인증 후 바로 시작할 수 있습니다.',
      icon: '🔐',
      image: 'https://images.unsplash.com/photo-1633265486064-086b219458ec?w=500&h=350&fit=crop'
    },
    {
      number: '02',
      title: '친환경 활동 기록',
      description: '로컬푸드 구매, 재활용, 대중교통 이용 등 일상 속 친환경 활동을 앱으로 기록하세요.',
      icon: '📸',
      image: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=500&h=350&fit=crop'
    },
    {
      number: '03',
      title: '증빙 자료 제출',
      description: '영수증, 사진, GPS 위치 등 증빙 자료를 업로드하여 활동을 증명하세요.',
      icon: '📄',
      image: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=500&h=350&fit=crop'
    },
    {
      number: '04',
      title: 'ESG 위원회 검증',
      description: '전문 위원회가 제출한 자료를 검토하고 정확한 탄소 감축량을 계산합니다.',
      icon: '✅',
      image: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=350&fit=crop'
    },
    {
      number: '05',
      title: '블록체인 기록',
      description: '검증 결과가 블록체인에 영구적으로 기록되어 투명성과 신뢰성이 보장됩니다.',
      icon: '⛓️',
      image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=500&h=350&fit=crop'
    },
    {
      number: '06',
      title: 'ESG-GOLD 수령',
      description: '검증 완료 즉시 ESG-GOLD 디지털 쿠폰을 받고, 로컬푸드나 친환경 제품 구매에 사용하세요.',
      icon: '🪙',
      image: 'https://images.unsplash.com/photo-1607082349566-187342175e2f?w=500&h=350&fit=crop'
    }
  ];

  return (
    <section className="how-it-works-section">
      <div className="how-it-works-container">
        <div className="section-header">
          <h2 className="section-title">
            <span className="gradient-text">어떻게</span> 작동하나요?
          </h2>
          <p className="section-description">
            6단계로 간단하게 탄소 감축 활동을 시작하고 리워드를 받으세요
          </p>
        </div>

        <div className="steps-timeline">
          {steps.map((step, index) => (
            <div key={index} className="step-item">
              <div className="step-line">
                <div className="step-dot"></div>
                {index < steps.length - 1 && <div className="step-connector"></div>}
              </div>
              <div className="step-content">
                <div className="step-image">
                  <img src={step.image} alt={step.title} />
                  <div className="step-number">{step.number}</div>
                  <div className="step-icon">{step.icon}</div>
                </div>
                <div className="step-info">
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-description">{step.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorksSection;
