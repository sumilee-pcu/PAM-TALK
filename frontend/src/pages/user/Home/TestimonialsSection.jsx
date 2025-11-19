/**
 * Testimonials Section
 * 사용자 후기 섹션
 */

import React, { useState } from 'react';

function TestimonialsSection() {
  const [activeIndex, setActiveIndex] = useState(0);

  const testimonials = [
    {
      name: '김지영',
      role: '직장인',
      avatar: 'https://i.pravatar.cc/150?img=5',
      rating: 5,
      content: '매일 대중교통을 이용하는데 이렇게 포인트로 돌려받을 수 있다니 놀라워요! 6개월간 모은 포인트로 친환경 제품도 구매했습니다.',
      stats: { points: '12,500', carbon: '45kg' }
    },
    {
      name: '박민수',
      role: '환경운동가',
      avatar: 'https://i.pravatar.cc/150?img=12',
      rating: 5,
      content: '로컬푸드 챌린지에 참여하면서 우리 동네 농부님들도 알게 되고, 포인트도 쌓여서 일석이조예요. 정말 의미있는 활동입니다!',
      stats: { points: '28,900', carbon: '125kg' }
    },
    {
      name: '이서연',
      role: '대학생',
      avatar: 'https://i.pravatar.cc/150?img=9',
      rating: 5,
      content: '앱 사용이 정말 간편해요! 영수증 찍어서 올리면 자동으로 처리되고, 포인트도 바로 들어와요. 친구들에게 추천하고 싶어요.',
      stats: { points: '8,200', carbon: '32kg' }
    },
    {
      name: '정현우',
      role: '자영업자',
      avatar: 'https://i.pravatar.cc/150?img=15',
      rating: 5,
      content: '로컬푸드 매장을 운영하는데 PAM-TALK 덕분에 고객들이 더 많이 찾아주세요. 서로 윈윈하는 좋은 플랫폼입니다!',
      stats: { points: '35,000', carbon: '180kg' }
    }
  ];

  const nextTestimonial = () => {
    setActiveIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setActiveIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <section className="testimonials-section">
      <div className="testimonials-container">
        <div className="section-header">
          <h2 className="section-title">
            사용자들의 <span className="gradient-text">실제 후기</span>
          </h2>
          <p className="section-description">
            PAM-TALK과 함께 지구를 지키는 분들의 이야기를 들어보세요
          </p>
        </div>

        <div className="testimonials-carousel">
          <button className="carousel-btn prev" onClick={prevTestimonial}>
            ‹
          </button>

          <div className="testimonials-wrapper">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className={`testimonial-card ${
                  index === activeIndex ? 'active' : ''
                } ${
                  index === (activeIndex - 1 + testimonials.length) % testimonials.length
                    ? 'prev'
                    : ''
                } ${
                  index === (activeIndex + 1) % testimonials.length ? 'next' : ''
                }`}
              >
                <div className="testimonial-content">
                  <div className="rating">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <span key={i} className="star">★</span>
                    ))}
                  </div>
                  <p className="testimonial-text">"{testimonial.content}"</p>
                  <div className="testimonial-stats">
                    <div className="stat">
                      <span className="stat-value">{testimonial.stats.points}</span>
                      <span className="stat-label">포인트 획득</span>
                    </div>
                    <div className="stat">
                      <span className="stat-value">{testimonial.stats.carbon}</span>
                      <span className="stat-label">CO₂ 감축</span>
                    </div>
                  </div>
                </div>
                <div className="testimonial-author">
                  <img src={testimonial.avatar} alt={testimonial.name} />
                  <div className="author-info">
                    <div className="author-name">{testimonial.name}</div>
                    <div className="author-role">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button className="carousel-btn next" onClick={nextTestimonial}>
            ›
          </button>
        </div>

        <div className="carousel-dots">
          {testimonials.map((_, index) => (
            <button
              key={index}
              className={`dot ${index === activeIndex ? 'active' : ''}`}
              onClick={() => setActiveIndex(index)}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export default TestimonialsSection;
