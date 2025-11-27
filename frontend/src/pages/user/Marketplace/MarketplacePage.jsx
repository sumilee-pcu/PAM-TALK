/**
 * PAM MALL Marketplace Page - Enhanced Commercial Version
 * 농산물 직거래 마켓플레이스 고도화
 */

import React, { useState, useEffect } from 'react';
import algorandService, { PAM_TOKEN_ASSET_ID } from '../../../services/blockchain/algorandService';
import marketplaceService from '../../../services/api/marketplaceService';
import './MarketplacePage.css';

function MarketplacePage() {
  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    subCategory: '',
    location: '',
    certification: '',
    priceRange: '',
    search: ''
  });
  const [sortBy, setSortBy] = useState('popular');
  const [wallet, setWallet] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [paying, setPaying] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);

  // 메인 배너 슬라이드
  const bannerSlides = [
    {
      id: 1,
      image: 'https://via.placeholder.com/1200x400/4CAF50/white?text=Fresh+Fruits',
      title: '신선한 제철 과일',
      subtitle: '농부에게 직접! 100% 국내산',
      description: '오늘 수확한 신선함을 그대로',
      badge: '무료배송',
      color: '#4CAF50'
    },
    {
      id: 2,
      image: 'https://via.placeholder.com/1200x400/FF9800/white?text=Organic+Vegetables',
      title: '유기농 채소 특가',
      subtitle: '건강한 밥상의 시작',
      description: '친환경 인증 농산물 최대 30% 할인',
      badge: '최대 30% 할인',
      color: '#FF9800'
    },
    {
      id: 3,
      image: 'https://via.placeholder.com/1200x400/2E7D32/white?text=Fresh+Products',
      title: '이달의 신선 상품',
      subtitle: '지금이 제철! 맛과 영양이 가득',
      description: 'DC 포인트 2배 적립 이벤트',
      badge: 'DC 2배 적립',
      color: '#2E7D32'
    },
    {
      id: 4,
      image: 'https://via.placeholder.com/1200x400/8D6E63/white?text=Local+Food',
      title: '로컬푸드 직거래',
      subtitle: '우리 동네 신선 농산물',
      description: '탄소발자국 ZERO, 지역경제 살리기',
      badge: '친환경',
      color: '#8D6E63'
    }
  ];

  // 카테고리 정의
  const categories = {
    '채소': ['토마토', '오이', '배추', '상추', '시금치', '당근', '무', '호박', '고추', '파'],
    '과일': ['사과', '배', '딸기', '포도', '복숭아', '감', '귤', '수박', '참외', '블루베리'],
    '곡물/쌀': ['백미', '현미', '찹쌀', '보리', '귀리', '콩', '팥', '녹두'],
    '축산물': ['한우', '돼지고기', '닭고기', '오리고기', '계란', '우유'],
    '수산물': ['고등어', '갈치', '조기', '오징어', '새우', '낙지', '멸치', '김'],
    '가공식품': ['된장', '고추장', '간장', '김치', '장아찌', '젓갈'],
    '건강식품': ['홍삼', '꿀', '녹차', '한방차', '효소', '청국장'],
    '생활용품': ['수세미', '천연비누', '친환경세제', '대나무용품']
  };

  // 배너 자동 슬라이드
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % bannerSlides.length);
    }, 5000); // 5초마다 자동 슬라이드

    return () => clearInterval(timer);
  }, [bannerSlides.length]);

  useEffect(() => {
    loadProducts();

    const savedCart = localStorage.getItem('pamtalk_cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }

    const savedWallet = localStorage.getItem('algorand_wallet');
    if (savedWallet) {
      setWallet(JSON.parse(savedWallet));
    }
  }, []);

  // API에서 상품 불러오기
  const loadProducts = async () => {
    try {
      const response = await marketplaceService.getProducts();

      if (response.success && response.data) {
        // API 데이터를 프론트엔드 형식으로 변환
        const apiProducts = response.data.map((item, index) => ({
          product_id: item.product_id,
          name: item.name,
          category: item.category,
          image: item.image_url || `https://images.unsplash.com/photo-1546470427-227a1e3e0d05?w=500`,
          price_per_kg: item.price,
          farmer_name: '직영농장',
          farmer_photo: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100',
          farmer_id: item.farm_id || 'FARM_001',
          location: '충남 아산시',
          certifications: '친환경',
          carbon_footprint: '1.2',
          description: item.description,
          badge: index < 5 ? 'best' : null,
          available_quantity: item.stock,
          distance_km: Math.floor(Math.random() * 100) + 5,
          likes: Math.floor(Math.random() * 150) + 10,
          reviews: Math.floor(Math.random() * 50) + 5,
          rating: (Math.random() * 1.5 + 3.5).toFixed(1),
          discount: item.price === 100 ? 90 : 0 // 런칭특가 상품은 할인
        }));

        // 더미 데이터 추가 (더 풍성하게)
        const demoProducts = generateEnhancedProducts();
        const combinedProducts = [...apiProducts, ...demoProducts];

        setProducts(combinedProducts);
        setFilteredProducts(combinedProducts);
      } else {
        // API 실패 시 더미 데이터만 사용
        const demoProducts = generateEnhancedProducts();
        setProducts(demoProducts);
        setFilteredProducts(demoProducts);
      }
    } catch (error) {
      console.error('상품 로딩 실패:', error);
      // 에러 시에도 더미 데이터 표시
      const demoProducts = generateEnhancedProducts();
      setProducts(demoProducts);
      setFilteredProducts(demoProducts);
    }
  };

  // 필터 적용
  useEffect(() => {
    let filtered = [...products];

    if (filters.category) {
      filtered = filtered.filter(p => p.category === filters.category);
    }
    if (filters.subCategory) {
      filtered = filtered.filter(p => p.name.includes(filters.subCategory));
    }
    if (filters.location) {
      filtered = filtered.filter(p => p.location.includes(filters.location));
    }
    if (filters.certification) {
      filtered = filtered.filter(p => p.certifications.includes(filters.certification));
    }
    if (filters.priceRange) {
      const [min, max] = filters.priceRange.split('-').map(Number);
      filtered = filtered.filter(p => {
        if (max) {
          return p.price_per_kg >= min && p.price_per_kg <= max;
        } else {
          return p.price_per_kg >= min;
        }
      });
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchLower) ||
        p.farmer_name.toLowerCase().includes(searchLower) ||
        p.description.toLowerCase().includes(searchLower)
      );
    }

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price_low':
          return a.price_per_kg - b.price_per_kg;
        case 'price_high':
          return b.price_per_kg - a.price_per_kg;
        case 'distance':
          return a.distance_km - b.distance_km;
        case 'eco_friendly':
          return parseFloat(a.carbon_footprint) - parseFloat(b.carbon_footprint);
        case 'popular':
          return b.likes - a.likes;
        case 'newest':
          return b.product_id.localeCompare(a.product_id);
        default:
          return 0;
      }
    });

    setFilteredProducts(filtered);
  }, [filters, sortBy, products]);

  // 향상된 상품 데이터 생성
  function generateEnhancedProducts() {
    const productData = [
      // 채소류
      { name: '완숙 토마토', category: '채소', image: 'https://via.placeholder.com/500/ef4444/white?text=Tomato', price: 3500, cert: '유기농', carbon: 0.8, desc: '당도 높은 완숙 토마토', badge: 'best' },
      { name: '싱싱 오이', category: '채소', image: 'https://via.placeholder.com/500/22c55e/white?text=Cucumber', price: 2500, cert: '무농약', carbon: 0.6, desc: '아삭아삭 신선한 오이' },
      { name: '포기 배추', category: '채소', image: 'https://via.placeholder.com/500/84cc16/white?text=Cabbage', price: 4000, cert: '친환경', carbon: 1.2, desc: '김장용 배추', badge: 'new' },
      { name: '청상추', category: '채소', image: 'https://via.placeholder.com/500/10b981/white?text=Lettuce', price: 2000, cert: '유기농', carbon: 0.4, desc: '부드러운 청상추' },
      { name: '시금치', category: '채소', image: 'https://via.placeholder.com/500/059669/white?text=Spinach', price: 2800, cert: '무농약', carbon: 0.5, desc: '영양 가득 시금치' },
      { name: '당근', category: '채소', image: 'https://via.placeholder.com/500/f97316/white?text=Carrot', price: 3000, cert: '친환경', carbon: 0.7, desc: '달콤한 당근', badge: 'best' },
      { name: '무', category: '채소', image: 'https://via.placeholder.com/500/f3f4f6/333?text=Radish', price: 2500, cert: '유기농', carbon: 0.9, desc: '아삭한 무' },
      { name: '애호박', category: '채소', image: 'https://via.placeholder.com/500/65a30d/white?text=Zucchini', price: 2200, cert: '무농약', carbon: 0.6, desc: '신선한 애호박' },
      { name: '청양고추', category: '채소', image: 'https://via.placeholder.com/500/dc2626/white?text=Chili', price: 4500, cert: '친환경', carbon: 0.5, desc: '매운 청양고추', badge: 'hot' },
      { name: '대파', category: '채소', image: 'https://via.placeholder.com/500/16a34a/white?text=Green.Onion', price: 1800, cert: '유기농', carbon: 0.4, desc: '향긋한 대파' },

      // 과일류
      { name: '사과(부사)', category: '과일', image: 'https://via.placeholder.com/500/ef4444/white?text=Apple', price: 5000, cert: '유기농', carbon: 1.5, desc: '달콤한 부사 사과', badge: 'best' },
      { name: '배(신고배)', category: '과일', image: 'https://via.placeholder.com/500/eab308/white?text=Pear', price: 6000, cert: '친환경', carbon: 1.4, desc: '즙이 풍부한 신고배' },
      { name: '딸기', category: '과일', image: 'https://via.placeholder.com/500/f43f5e/white?text=Strawberry', price: 8000, cert: '유기농', carbon: 1.8, desc: '당도 높은 딸기', badge: 'new' },
      { name: '포도(샤인머스캣)', category: '과일', image: 'https://via.placeholder.com/500/a78bfa/white?text=Grape', price: 12000, cert: '무농약', carbon: 2.0, desc: '프리미엄 샤인머스캣', badge: 'premium' },
      { name: '복숭아', category: '과일', image: 'https://via.placeholder.com/500/fb923c/white?text=Peach', price: 7000, cert: '친환경', carbon: 1.6, desc: '달콤한 백도 복숭아' },
      { name: '감(단감)', category: '과일', image: 'https://via.placeholder.com/500/ea580c/white?text=Persimmon', price: 4500, cert: '유기농', carbon: 1.3, desc: '아삭한 단감', badge: 'best' },
      { name: '귤(제주)', category: '과일', image: 'https://via.placeholder.com/500/f59e0b/white?text=Tangerine', price: 3500, cert: '친환경', carbon: 1.2, desc: '제주 노지 귤' },
      { name: '수박', category: '과일', image: 'https://via.placeholder.com/500/22c55e/white?text=Watermelon', price: 15000, cert: '무농약', carbon: 2.5, desc: '당도 높은 수박' },
      { name: '참외', category: '과일', image: 'https://via.placeholder.com/500/fde047/333?text=Melon', price: 4000, cert: '친환경', carbon: 1.1, desc: '달콤한 성주 참외' },
      { name: '블루베리', category: '과일', image: 'https://via.placeholder.com/500/6366f1/white?text=Blueberry', price: 9000, cert: '유기농', carbon: 1.7, desc: '생과 블루베리', badge: 'new' },

      // 곡물/쌀
      { name: '백미(10kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/f5f5dc/333?text=Rice', price: 35000, cert: '무농약', carbon: 3.5, desc: '찰진 백미' },
      { name: '현미(10kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/d2b48c/white?text=Brown.Rice', price: 40000, cert: '유기농', carbon: 3.8, desc: '영양 가득 현미', badge: 'best' },
      { name: '찹쌀(5kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/faf0e6/333?text=Sticky.Rice', price: 25000, cert: '친환경', carbon: 2.5, desc: '고소한 찹쌀' },
      { name: '보리쌀(2kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/c19a6b/white?text=Barley', price: 12000, cert: '무농약', carbon: 1.8, desc: '건강한 보리쌀' },
      { name: '귀리(1kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/daa520/white?text=Oat', price: 8000, cert: '유기농', carbon: 1.2, desc: '다이어트 귀리' },
      { name: '서리태(1kg)', category: '곡물/쌀', image: 'https://via.placeholder.com/500/2f4f4f/white?text=Black.Bean', price: 15000, cert: '친환경', carbon: 1.5, desc: '영양 가득 서리태', badge: 'best' },

      // 축산물
      { name: '한우 등심', category: '축산물', image: 'https://via.placeholder.com/500/8b4513/white?text=Beef', price: 45000, cert: '1++등급', carbon: 15.0, desc: '프리미엄 한우', badge: 'premium' },
      { name: '한우 불고기', category: '축산물', image: 'https://via.placeholder.com/500/a0522d/white?text=Bulgogi', price: 28000, cert: '1+등급', carbon: 12.0, desc: '부드러운 불고기용', badge: 'best' },
      { name: '돼지고기 삼겹살', category: '축산물', image: 'https://via.placeholder.com/500/cd853f/white?text=Pork', price: 18000, cert: '1등급', carbon: 8.5, desc: '두툼한 삼겹살' },
      { name: '닭고기(백숙용)', category: '축산물', image: 'https://via.placeholder.com/500/ffefd5/333?text=Chicken', price: 12000, cert: '무항생제', carbon: 4.2, desc: '신선한 백숙용 닭' },
      { name: '오리고기', category: '축산물', image: 'https://via.placeholder.com/500/bc8f8f/white?text=Duck', price: 15000, cert: '친환경', carbon: 5.5, desc: '훈제 오리고기' },
      { name: '유정란(30입)', category: '축산물', image: 'https://via.placeholder.com/500/fff8dc/333?text=Egg', price: 8000, cert: '동물복지', carbon: 2.8, desc: '고급 유정란', badge: 'best' },
      { name: '우유(1L)', category: '축산물', image: 'https://via.placeholder.com/500/ffffff/333?text=Milk', price: 3500, cert: '유기농', carbon: 2.5, desc: '목장 신선 우유' },

      // 수산물
      { name: '고등어', category: '수산물', image: 'https://via.placeholder.com/500/4682b4/white?text=Mackerel', price: 8000, cert: '국내산', carbon: 3.2, desc: '생 고등어', badge: 'new' },
      { name: '갈치', category: '수산물', image: 'https://via.placeholder.com/500/5f9ea0/white?text=Hairtail', price: 25000, cert: '국내산', carbon: 3.8, desc: '제주 은갈치', badge: 'premium' },
      { name: '조기', category: '수산물', image: 'https://via.placeholder.com/500/ffd700/333?text=Croaker', price: 18000, cert: '국내산', carbon: 3.5, desc: '황금 조기' },
      { name: '오징어', category: '수산물', image: 'https://via.placeholder.com/500/f0e68c/333?text=Squid', price: 12000, cert: '국내산', carbon: 2.8, desc: '통통한 오징어' },
      { name: '새우(왕새우)', category: '수산물', image: 'https://via.placeholder.com/500/ff6347/white?text=Shrimp', price: 22000, cert: '국내산', carbon: 4.5, desc: '싱싱한 왕새우', badge: 'best' },
      { name: '낙지', category: '수산물', image: 'https://via.placeholder.com/500/dda0dd/333?text=Octopus', price: 28000, cert: '국내산', carbon: 3.0, desc: '연평도 낙지' },
      { name: '멸치(볶음용)', category: '수산물', image: 'https://via.placeholder.com/500/c0c0c0/333?text=Anchovy', price: 15000, cert: '국내산', carbon: 2.2, desc: '남해안 멸치' },
      { name: '김(재래김)', category: '수산물', image: 'https://via.placeholder.com/500/2f4f2f/white?text=Seaweed', price: 12000, cert: '유기농', carbon: 1.5, desc: '완도 재래김', badge: 'best' },

      // 가공식품
      { name: '전통 된장(1kg)', category: '가공식품', image: 'https://via.placeholder.com/500/8b7355/white?text=Doenjang', price: 15000, cert: '전통식품', carbon: 2.0, desc: '3년 숙성 된장', badge: 'best' },
      { name: '고추장(500g)', category: '가공식품', image: 'https://via.placeholder.com/500/dc143c/white?text=Gochujang', price: 12000, cert: '전통식품', carbon: 1.8, desc: '매콤한 고추장' },
      { name: '국간장(1L)', category: '가공식품', image: 'https://via.placeholder.com/500/654321/white?text=Soy.Sauce', price: 18000, cert: '전통식품', carbon: 2.5, desc: '천연 국간장' },
      { name: '포기김치(2kg)', category: '가공식품', image: 'https://via.placeholder.com/500/ff4500/white?text=Kimchi', price: 22000, cert: '전통식품', carbon: 3.2, desc: '맛있는 배추김치', badge: 'hot' },
      { name: '깍두기(1kg)', category: '가공식품', image: 'https://via.placeholder.com/500/ff6347/white?text=Kkakdugi', price: 12000, cert: '전통식품', carbon: 2.0, desc: '아삭한 깍두기' },
      { name: '오이소박이(500g)', category: '가공식품', image: 'https://via.placeholder.com/500/90ee90/333?text=Pickles', price: 8000, cert: '전통식품', carbon: 1.5, desc: '새콤달콤 오이소박이' },

      // 건강식품
      { name: '6년근 홍삼', category: '건강식품', image: 'https://via.placeholder.com/500/8b4513/white?text=Ginseng', price: 85000, cert: '건강기능식품', carbon: 3.5, desc: '프리미엄 홍삼', badge: 'premium' },
      { name: '아카시아 꿀(1kg)', category: '건강식품', image: 'https://via.placeholder.com/500/ffd700/333?text=Honey', price: 35000, cert: '유기농', carbon: 2.8, desc: '순수 벌꿀', badge: 'best' },
      { name: '제주 녹차', category: '건강식품', image: 'https://via.placeholder.com/500/228b22/white?text=Green.Tea', price: 18000, cert: '유기농', carbon: 1.2, desc: '제주 유기농 녹차' },
      { name: '쌍화차(20포)', category: '건강식품', image: 'https://via.placeholder.com/500/8b4513/white?text=Herbal.Tea', price: 15000, cert: '한방식품', carbon: 1.5, desc: '건강한 쌍화차' },
      { name: '매실효소(1L)', category: '건강식품', image: 'https://via.placeholder.com/500/98fb98/333?text=Plum.Syrup', price: 22000, cert: '전통식품', carbon: 2.2, desc: '3년 숙성 매실효소' },
      { name: '청국장(500g)', category: '건강식품', image: 'https://via.placeholder.com/500/d2691e/white?text=Fermented', price: 12000, cert: '전통식품', carbon: 1.8, desc: '발효 청국장', badge: 'best' },

      // 생활용품
      { name: '친환경 수세미', category: '생활용품', image: 'https://via.placeholder.com/500/9acd32/white?text=Sponge', price: 3000, cert: '친환경', carbon: 0.5, desc: '천연 수세미' },
      { name: '천연 비누', category: '생활용품', image: 'https://via.placeholder.com/500/e6e6fa/333?text=Soap', price: 5000, cert: '천연', carbon: 0.8, desc: '수제 천연비누' },
      { name: '친환경 세제(1L)', category: '생활용품', image: 'https://via.placeholder.com/500/87ceeb/white?text=Detergent', price: 8000, cert: '친환경', carbon: 1.2, desc: '환경 세탁세제' },
      { name: '대나무 칫솔', category: '생활용품', image: 'https://via.placeholder.com/500/8fbc8f/white?text=Toothbrush', price: 4000, cert: '친환경', carbon: 0.3, desc: '대나무 칫솔 3개' }
    ];

    const farmers = [
      { name: '김철수', location: '충남 아산시', photo: 'https://via.placeholder.com/100/4CAF50/white?text=K' },
      { name: '이영희', location: '경기 용인시', photo: 'https://via.placeholder.com/100/FF9800/white?text=L' },
      { name: '박민수', location: '강원 춘천시', photo: 'https://via.placeholder.com/100/2196F3/white?text=P' },
      { name: '정수연', location: '전북 완주군', photo: 'https://via.placeholder.com/100/E91E63/white?text=J' },
      { name: '최동욱', location: '경남 김해시', photo: 'https://via.placeholder.com/100/9C27B0/white?text=C' },
      { name: '강미래', location: '제주시', photo: 'https://via.placeholder.com/100/00BCD4/white?text=K' },
      { name: '윤준호', location: '충북 청주시', photo: 'https://via.placeholder.com/100/FFC107/white?text=Y' },
      { name: '한지우', location: '전남 완도군', photo: 'https://via.placeholder.com/100/795548/white?text=H' }
    ];

    return productData.map((item, index) => {
      const farmer = farmers[index % farmers.length];
      return {
        product_id: `prod_${index + 1}`,
        name: item.name,
        category: item.category,
        image: item.image,
        price_per_kg: item.price,
        farmer_name: farmer.name,
        farmer_photo: farmer.photo,
        farmer_id: `farmer_${(index % farmers.length) + 1}`,
        location: farmer.location,
        certifications: item.cert,
        carbon_footprint: item.carbon,
        description: item.desc,
        badge: item.badge || null,
        available_quantity: Math.floor(Math.random() * 50) + 10,
        distance_km: Math.floor(Math.random() * 100) + 5,
        likes: Math.floor(Math.random() * 150) + 10,
        reviews: Math.floor(Math.random() * 50) + 5,
        rating: (Math.random() * 1.5 + 3.5).toFixed(1),
        discount: item.badge === 'hot' ? 15 : (Math.random() > 0.7 ? Math.floor(Math.random() * 20) + 5 : 0)
      };
    });
  }

  // 배너 슬라이드 네비게이션
  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % bannerSlides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + bannerSlides.length) % bannerSlides.length);
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  // 장바구니에 추가
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.product_id);
    let newCart;

    if (existingItem) {
      newCart = cart.map(item =>
        item.product_id === product.product_id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      );
    } else {
      newCart = [...cart, { ...product, quantity: 1 }];
    }

    setCart(newCart);
    localStorage.setItem('pamtalk_cart', JSON.stringify(newCart));
    showNotification('장바구니에 추가되었습니다! 🛒');
  };

  // 장바구니에서 제거
  const removeFromCart = (productId) => {
    const newCart = cart.filter(item => item.product_id !== productId);
    setCart(newCart);
    localStorage.setItem('pamtalk_cart', JSON.stringify(newCart));
  };

  // 수량 변경
  const updateQuantity = (productId, change) => {
    const newCart = cart.map(item => {
      if (item.product_id === productId) {
        const newQuantity = Math.max(1, item.quantity + change);
        return { ...item, quantity: newQuantity };
      }
      return item;
    }).filter(item => item.quantity > 0);

    setCart(newCart);
    localStorage.setItem('pamtalk_cart', JSON.stringify(newCart));
  };

  // 알림 표시
  const showNotification = (message) => {
    alert(message);
  };

  // 결제
  const handleCheckout = async () => {
    if (cart.length === 0) {
      alert('장바구니가 비어있습니다.');
      return;
    }

    const totalAmount = cart.reduce((sum, item) => sum + (item.price_per_kg * item.quantity), 0);
    const totalCarbon = cart.reduce((sum, item) => sum + (parseFloat(item.carbon_footprint) * item.quantity), 0);

    if (paymentMethod === 'token') {
      if (!wallet) {
        alert('먼저 지갑을 생성해주세요!');
        return;
      }

      if (!wallet.mnemonic) {
        alert('❌ 지갑 니모닉이 없습니다. 지갑을 다시 생성해주세요.');
        return;
      }

      // PAM 토큰 환산 (100원 = 1 PAM, PAM은 3 decimals이므로 1 PAM = 1000 micro-PAM)
      const tokenAmount = Math.ceil(totalAmount / 100);
      const microTokenAmount = tokenAmount * 1000; // Convert to micro-PAM

      const sellerAddress = prompt(
        `🪙 DC(PAM) 토큰 결제\n\n` +
        `총 금액: ${totalAmount.toLocaleString()}원\n` +
        `토큰 수량: ${tokenAmount.toLocaleString()} DC\n` +
        `절약할 탄소: ${totalCarbon.toFixed(1)}kg CO₂\n\n` +
        `판매자의 지갑 주소를 입력하세요:\n` +
        `(테스트용으로 자신의 다른 지갑 주소를 입력해도 됩니다)`
      );

      if (!sellerAddress || sellerAddress.length !== 58) {
        alert('❌ 올바른 지갑 주소를 입력하세요 (58자).');
        return;
      }

      if (!window.confirm(
        `💳 결제를 진행하시겠습니까?\n\n` +
        `상품: ${cart.map(item => `${item.name} x${item.quantity}kg`).join(', ')}\n` +
        `토큰: ${tokenAmount} DC (PAM)\n` +
        `총 금액: ${totalAmount.toLocaleString()}원\n\n` +
        `⚠️ 실제 블록체인 트랜잭션이 발생합니다.`
      )) {
        return;
      }

      setPaying(true);

      try {
        // 1. Check if wallet is opted into PAM token
        const isOptedIn = await algorandService.isOptedIn(wallet.address, PAM_TOKEN_ASSET_ID);

        if (!isOptedIn) {
          alert('⚠️ PAM 토큰에 옵트인이 필요합니다. 먼저 옵트인을 진행합니다...');

          try {
            await algorandService.optInToAsset(wallet.address, wallet.mnemonic, PAM_TOKEN_ASSET_ID);
            alert('✅ PAM 토큰 옵트인 완료!');
          } catch (optInError) {
            throw new Error('옵트인 실패: ' + optInError.message);
          }
        }

        // 2. Check if wallet has enough PAM tokens
        const balance = await algorandService.getAssetBalance(wallet.address, PAM_TOKEN_ASSET_ID);

        if (balance < microTokenAmount) {
          throw new Error(
            `PAM 토큰이 부족합니다.\n필요: ${tokenAmount} DC\n보유: ${(balance / 1000).toFixed(3)} DC`
          );
        }

        // 3. Send PAM token transaction
        const txId = await algorandService.sendTransaction({
          from: wallet.address,
          to: sellerAddress,
          amount: microTokenAmount,
          mnemonic: wallet.mnemonic,
          assetId: PAM_TOKEN_ASSET_ID,
          note: `PAM-TALK 구매: ${cart.map(item => item.name).join(', ')}`
        });

        // 주문 생성 API 호출
        try {
          const orderItems = cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity,
            price: item.price_per_kg
          }));

          const orderResult = await marketplaceService.createOrder({
            user_address: wallet.address,
            items: orderItems,
            payment_txid: txId
          });

          console.log('주문 생성 완료:', orderResult);
        } catch (orderError) {
          console.error('주문 생성 실패:', orderError);
          // 주문 생성 실패해도 결제는 완료됨
        }

        alert(
          `✅ 결제가 완료되었습니다!\n\n` +
          `🪙 사용 토큰: ${tokenAmount} DC (PAM)\n` +
          `🌱 탄소 절감: ${totalCarbon.toFixed(1)}kg CO₂\n` +
          `📋 트랜잭션 ID: ${txId.substring(0, 20)}...\n\n` +
          `주문이 접수되었습니다.`
        );

        setCart([]);
        localStorage.removeItem('pamtalk_cart');
        setCartOpen(false);
      } catch (error) {
        console.error('Payment error:', error);
        alert('❌ 결제 실패: ' + (error.message || '알 수 없는 오류'));
      } finally {
        setPaying(false);
      }
    } else {
      // 일반 결제
      if (window.confirm(
        `💳 일반 결제를 진행하시겠습니까?\n\n` +
        `총 금액: ${totalAmount.toLocaleString()}원\n` +
        `상품: ${cart.map(item => `${item.name} x${item.quantity}kg`).join(', ')}`
      )) {
        try {
          const orderItems = cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity,
            price: item.price_per_kg
          }));

          const userAddress = wallet?.address || `GUEST_${Date.now()}`;
          const orderResult = await marketplaceService.createOrder({
            user_address: userAddress,
            items: orderItems
          });

          console.log('주문 생성 완료:', orderResult);
          alert('✅ 주문이 접수되었습니다!');
        } catch (error) {
          console.error('주문 생성 실패:', error);
          alert('❌ 주문 생성 실패: ' + error.message);
          return;
        }

        setCart([]);
        localStorage.removeItem('pamtalk_cart');
        setCartOpen(false);
      }
    }
  };

  // 좋아요
  const toggleLike = (productId) => {
    setProducts(products.map(p =>
      p.product_id === productId
        ? { ...p, likes: p.likes + 1, liked: !p.liked }
        : p
    ));
  };

  const resetFilters = () => {
    setFilters({
      category: '',
      subCategory: '',
      location: '',
      certification: '',
      priceRange: '',
      search: ''
    });
  };

  return (
    <div className="marketplace-page">
      {/* 사이트 타이틀 */}
      <div className="marketplace-title-bar">
        <div className="title-content">
          <h1>🌾 PAM 농산물 직거래 장터</h1>
          <p>농부에게 직접, 신선하고 건강하게</p>
        </div>
      </div>

      {/* 메인 배너 캐러셀 */}
      <div className="banner-carousel">
        <div className="carousel-container">
          {bannerSlides.map((slide, index) => (
            <div
              key={slide.id}
              className={`carousel-slide ${index === currentSlide ? 'active' : ''} ${index === currentSlide - 1 || (currentSlide === 0 && index === bannerSlides.length - 1) ? 'prev' : ''} ${index === currentSlide + 1 || (currentSlide === bannerSlides.length - 1 && index === 0) ? 'next' : ''}`}
              style={{ backgroundImage: `url(${slide.image})` }}
            >
              <div className="carousel-overlay"></div>
              <div className="carousel-content">
                <span className="carousel-badge" style={{ background: slide.color }}>
                  {slide.badge}
                </span>
                <h2 className="carousel-title">{slide.title}</h2>
                <p className="carousel-subtitle">{slide.subtitle}</p>
                <p className="carousel-description">{slide.description}</p>
                <div className="carousel-stats">
                  <div className="stat-item">
                    <span className="stat-value">{products.length}</span>
                    <span className="stat-label">상품</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-value">356</span>
                    <span className="stat-label">농가</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-value">2,547kg</span>
                    <span className="stat-label">탄소 절감</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 네비게이션 버튼 */}
        <button className="carousel-btn carousel-btn-prev" onClick={prevSlide}>
          ❮
        </button>
        <button className="carousel-btn carousel-btn-next" onClick={nextSlide}>
          ❯
        </button>

        {/* 인디케이터 */}
        <div className="carousel-indicators">
          {bannerSlides.map((_, index) => (
            <button
              key={index}
              className={`indicator ${index === currentSlide ? 'active' : ''}`}
              onClick={() => goToSlide(index)}
            />
          ))}
        </div>
      </div>

      {/* 카테고리 네비게이션 */}
      <div className="category-nav-wrapper">
        <div className="category-nav">
          <button
            className={`category-nav-item ${!filters.category ? 'active' : ''}`}
            onClick={() => setFilters({...filters, category: '', subCategory: ''})}
          >
            전체
          </button>
          <button className="category-nav-item">AI추천</button>
          <button className="category-nav-item special">상생페이백🌟</button>
          <button className="category-nav-item">베스트</button>
          <button className="category-nav-item">특가</button>
          <button className="category-nav-item">이달의 맛</button>
          {Object.keys(categories).map(cat => (
            <button
              key={cat}
              className={`category-nav-item ${filters.category === cat ? 'active' : ''}`}
              onClick={() => setFilters({...filters, category: cat, subCategory: ''})}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="marketplace-container">
        {/* 사이드바 필터 */}
        <aside className="marketplace-sidebar">
          <div className="filter-section">
            <div className="filter-header">
              <h3>🔍 필터</h3>
              <button className="btn-reset-filters" onClick={resetFilters}>초기화</button>
            </div>

            {/* 카테고리 */}
            <div className="filter-group">
              <h4>카테고리</h4>
              <select
                value={filters.category}
                onChange={(e) => setFilters({...filters, category: e.target.value, subCategory: ''})}
                className="filter-select"
              >
                <option value="">전체</option>
                {Object.keys(categories).map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* 세부 카테고리 */}
            {filters.category && (
              <div className="filter-group">
                <h4>세부 품목</h4>
                <select
                  value={filters.subCategory}
                  onChange={(e) => setFilters({...filters, subCategory: e.target.value})}
                  className="filter-select"
                >
                  <option value="">전체</option>
                  {categories[filters.category].map(item => (
                    <option key={item} value={item}>{item}</option>
                  ))}
                </select>
              </div>
            )}

            {/* 지역 */}
            <div className="filter-group">
              <h4>지역</h4>
              <select
                value={filters.location}
                onChange={(e) => setFilters({...filters, location: e.target.value})}
                className="filter-select"
              >
                <option value="">전체 지역</option>
                <option value="경기">경기</option>
                <option value="강원">강원</option>
                <option value="충남">충남</option>
                <option value="충북">충북</option>
                <option value="전남">전남</option>
                <option value="전북">전북</option>
                <option value="경남">경남</option>
                <option value="경북">경북</option>
                <option value="제주">제주</option>
              </select>
            </div>

            {/* 인증 */}
            <div className="filter-group">
              <h4>인증</h4>
              <select
                value={filters.certification}
                onChange={(e) => setFilters({...filters, certification: e.target.value})}
                className="filter-select"
              >
                <option value="">전체</option>
                <option value="유기농">유기농</option>
                <option value="무농약">무농약</option>
                <option value="친환경">친환경</option>
                <option value="GAP인증">GAP인증</option>
              </select>
            </div>

            {/* 가격대 */}
            <div className="filter-group">
              <h4>가격대</h4>
              <select
                value={filters.priceRange}
                onChange={(e) => setFilters({...filters, priceRange: e.target.value})}
                className="filter-select"
              >
                <option value="">전체</option>
                <option value="0-5000">5천원 이하</option>
                <option value="5000-10000">5천원 ~ 1만원</option>
                <option value="10000-20000">1만원 ~ 2만원</option>
                <option value="20000-50000">2만원 ~ 5만원</option>
                <option value="50000-999999">5만원 이상</option>
              </select>
            </div>
          </div>

          {/* 탄소 절감 정보 */}
          <div className="carbon-info-box">
            <h4>🌱 지역 농산물 선택하면</h4>
            <p>평균 <strong>{(filteredProducts.reduce((sum, p) => sum + parseFloat(p.carbon_footprint), 0) / Math.max(filteredProducts.length, 1)).toFixed(1)}kg</strong> CO₂ 절감</p>
            <p className="carbon-desc">장거리 운송을 줄여 탄소 배출을 감소시킵니다</p>
          </div>
        </aside>

        {/* 메인 컨텐츠 */}
        <main className="marketplace-main">
          {/* 검색 및 정렬 */}
          <div className="marketplace-controls">
            <div className="search-box">
              <input
                type="text"
                placeholder="상품명, 농가명으로 검색..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="search-input"
              />
              <span className="search-icon">🔍</span>
            </div>

            <div className="controls-right">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="popular">인기순</option>
                <option value="newest">최신순</option>
                <option value="price_low">낮은 가격순</option>
                <option value="price_high">높은 가격순</option>
                <option value="distance">가까운 순</option>
                <option value="eco_friendly">친환경순</option>
              </select>

              <div className="view-mode-toggle">
                <button
                  className={viewMode === 'grid' ? 'active' : ''}
                  onClick={() => setViewMode('grid')}
                  title="그리드 뷰"
                >
                  ⊞
                </button>
                <button
                  className={viewMode === 'list' ? 'active' : ''}
                  onClick={() => setViewMode('list')}
                  title="리스트 뷰"
                >
                  ☰
                </button>
              </div>
            </div>
          </div>

          {/* 상품 개수 */}
          <div className="products-count">
            총 <strong>{filteredProducts.length}</strong>개 상품
          </div>

          {/* 상품 목록 */}
          <div className={`products-grid ${viewMode}`}>
            {filteredProducts.length === 0 ? (
              <div className="no-products">
                <p>검색 결과가 없습니다.</p>
                <button onClick={resetFilters} className="btn-reset">필터 초기화</button>
              </div>
            ) : (
              filteredProducts.map(product => (
                <div key={product.product_id} className="product-card">
                  {/* 배지 */}
                  {product.badge && (
                    <div className={`product-badge badge-${product.badge}`}>
                      {product.badge === 'best' && '⭐ BEST'}
                      {product.badge === 'new' && '🆕 NEW'}
                      {product.badge === 'hot' && '🔥 HOT'}
                      {product.badge === 'premium' && '👑 PREMIUM'}
                    </div>
                  )}

                  {/* 할인율 */}
                  {product.discount > 0 && (
                    <div className="product-discount">{product.discount}%</div>
                  )}

                  {/* 상품 이미지 */}
                  <div className="product-image-container">
                    <img src={product.image} alt={product.name} className="product-image" />
                    <button
                      className={`btn-like ${product.liked ? 'liked' : ''}`}
                      onClick={() => toggleLike(product.product_id)}
                    >
                      {product.liked ? '❤️' : '🤍'}
                    </button>
                  </div>

                  {/* 상품 정보 */}
                  <div className="product-info">
                    <div className="product-category">{product.category}</div>
                    <h3 className="product-name">{product.name}</h3>
                    <p className="product-description">{product.description}</p>

                    {/* 농부 정보 */}
                    <div className="farmer-info">
                      <img src={product.farmer_photo} alt={product.farmer_name} className="farmer-photo" />
                      <div className="farmer-details">
                        <div className="farmer-name">{product.farmer_name}</div>
                        <div className="farmer-location">📍 {product.location}</div>
                      </div>
                    </div>

                    {/* 인증 및 탄소 */}
                    <div className="product-badges-row">
                      <span className="cert-badge">{product.certifications}</span>
                      <span className="carbon-badge">🌱 -{product.carbon_footprint}kg CO₂</span>
                    </div>

                    {/* 평점 및 리뷰 */}
                    <div className="product-rating">
                      <span className="rating-stars">⭐ {product.rating}</span>
                      <span className="rating-count">({product.reviews})</span>
                      <span className="likes-count">❤️ {product.likes}</span>
                    </div>

                    {/* 가격 */}
                    <div className="product-price-section">
                      {product.discount > 0 ? (
                        <>
                          <span className="price-original">{product.price_per_kg.toLocaleString()}원</span>
                          <span className="price-discounted">
                            {Math.floor(product.price_per_kg * (100 - product.discount) / 100).toLocaleString()}원
                          </span>
                        </>
                      ) : (
                        <span className="price-current">{product.price_per_kg.toLocaleString()}원</span>
                      )}
                      <span className="price-unit">/kg</span>
                    </div>

                    {/* 재고 */}
                    <div className="product-stock">
                      재고: {product.available_quantity}kg
                    </div>

                    {/* 장바구니 버튼 */}
                    <button
                      className="btn-add-cart"
                      onClick={() => addToCart(product)}
                    >
                      🛒 장바구니 담기
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </main>
      </div>

      {/* 장바구니 버튼 */}
      <button
        className="floating-cart-btn"
        onClick={() => setCartOpen(true)}
      >
        🛒
        {cart.length > 0 && <span className="cart-count">{cart.length}</span>}
      </button>

      {/* 장바구니 모달 */}
      {cartOpen && (
        <div className="cart-modal-overlay" onClick={() => setCartOpen(false)}>
          <div className="cart-modal" onClick={(e) => e.stopPropagation()}>
            <div className="cart-header">
              <h2>🛒 장바구니</h2>
              <button className="btn-close-cart" onClick={() => setCartOpen(false)}>✕</button>
            </div>

            <div className="cart-content">
              {cart.length === 0 ? (
                <div className="cart-empty">
                  <p>장바구니가 비어있습니다</p>
                </div>
              ) : (
                <>
                  <div className="cart-items">
                    {cart.map(item => (
                      <div key={item.product_id} className="cart-item">
                        <img src={item.image} alt={item.name} className="cart-item-image" />
                        <div className="cart-item-info">
                          <h4>{item.name}</h4>
                          <p>{item.price_per_kg.toLocaleString()}원/kg</p>
                          <div className="cart-item-quantity">
                            <button onClick={() => updateQuantity(item.product_id, -1)}>-</button>
                            <span>{item.quantity}kg</span>
                            <button onClick={() => updateQuantity(item.product_id, 1)}>+</button>
                          </div>
                        </div>
                        <div className="cart-item-price">
                          {(item.price_per_kg * item.quantity).toLocaleString()}원
                        </div>
                        <button
                          className="btn-remove-item"
                          onClick={() => removeFromCart(item.product_id)}
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="cart-summary">
                    <div className="summary-row">
                      <span>총 상품 금액</span>
                      <span>{cart.reduce((sum, item) => sum + (item.price_per_kg * item.quantity), 0).toLocaleString()}원</span>
                    </div>
                    <div className="summary-row carbon-summary">
                      <span>🌱 탄소 절감</span>
                      <span>{cart.reduce((sum, item) => sum + (parseFloat(item.carbon_footprint) * item.quantity), 0).toFixed(1)}kg CO₂</span>
                    </div>

                    <div className="payment-method-selector">
                      <label>
                        <input
                          type="radio"
                          value="cash"
                          checked={paymentMethod === 'cash'}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                        />
                        일반 결제
                      </label>
                      <label>
                        <input
                          type="radio"
                          value="token"
                          checked={paymentMethod === 'token'}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                        />
                        🪙 ESG-GOLD 결제
                      </label>
                    </div>

                    <button
                      className="btn-checkout"
                      onClick={handleCheckout}
                      disabled={paying}
                    >
                      {paying ? '처리중...' : '결제하기'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MarketplacePage;
