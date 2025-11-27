/**
 * Product Management Page (Admin)
 * 상품 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import marketplaceService from '../../../services/api/marketplaceService';
import './ProductManagementPage.css';

function ProductManagementPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentProduct, setCurrentProduct] = useState({
    product_id: '',
    name: '',
    category: '',
    price: '',
    stock: '',
    description: '',
    image_url: '',
    farm_id: 'FARM_001'
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await marketplaceService.getProducts();
      if (response.success && response.data) {
        setProducts(response.data);
      }
    } catch (error) {
      console.error('상품 로딩 실패:', error);
      alert('상품 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentProduct(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const openCreateModal = () => {
    setEditMode(false);
    setCurrentProduct({
      product_id: `PRODUCT_${Date.now()}`,
      name: '',
      category: '',
      price: '',
      stock: '',
      description: '',
      image_url: '',
      farm_id: 'FARM_001'
    });
    setShowModal(true);
  };

  const openEditModal = (product) => {
    setEditMode(true);
    setCurrentProduct({
      product_id: product.product_id,
      name: product.name,
      category: product.category,
      price: product.price.toString(),
      stock: product.stock.toString(),
      description: product.description || '',
      image_url: product.image_url || '',
      farm_id: product.farm_id || 'FARM_001'
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!currentProduct.name || !currentProduct.category || !currentProduct.price || !currentProduct.stock) {
      alert('필수 항목을 모두 입력해주세요.');
      return;
    }

    try {
      setLoading(true);

      const productData = {
        ...currentProduct,
        price: parseFloat(currentProduct.price),
        stock: parseInt(currentProduct.stock)
      };

      if (editMode) {
        await marketplaceService.updateProduct(currentProduct.product_id, productData);
        alert('✅ 상품이 수정되었습니다.');
      } else {
        await marketplaceService.createProduct(productData);
        alert('✅ 상품이 등록되었습니다.');
      }

      setShowModal(false);
      loadProducts();
    } catch (error) {
      console.error('상품 저장 실패:', error);
      alert('❌ ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('정말 이 상품을 삭제하시겠습니까?')) {
      return;
    }

    try {
      setLoading(true);
      await marketplaceService.deleteProduct(productId);
      alert('✅ 상품이 삭제되었습니다.');
      loadProducts();
    } catch (error) {
      console.error('상품 삭제 실패:', error);
      alert('❌ ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-management-page">
      <div className="page-header">
        <h1>🛒 상품 관리</h1>
        <button className="btn-primary" onClick={openCreateModal}>
          + 신규 상품 등록
        </button>
      </div>

      <div className="products-stats">
        <div className="stat-card">
          <h3>전체 상품</h3>
          <p className="stat-value">{products.length}</p>
        </div>
        <div className="stat-card">
          <h3>재고 부족</h3>
          <p className="stat-value">{products.filter(p => p.stock < 10).length}</p>
        </div>
        <div className="stat-card">
          <h3>총 재고</h3>
          <p className="stat-value">{products.reduce((sum, p) => sum + p.stock, 0)}</p>
        </div>
      </div>

      {loading && <div className="loading">로딩 중...</div>}

      <div className="products-table-container">
        <table className="products-table">
          <thead>
            <tr>
              <th>이미지</th>
              <th>상품 ID</th>
              <th>상품명</th>
              <th>카테고리</th>
              <th>가격</th>
              <th>재고</th>
              <th>농장 ID</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {products.length === 0 ? (
              <tr>
                <td colSpan="8" className="no-data">등록된 상품이 없습니다.</td>
              </tr>
            ) : (
              products.map(product => (
                <tr key={product.product_id}>
                  <td>
                    {product.image_url ? (
                      <img src={product.image_url} alt={product.name} className="product-thumb" />
                    ) : (
                      <div className="product-thumb-placeholder">No Image</div>
                    )}
                  </td>
                  <td>{product.product_id}</td>
                  <td><strong>{product.name}</strong></td>
                  <td><span className="badge">{product.category}</span></td>
                  <td>{product.price.toLocaleString()}원</td>
                  <td>
                    <span className={product.stock < 10 ? 'stock-low' : 'stock-ok'}>
                      {product.stock}개
                    </span>
                  </td>
                  <td>{product.farm_id || '-'}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-edit" onClick={() => openEditModal(product)}>
                        수정
                      </button>
                      <button className="btn-delete" onClick={() => handleDelete(product.product_id)}>
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* 상품 등록/수정 모달 */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editMode ? '상품 수정' : '신규 상품 등록'}</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSubmit} className="product-form">
              <div className="form-group">
                <label>상품 ID *</label>
                <input
                  type="text"
                  name="product_id"
                  value={currentProduct.product_id}
                  onChange={handleInputChange}
                  disabled={editMode}
                  required
                />
              </div>

              <div className="form-group">
                <label>상품명 *</label>
                <input
                  type="text"
                  name="name"
                  value={currentProduct.name}
                  onChange={handleInputChange}
                  placeholder="예: 유기농 사과"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>카테고리 *</label>
                  <select
                    name="category"
                    value={currentProduct.category}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">선택</option>
                    <option value="과일">과일</option>
                    <option value="채소">채소</option>
                    <option value="곡물/쌀">곡물/쌀</option>
                    <option value="축산물">축산물</option>
                    <option value="수산물">수산물</option>
                    <option value="가공식품">가공식품</option>
                    <option value="건강식품">건강식품</option>
                    <option value="런칭특가">런칭특가</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>농장 ID</label>
                  <select
                    name="farm_id"
                    value={currentProduct.farm_id}
                    onChange={handleInputChange}
                  >
                    <option value="FARM_001">FARM_001</option>
                    <option value="FARM_002">FARM_002</option>
                    <option value="FARM_003">FARM_003</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>가격 (원) *</label>
                  <input
                    type="number"
                    name="price"
                    value={currentProduct.price}
                    onChange={handleInputChange}
                    placeholder="예: 5000"
                    min="0"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>재고 수량 *</label>
                  <input
                    type="number"
                    name="stock"
                    value={currentProduct.stock}
                    onChange={handleInputChange}
                    placeholder="예: 100"
                    min="0"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>설명</label>
                <textarea
                  name="description"
                  value={currentProduct.description}
                  onChange={handleInputChange}
                  placeholder="상품 설명을 입력하세요"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>이미지 URL</label>
                <input
                  type="text"
                  name="image_url"
                  value={currentProduct.image_url}
                  onChange={handleInputChange}
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={() => setShowModal(false)}>
                  취소
                </button>
                <button type="submit" className="btn-submit" disabled={loading}>
                  {loading ? '처리중...' : (editMode ? '수정하기' : '등록하기')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductManagementPage;
