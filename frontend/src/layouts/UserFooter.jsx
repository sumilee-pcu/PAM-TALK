/**
 * User Portal Footer
 * 사용자 포털 푸터
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './UserFooter.css';

function UserFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="user-footer">
      <div className="footer-container">
        {/* Footer Top */}
        <div className="footer-top">
          {/* Company Info */}
          <div className="footer-section">
            <div className="footer-logo">
              <div className="logo-icon">🌱</div>
              <span className="logo-text">PAM-TALK</span>
            </div>
            <p className="footer-description">
              블록체인 기반 탄소 감축 활동 플랫폼<br />
              지구를 지키는 작은 실천, PAM-TALK과 함께하세요
            </p>
            <div className="social-links">
              <a href="https://facebook.com" aria-label="Facebook" target="_blank" rel="noopener noreferrer"><i className="fab fa-facebook"></i></a>
              <a href="https://twitter.com" aria-label="Twitter" target="_blank" rel="noopener noreferrer"><i className="fab fa-twitter"></i></a>
              <a href="https://instagram.com" aria-label="Instagram" target="_blank" rel="noopener noreferrer"><i className="fab fa-instagram"></i></a>
              <a href="https://youtube.com" aria-label="YouTube" target="_blank" rel="noopener noreferrer"><i className="fab fa-youtube"></i></a>
            </div>
          </div>

          {/* Product */}
          <div className="footer-section">
            <h4>서비스</h4>
            <ul>
              <li><Link to="/activities">탄소 감축 활동</Link></li>
              <li><Link to="/coupons">디지털 쿠폰</Link></li>
              <li><Link to="/marketplace">친환경 마켓</Link></li>
              <li><Link to="/community">커뮤니티</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div className="footer-section">
            <h4>회사</h4>
            <ul>
              <li><Link to="/about">회사 소개</Link></li>
              <li><Link to="/team">팀 소개</Link></li>
              <li><Link to="/careers">채용</Link></li>
              <li><Link to="/press">보도자료</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div className="footer-section">
            <h4>고객지원</h4>
            <ul>
              <li><Link to="/support">고객센터</Link></li>
              <li><Link to="/faq">FAQ</Link></li>
              <li><Link to="/guides">이용가이드</Link></li>
              <li><Link to="/contact">문의하기</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="footer-section">
            <h4>법적고지</h4>
            <ul>
              <li><Link to="/terms">이용약관</Link></li>
              <li><Link to="/privacy">개인정보처리방침</Link></li>
              <li><Link to="/blockchain">블록체인 정책</Link></li>
              <li><Link to="/licenses">라이선스</Link></li>
            </ul>
          </div>
        </div>

        {/* Footer Bottom */}
        <div className="footer-bottom">
          <div className="footer-bottom-left">
            <p>&copy; {currentYear} PAM-TALK. All rights reserved.</p>
            <p className="footer-company-info">
              (주)팜톡 | 대표이사: 홍길동 | 사업자등록번호: 123-45-67890<br />
              서울특별시 강남구 테헤란로 123 | 이메일: contact@pam-talk.com
            </p>
          </div>
          <div className="footer-bottom-right">
            <div className="blockchain-badge">
              <img src="https://algorand.foundation/static/algorand-logo.svg" alt="Algorand" />
              <span>Powered by Algorand</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default UserFooter;
