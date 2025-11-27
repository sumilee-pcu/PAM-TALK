/**
 * Order Management Page (Admin)
 * 주문 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import marketplaceService from '../../../services/api/marketplaceService';
import './OrderManagementPage.css';

function OrderManagementPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    loadOrders();
  }, [statusFilter]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const response = await marketplaceService.getAllOrders(params);
      if (response.success && response.data) {
        setOrders(response.data);
      }
    } catch (error) {
      console.error('주문 로딩 실패:', error);
      alert('주문 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId, newStatus) => {
    if (!window.confirm(`주문 상태를 '${getStatusLabel(newStatus)}'(으)로 변경하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      await marketplaceService.updateOrderStatus(orderId, newStatus);
      alert('✅ 주문 상태가 변경되었습니다.');
      loadOrders();
    } catch (error) {
      console.error('상태 변경 실패:', error);
      alert('❌ ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const showOrderDetail = async (orderId) => {
    try {
      setLoading(true);
      const response = await marketplaceService.getOrderById(orderId);
      if (response.success && response.data) {
        setSelectedOrder(response.data);
        setShowDetailModal(true);
      }
    } catch (error) {
      console.error('주문 상세 조회 실패:', error);
      alert('주문 상세 정보를 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      pending: '대기중',
      confirmed: '확인됨',
      shipping: '배송중',
      delivered: '배송완료',
      cancelled: '취소됨'
    };
    return labels[status] || status;
  };

  const getStatusClass = (status) => {
    const classes = {
      pending: 'status-pending',
      confirmed: 'status-confirmed',
      shipping: 'status-shipping',
      delivered: 'status-delivered',
      cancelled: 'status-cancelled'
    };
    return classes[status] || '';
  };

  const calculateStats = () => {
    const total = orders.length;
    const pending = orders.filter(o => o.status === 'pending').length;
    const completed = orders.filter(o => o.status === 'delivered').length;
    const revenue = orders
      .filter(o => o.status !== 'cancelled')
      .reduce((sum, o) => sum + (o.total_amount || 0), 0);

    return { total, pending, completed, revenue };
  };

  const stats = calculateStats();

  return (
    <div className="order-management-page">
      <div className="page-header">
        <h1>📦 주문 관리</h1>
        <div className="filter-group">
          <label>상태 필터:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">전체</option>
            <option value="pending">대기중</option>
            <option value="confirmed">확인됨</option>
            <option value="shipping">배송중</option>
            <option value="delivered">배송완료</option>
            <option value="cancelled">취소됨</option>
          </select>
        </div>
      </div>

      <div className="orders-stats">
        <div className="stat-card">
          <h3>전체 주문</h3>
          <p className="stat-value">{stats.total}</p>
        </div>
        <div className="stat-card">
          <h3>처리 대기</h3>
          <p className="stat-value pending-color">{stats.pending}</p>
        </div>
        <div className="stat-card">
          <h3>배송 완료</h3>
          <p className="stat-value success-color">{stats.completed}</p>
        </div>
        <div className="stat-card">
          <h3>총 매출</h3>
          <p className="stat-value">{stats.revenue.toLocaleString()}원</p>
        </div>
      </div>

      {loading && <div className="loading">로딩 중...</div>}

      <div className="orders-table-container">
        <table className="orders-table">
          <thead>
            <tr>
              <th>주문 ID</th>
              <th>고객 주소</th>
              <th>주문금액</th>
              <th>결제방법</th>
              <th>상태</th>
              <th>주문일시</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan="7" className="no-data">주문 내역이 없습니다.</td>
              </tr>
            ) : (
              orders.map(order => (
                <tr key={order.order_id}>
                  <td>
                    <button
                      className="link-button"
                      onClick={() => showOrderDetail(order.order_id)}
                    >
                      {order.order_id}
                    </button>
                  </td>
                  <td>
                    <code className="address-code">
                      {order.user_address.substring(0, 10)}...
                    </code>
                  </td>
                  <td><strong>{order.total_amount.toLocaleString()}원</strong></td>
                  <td>
                    <span className="badge">
                      {order.payment_method === 'token' ? '토큰' : '현금'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${getStatusClass(order.status)}`}>
                      {getStatusLabel(order.status)}
                    </span>
                  </td>
                  <td>{new Date(order.created_at).toLocaleString('ko-KR')}</td>
                  <td>
                    <select
                      value={order.status}
                      onChange={(e) => handleStatusChange(order.order_id, e.target.value)}
                      className="status-select"
                      disabled={order.status === 'delivered' || order.status === 'cancelled'}
                    >
                      <option value="pending">대기중</option>
                      <option value="confirmed">확인됨</option>
                      <option value="shipping">배송중</option>
                      <option value="delivered">배송완료</option>
                      <option value="cancelled">취소됨</option>
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* 주문 상세 모달 */}
      {showDetailModal && selectedOrder && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal-content order-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>주문 상세 정보</h2>
              <button className="btn-close" onClick={() => setShowDetailModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h3>📋 주문 정보</h3>
                <div className="detail-row">
                  <span className="label">주문 ID:</span>
                  <span className="value">{selectedOrder.order_id}</span>
                </div>
                <div className="detail-row">
                  <span className="label">주문 상태:</span>
                  <span className={`status-badge ${getStatusClass(selectedOrder.status)}`}>
                    {getStatusLabel(selectedOrder.status)}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="label">주문 일시:</span>
                  <span className="value">
                    {new Date(selectedOrder.created_at).toLocaleString('ko-KR')}
                  </span>
                </div>
              </div>

              <div className="detail-section">
                <h3>👤 고객 정보</h3>
                <div className="detail-row">
                  <span className="label">고객 주소:</span>
                  <code className="value address-full">{selectedOrder.user_address}</code>
                </div>
                {selectedOrder.delivery_address && (
                  <div className="detail-row">
                    <span className="label">배송지:</span>
                    <span className="value">{selectedOrder.delivery_address}</span>
                  </div>
                )}
                {selectedOrder.delivery_phone && (
                  <div className="detail-row">
                    <span className="label">연락처:</span>
                    <span className="value">{selectedOrder.delivery_phone}</span>
                  </div>
                )}
                {selectedOrder.delivery_request && (
                  <div className="detail-row">
                    <span className="label">배송 요청사항:</span>
                    <span className="value">{selectedOrder.delivery_request}</span>
                  </div>
                )}
              </div>

              <div className="detail-section">
                <h3>🛒 주문 상품</h3>
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>상품 ID</th>
                      <th>수량</th>
                      <th>단가</th>
                      <th>소계</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedOrder.items && selectedOrder.items.map((item, index) => (
                      <tr key={index}>
                        <td>{item.product_id}</td>
                        <td>{item.quantity}개</td>
                        <td>{item.price ? item.price.toLocaleString() : '-'}원</td>
                        <td>
                          <strong>
                            {(item.quantity * (item.price || 0)).toLocaleString()}원
                          </strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="detail-section">
                <h3>💳 결제 정보</h3>
                <div className="detail-row">
                  <span className="label">결제 방법:</span>
                  <span className="value">
                    {selectedOrder.payment_method === 'token' ? '토큰 결제' : '현금 결제'}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="label">총 결제 금액:</span>
                  <span className="value total-amount">
                    {selectedOrder.total_amount.toLocaleString()}원
                  </span>
                </div>
                {selectedOrder.payment_txid && (
                  <div className="detail-row">
                    <span className="label">트랜잭션 ID:</span>
                    <code className="value txid">{selectedOrder.payment_txid}</code>
                  </div>
                )}
                {selectedOrder.coupon_id && (
                  <div className="detail-row">
                    <span className="label">사용 쿠폰:</span>
                    <span className="value">{selectedOrder.coupon_id}</span>
                  </div>
                )}
              </div>

              {selectedOrder.total_carbon_saved > 0 && (
                <div className="detail-section carbon-section">
                  <h3>🌱 탄소 절감</h3>
                  <div className="detail-row">
                    <span className="label">절감량:</span>
                    <span className="value carbon-value">
                      {selectedOrder.total_carbon_saved.toFixed(2)} kg CO₂
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OrderManagementPage;
