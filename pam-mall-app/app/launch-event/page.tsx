'use client'

import React, { useEffect, useState } from "react"
import {
  ShoppingCart,
  Sparkles,
  Tag,
  Check,
  X,
  ArrowLeft,
  Zap,
  Gift,
  Timer
} from "lucide-react"
import Link from "next/link"

// API 엔드포인트
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001/api/mall"

// 타입 정의
interface Product {
  product_id: string
  name: string
  category: string
  price: number
  stock: number
  description: string
  image_url: string
  farm_id?: string
}

interface CartItem extends Product {
  quantity: number
}

// 공통 컨테이너
const Container = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`mx-auto w-full max-w-[1200px] px-4 sm:px-6 lg:px-8 ${className}`}>{children}</div>
)

// 특가 상품 카드
const LaunchSpecialCard = ({ product, onAddToCart }: { product: Product; onAddToCart: (p: Product) => void }) => {
  const originalPrice = product.description.match(/원가 ([\d,]+)원/)?.[1]?.replace(/,/g, '') || '3000'
  const discount = Math.round((1 - product.price / parseInt(originalPrice)) * 100)

  return (
    <article className="rounded-2xl border-2 border-red-300 bg-gradient-to-br from-red-50 to-orange-50 p-6 shadow-lg hover:shadow-xl transition-all relative overflow-hidden">
      {/* 할인율 배지 */}
      <div className="absolute top-0 right-0 bg-red-600 text-white px-4 py-2 rounded-bl-2xl font-bold text-lg">
        {discount}% OFF
      </div>

      {/* 품절 임박 배지 */}
      {product.stock < 20 && (
        <div className="absolute top-2 left-2 bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">
          품절임박
        </div>
      )}

      <div className="aspect-square bg-white rounded-xl mb-4 overflow-hidden mt-8">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              // 이미지 로드 실패 시 폴백
              e.currentTarget.style.display = 'none'
              e.currentTarget.parentElement!.classList.add('flex', 'items-center', 'justify-center')
              const fallback = document.createElement('div')
              fallback.innerHTML = `<svg class="w-20 h-20 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>`
              e.currentTarget.parentElement!.appendChild(fallback)
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Sparkles className="w-20 h-20 text-red-400" />
          </div>
        )}
      </div>

      <h3 className="text-xl font-bold text-gray-900 mb-2">{product.name}</h3>
      <p className="text-sm text-gray-600 mb-3">{product.description}</p>

      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-3xl font-bold text-red-600">100 DC</span>
            <Gift className="w-6 h-6 text-red-500" />
          </div>
          <div className="text-sm text-gray-500 line-through">
            원가: {parseInt(originalPrice).toLocaleString()}원
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">재고</div>
          <div className={`font-bold ${product.stock < 20 ? 'text-red-600' : 'text-emerald-600'}`}>
            {product.stock}개
          </div>
        </div>
      </div>

      <button
        onClick={() => onAddToCart(product)}
        disabled={product.stock === 0}
        className={`w-full rounded-full px-4 py-3 text-white font-bold transition-colors flex items-center justify-center gap-2 ${
          product.stock === 0
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700'
        }`}
      >
        <ShoppingCart className="w-5 h-5" />
        {product.stock === 0 ? '품절' : '100DC로 구매하기'}
      </button>
    </article>
  )
}

export default function LaunchEventPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLaunchProducts()
  }, [])

  const fetchLaunchProducts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/products?category=런칭특가`)
      const data = await response.json()
      if (data.success) {
        setProducts(data.data)
      }
    } catch (error) {
      console.error('특가 상품 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCart = (product: Product) => {
    const existingItem = cart.find(item => item.product_id === product.product_id)
    if (existingItem) {
      setCart(cart.map(item =>
        item.product_id === product.product_id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ))
    } else {
      setCart([...cart, { ...product, quantity: 1 }])
    }
    alert(`${product.name}이(가) 장바구니에 담겼습니다!`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-orange-50">
      {/* 헤더 */}
      <header className="border-b bg-white shadow-sm sticky top-0 z-40">
        <Container className="flex items-center justify-between gap-4 py-3">
          <Link href="/" className="flex items-center gap-2 text-red-600 hover:text-red-700">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-semibold">메인으로</span>
          </Link>
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-red-600" />
            <span className="text-2xl font-extrabold tracking-tight text-red-600">런칭 특가</span>
          </div>
          <Link href="/" className="flex items-center gap-2 text-emerald-600 hover:text-emerald-700">
            <ShoppingCart className="w-5 h-5" />
            {cart.length > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </Link>
        </Container>
      </header>

      {/* 이벤트 히어로 배너 */}
      <section className="bg-gradient-to-r from-red-600 via-orange-600 to-red-600 text-white py-16">
        <Container>
          <div className="text-center">
            <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-6 py-2 rounded-full mb-4">
              <Timer className="w-5 h-5" />
              <span className="font-semibold">🔥 기간 한정 특가 🔥</span>
            </div>

            <h1 className="text-5xl font-extrabold mb-4">
              팜몰 런칭 기념 특가
            </h1>
            <p className="text-2xl mb-6 font-semibold">
              모든 상품 단돈 100DC!
            </p>
            <div className="flex items-center justify-center gap-8 text-lg">
              <div className="flex items-center gap-2">
                <Check className="w-6 h-6" />
                <span>신선한 농산물</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-6 h-6" />
                <span>100DC 균일가</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-6 h-6" />
                <span>선착순 한정수량</span>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* 특가 상품 그리드 */}
      <section className="py-12">
        <Container>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              🎉 100DC 특가 상품
            </h2>
            <div className="text-right">
              <div className="text-sm text-gray-600">전체 상품</div>
              <div className="text-2xl font-bold text-red-600">{products.length}개</div>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-red-600 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">특가 상품 불러오는 중...</p>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-2xl">
              <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">특가 상품이 준비 중입니다</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {products.map((product) => (
                <LaunchSpecialCard
                  key={product.product_id}
                  product={product}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          )}
        </Container>
      </section>

      {/* 이벤트 안내 */}
      <section className="bg-white py-12 border-t">
        <Container>
          <div className="max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-center mb-8">이벤트 안내</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-red-50 p-6 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <Tag className="w-6 h-6 text-red-600" />
                  <h4 className="font-bold text-lg">100DC 균일가</h4>
                </div>
                <p className="text-gray-700">
                  런칭특가 카테고리의 모든 상품을 단돈 100DC에 구매하실 수 있습니다.
                </p>
              </div>

              <div className="bg-orange-50 p-6 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <Timer className="w-6 h-6 text-orange-600" />
                  <h4 className="font-bold text-lg">선착순 한정</h4>
                </div>
                <p className="text-gray-700">
                  재고 소진 시 조기 종료될 수 있으니 서두르세요!
                </p>
              </div>

              <div className="bg-emerald-50 p-6 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <Gift className="w-6 h-6 text-emerald-600" />
                  <h4 className="font-bold text-lg">신규 가입 혜택</h4>
                </div>
                <p className="text-gray-700">
                  지금 가입하면 100DC 무료 지급! 바로 특가 상품을 구매하세요.
                </p>
              </div>

              <div className="bg-blue-50 p-6 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                  <h4 className="font-bold text-lg">블록체인 보장</h4>
                </div>
                <p className="text-gray-700">
                  Algorand 블록체인 기반으로 안전하고 투명한 거래를 보장합니다.
                </p>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA 섹션 */}
      <section className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-12">
        <Container>
          <div className="text-center">
            <h3 className="text-3xl font-bold mb-4">지금 바로 특가 상품을 만나보세요!</h3>
            <Link
              href="/"
              className="inline-flex items-center gap-2 bg-white text-red-600 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition-colors"
            >
              <ShoppingCart className="w-6 h-6" />
              메인으로 돌아가기
            </Link>
          </div>
        </Container>
      </section>
    </div>
  )
}
