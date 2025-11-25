/**
 * System Page
 * 시스템 설정 및 관리 페이지
 */

import React, { useState } from 'react';
import '../Users/UsersPage.css';

function SystemPage() {
  const [settings, setSettings] = useState({
    maintenanceMode: false,
    registrationEnabled: true,
    emailNotifications: true,
    smsNotifications: false,
    autoBackup: true,
    maxUploadSize: 10,
    sessionTimeout: 30
  });

  const handleToggle = (key) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = () => {
    localStorage.setItem('admin_system_settings', JSON.stringify(settings));
    alert('✅ 설정이 저장되었습니다.');
  };

  const systemInfo = {
    version: '1.0.0',
    environment: 'Development',
    database: 'PostgreSQL 14.5',
    cache: 'Redis 7.0',
    server: 'Node.js 18.x',
    uptime: '7일 14시간 32분'
  };

  const logs = [
    { id: 1, level: 'INFO', message: '사용자 로그인: admin@pamtalk.com', timestamp: '2024-11-22 10:30:15' },
    { id: 2, level: 'SUCCESS', message: '쿠폰 발행 완료: 1000개', timestamp: '2024-11-22 10:15:08' },
    { id: 3, level: 'WARNING', message: 'API 응답 시간 증가: 1.2s', timestamp: '2024-11-22 09:45:22' },
    { id: 4, level: 'ERROR', message: '블록체인 연결 재시도', timestamp: '2024-11-22 09:30:10' },
    { id: 5, level: 'INFO', message: '자동 백업 완료', timestamp: '2024-11-22 09:00:00' }
  ];

  const getLevelBadge = (level) => {
    const classes = {
      'INFO': 'role-badge consumer',
      'SUCCESS': 'role-badge farmer',
      'WARNING': 'role-badge committee',
      'ERROR': 'role-badge admin'
    };
    return classes[level] || 'role-badge';
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>⚙️ 시스템 설정</h1>
        <p>시스템 설정 및 모니터링</p>
      </div>

      {/* 시스템 정보 */}
      <div className="users-table-container" style={{marginBottom: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>시스템 정보</h2>
        <div className="user-detail-grid">
          <div className="detail-item">
            <label>버전</label>
            <div>{systemInfo.version}</div>
          </div>
          <div className="detail-item">
            <label>환경</label>
            <div>{systemInfo.environment}</div>
          </div>
          <div className="detail-item">
            <label>데이터베이스</label>
            <div>{systemInfo.database}</div>
          </div>
          <div className="detail-item">
            <label>캐시</label>
            <div>{systemInfo.cache}</div>
          </div>
          <div className="detail-item">
            <label>서버</label>
            <div>{systemInfo.server}</div>
          </div>
          <div className="detail-item">
            <label>가동 시간</label>
            <div className="points-large">{systemInfo.uptime}</div>
          </div>
        </div>
      </div>

      {/* 시스템 설정 */}
      <div className="users-table-container" style={{marginBottom: '2rem'}}>
        <h2 style={{marginBottom: '1.5rem'}}>시스템 설정</h2>

        <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
          {/* 유지보수 모드 */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
            <div>
              <div style={{fontWeight: 600, marginBottom: '0.25rem'}}>유지보수 모드</div>
              <div style={{fontSize: '0.9rem', color: '#666'}}>시스템 점검 시 활성화</div>
            </div>
            <label style={{position: 'relative', display: 'inline-block', width: '60px', height: '34px'}}>
              <input
                type="checkbox"
                checked={settings.maintenanceMode}
                onChange={() => handleToggle('maintenanceMode')}
                style={{opacity: 0, width: 0, height: 0}}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.maintenanceMode ? '#667eea' : '#ccc',
                borderRadius: '34px',
                transition: '0.4s'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '26px',
                  width: '26px',
                  left: settings.maintenanceMode ? '30px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  borderRadius: '50%',
                  transition: '0.4s'
                }} />
              </span>
            </label>
          </div>

          {/* 회원가입 허용 */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
            <div>
              <div style={{fontWeight: 600, marginBottom: '0.25rem'}}>회원가입 허용</div>
              <div style={{fontSize: '0.9rem', color: '#666'}}>신규 사용자 가입 활성화</div>
            </div>
            <label style={{position: 'relative', display: 'inline-block', width: '60px', height: '34px'}}>
              <input
                type="checkbox"
                checked={settings.registrationEnabled}
                onChange={() => handleToggle('registrationEnabled')}
                style={{opacity: 0, width: 0, height: 0}}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.registrationEnabled ? '#667eea' : '#ccc',
                borderRadius: '34px',
                transition: '0.4s'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '26px',
                  width: '26px',
                  left: settings.registrationEnabled ? '30px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  borderRadius: '50%',
                  transition: '0.4s'
                }} />
              </span>
            </label>
          </div>

          {/* 이메일 알림 */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
            <div>
              <div style={{fontWeight: 600, marginBottom: '0.25rem'}}>이메일 알림</div>
              <div style={{fontSize: '0.9rem', color: '#666'}}>이메일 알림 발송</div>
            </div>
            <label style={{position: 'relative', display: 'inline-block', width: '60px', height: '34px'}}>
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={() => handleToggle('emailNotifications')}
                style={{opacity: 0, width: 0, height: 0}}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.emailNotifications ? '#667eea' : '#ccc',
                borderRadius: '34px',
                transition: '0.4s'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '26px',
                  width: '26px',
                  left: settings.emailNotifications ? '30px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  borderRadius: '50%',
                  transition: '0.4s'
                }} />
              </span>
            </label>
          </div>

          {/* 자동 백업 */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
            <div>
              <div style={{fontWeight: 600, marginBottom: '0.25rem'}}>자동 백업</div>
              <div style={{fontSize: '0.9rem', color: '#666'}}>매일 자동 백업 실행</div>
            </div>
            <label style={{position: 'relative', display: 'inline-block', width: '60px', height: '34px'}}>
              <input
                type="checkbox"
                checked={settings.autoBackup}
                onChange={() => handleToggle('autoBackup')}
                style={{opacity: 0, width: 0, height: 0}}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: settings.autoBackup ? '#667eea' : '#ccc',
                borderRadius: '34px',
                transition: '0.4s'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '',
                  height: '26px',
                  width: '26px',
                  left: settings.autoBackup ? '30px' : '4px',
                  bottom: '4px',
                  background: 'white',
                  borderRadius: '50%',
                  transition: '0.4s'
                }} />
              </span>
            </label>
          </div>
        </div>

        <button
          onClick={handleSave}
          style={{
            marginTop: '1.5rem',
            padding: '0.75rem 2rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          💾 설정 저장
        </button>
      </div>

      {/* 시스템 로그 */}
      <div className="users-table-container">
        <h2 style={{marginBottom: '1rem'}}>시스템 로그</h2>
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>레벨</th>
              <th>메시지</th>
              <th>시간</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>
                  <span className={getLevelBadge(log.level)}>
                    {log.level}
                  </span>
                </td>
                <td>{log.message}</td>
                <td style={{fontSize: '0.9rem'}}>{log.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default SystemPage;
