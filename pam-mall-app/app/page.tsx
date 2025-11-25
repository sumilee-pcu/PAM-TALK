'use client'

import React, { useEffect, useState } from "react"
import {
  ShoppingCart,
  User,
  LogIn,
  Search,
  Gift,
  Store,
  Sparkles,
  Moon,
  Sun,
  Wallet,
  Tag,
  Check,
  X,
  MessageCircle,
  Users
} from "lucide-react"
import Link from "next/link"

// API 엔드포인트 - 환경변수로 설정 가능
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

interface Coupon {
  coupon_id: string
  name: string
  discount_type: 'percentage' | 'fixed'
  discount_value: number
  valid_from: string
  valid_until: string
  usage_limit: number
  used_count: number
  product_ids: string[]
}

interface CartItem extends Product {
  quantity: number
}

// 공통 컨테이너
const Container = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`mx-auto w-full max-w-[1200px] px-4 sm:px-6 lg:px-8 ${className}`}>{children}</div>
)

// 다크모드 훅
function useDarkMode() {
  const [isDark, setIsDark] = useState(false)
  useEffect(() => {
    const stored = localStorage.getItem("pam.theme")
    if (stored === "dark") setIsDark(true)
  }, [])
  useEffect(() => {
    const root = document.documentElement
    if (isDark) {
      root.classList.add("dark")
      localStorage.setItem("pam.theme", "dark")
    } else {
      root.classList.remove("dark")
      localStorage.setItem("pam.theme", "light")
    }
  }, [isDark])
  return { isDark, setIsDark }
}

// 상품 카드 컴포넌트
const ProductCard = ({ product, onAddToCart }: { product: Product; onAddToCart: (p: Product) => void }) => (
  <article className="rounded-2xl border bg-white p-6 shadow-sm hover:shadow-md transition-shadow dark:bg-neutral-900 dark:border-neutral-800">
    <div className="aspect-square bg-emerald-50 rounded-xl mb-4 flex items-center justify-center dark:bg-neutral-800">
      <Store className="w-16 h-16 text-emerald-300 dark:text-emerald-700" />
    </div>
    <h3 className="text-lg font-bold text-emerald-900 mb-2 dark:text-neutral-100">{product.name}</h3>
    <p className="text-sm text-emerald-900/70 mb-3 dark:text-neutral-300">{product.description}</p>
    <div className="flex items-center justify-between mb-4">
      <span className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">{product.price.toLocaleString()}원</span>
      <span className="text-sm text-emerald-600 dark:text-neutral-400">재고: {product.stock}</span>
    </div>
    <button
      onClick={() => onAddToCart(product)}
      className="w-full rounded-full bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700 transition-colors flex items-center justify-center gap-2"
    >
      <ShoppingCart className="w-4 h-4" />
      장바구니 담기
    </button>
  </article>
)

// 쿠폰 카드 컴포넌트
const CouponCard = ({ coupon, onSelect, isSelected }: { coupon: Coupon; onSelect: (c: Coupon) => void; isSelected: boolean }) => {
  const isValid = new Date(coupon.valid_until) > new Date() && coupon.used_count < coupon.usage_limit

  return (
    <div
      onClick={() => isValid && onSelect(coupon)}
      className={`rounded-xl border p-4 cursor-pointer transition-all ${
        isSelected
          ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
          : isValid
          ? 'border-emerald-200 hover:border-emerald-400 dark:border-neutral-700 dark:hover:border-emerald-600'
          : 'border-gray-300 bg-gray-50 opacity-50 cursor-not-allowed dark:bg-neutral-800'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Gift className={`w-5 h-5 ${isValid ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-400'}`} />
          <h4 className="font-bold text-emerald-900 dark:text-neutral-100">{coupon.name}</h4>
        </div>
        {isSelected && <Check className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />}
      </div>
      <p className="text-sm text-emerald-900/70 mb-2 dark:text-neutral-300">
        {coupon.discount_type === 'percentage'
          ? `${coupon.discount_value}% 할인`
          : `${coupon.discount_value.toLocaleString()}원 할인`}
      </p>
      <p className="text-xs text-emerald-600 dark:text-neutral-400">
        {new Date(coupon.valid_until).toLocaleDateString()} 까지
      </p>
    </div>
  )
}

// 장바구니 모달
const CartModal = ({
  isOpen,
  onClose,
  cartItems,
  onRemoveItem,
  onCheckout,
  userAddress
}: {
  isOpen: boolean
  onClose: () => void
  cartItems: CartItem[]
  onRemoveItem: (index: number) => void
  onCheckout: (coupon: Coupon | null) => void
  userAddress: string
}) => {
  const [selectedCoupon, setSelectedCoupon] = useState<Coupon | null>(null)
  const [coupons, setCoupons] = useState<Coupon[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && userAddress) {
      fetchUserCoupons()
    }
  }, [isOpen, userAddress])

  const fetchUserCoupons = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/${userAddress}/coupons`)
      const data = await response.json()
      if (data.success) {
        setCoupons(data.data)
      }
    } catch (error) {
      console.error('쿠폰 조회 실패:', error)
    }
  }

  const totalAmount = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)

  let discountAmount = 0
  if (selectedCoupon) {
    if (selectedCoupon.discount_type === 'percentage') {
      discountAmount = totalAmount * (selectedCoupon.discount_value / 100)
    } else {
      discountAmount = Math.min(selectedCoupon.discount_value, totalAmount)
    }
  }

  const finalAmount = totalAmount - discountAmount

  const handleCheckout = () => {
    onCheckout(selectedCoupon)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-neutral-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-neutral-900 p-6 border-b dark:border-neutral-800 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-emerald-900 dark:text-neutral-100">장바구니</h2>
          <button onClick={onClose} className="p-2 hover:bg-emerald-50 rounded-full dark:hover:bg-neutral-800">
            <X className="w-6 h-6 text-emerald-700 dark:text-neutral-300" />
          </button>
        </div>

        <div className="p-6">
          {/* 장바구니 아이템 */}
          <div className="mb-6">
            <h3 className="font-bold text-lg mb-4 text-emerald-900 dark:text-neutral-100">주문 상품</h3>
            {cartItems.length === 0 ? (
              <p className="text-center py-8 text-emerald-900/70 dark:text-neutral-400">장바구니가 비어있습니다</p>
            ) : (
              <div className="space-y-3">
                {cartItems.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-emerald-50 rounded-xl dark:bg-neutral-800">
                    <div className="flex-1">
                      <h4 className="font-semibold text-emerald-900 dark:text-neutral-100">{item.name}</h4>
                      <p className="text-sm text-emerald-700 dark:text-neutral-300">{item.price.toLocaleString()}원 x {item.quantity}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-bold text-emerald-900 dark:text-neutral-100">{(item.price * item.quantity).toLocaleString()}원</span>
                      <button
                        onClick={() => onRemoveItem(index)}
                        className="p-2 hover:bg-red-100 rounded-full dark:hover:bg-red-900/20"
                      >
                        <X className="w-4 h-4 text-red-600 dark:text-red-400" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 쿠폰 선택 */}
          {cartItems.length > 0 && (
            <div className="mb-6">
              <h3 className="font-bold text-lg mb-4 text-emerald-900 dark:text-neutral-100 flex items-center gap-2">
                <Tag className="w-5 h-5" />
                디지털 쿠폰
              </h3>
              {coupons.length === 0 ? (
                <p className="text-sm text-emerald-900/70 dark:text-neutral-400">사용 가능한 쿠폰이 없습니다</p>
              ) : (
                <div className="grid gap-3 md:grid-cols-2">
                  {coupons.map((coupon) => (
                    <CouponCard
                      key={coupon.coupon_id}
                      coupon={coupon}
                      onSelect={setSelectedCoupon}
                      isSelected={selectedCoupon?.coupon_id === coupon.coupon_id}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 결제 금액 */}
          {cartItems.length > 0 && (
            <div className="border-t dark:border-neutral-700 pt-4 space-y-2">
              <div className="flex justify-between text-emerald-900 dark:text-neutral-300">
                <span>상품 금액</span>
                <span>{totalAmount.toLocaleString()}원</span>
              </div>
              {selectedCoupon && (
                <div className="flex justify-between text-emerald-600 dark:text-emerald-400">
                  <span>쿠폰 할인</span>
                  <span>-{discountAmount.toLocaleString()}원</span>
                </div>
              )}
              <div className="flex justify-between text-xl font-bold text-emerald-900 dark:text-neutral-100 pt-2 border-t dark:border-neutral-700">
                <span>최종 결제 금액</span>
                <span>{finalAmount.toLocaleString()}원</span>
              </div>
              <button
                onClick={handleCheckout}
                disabled={loading}
                className="w-full mt-4 rounded-full bg-emerald-600 px-6 py-3 text-white font-bold hover:bg-emerald-700 transition-colors flex items-center justify-center gap-2 disabled:bg-gray-400"
              >
                <Wallet className="w-5 h-5" />
                {loading ? '처리 중...' : '디지털 쿠폰으로 결제하기'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// 메인 앱
export default function PamMallApp() {
  const { isDark, setIsDark } = useDarkMode()
  const [products, setProducts] = useState<Product[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [cartOpen, setCartOpen] = useState(false)
  const [userAddress, setUserAddress] = useState("USER_WALLET_ADDRESS_123")
  const [orderComplete, setOrderComplete] = useState(false)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`)
      const data = await response.json()
      if (data.success) {
        setProducts(data.data)
      }
    } catch (error) {
      console.error('상품 조회 실패:', error)
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
  }

  const handleRemoveFromCart = (index: number) => {
    setCart(cart.filter((_, i) => i !== index))
  }

  const handleCheckout = async (selectedCoupon: Coupon | null) => {
    try {
      const orderData = {
        user_address: userAddress,
        items: cart.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        })),
        coupon_id: selectedCoupon?.coupon_id,
        payment_txid: `ALGO_TX_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      }

      const response = await fetch(`${API_BASE_URL}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
      })

      const data = await response.json()

      if (data.success) {
        setOrderComplete(true)
        setCart([])
        setCartOpen(false)
        setTimeout(() => setOrderComplete(false), 3000)
      } else {
        alert('주문 실패: ' + (data.error?.message || '알 수 없는 오류'))
      }
    } catch (error) {
      console.error('주문 실패:', error)
      alert('주문 처리 중 오류가 발생했습니다')
    }
  }

  return (
    <div className="min-h-screen bg-white text-emerald-900 dark:bg-neutral-900 dark:text-neutral-100">
      {/* 헤더 */}
      <header className="border-b bg-white dark:bg-neutral-900 dark:border-neutral-800 sticky top-0 z-40">
        <Container className="flex items-center justify-between gap-4 py-3">
          <a href="#" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-emerald-600 dark:bg-emerald-500"></div>
            <span className="text-2xl font-extrabold tracking-tight text-emerald-700 dark:text-emerald-400">PAM MALL</span>
          </a>

          <nav className="flex items-center gap-4">
            <Link href="/community" className="flex items-center gap-1 text-emerald-800 hover:text-emerald-600 dark:text-neutral-200">
              <Users className="w-5 h-5" />
              <span className="hidden sm:inline">커뮤니티</span>
            </Link>
            <Link href="/chat" className="flex items-center gap-1 text-emerald-800 hover:text-emerald-600 dark:text-neutral-200">
              <MessageCircle className="w-5 h-5" />
              <span className="hidden sm:inline">채팅</span>
            </Link>
            <button onClick={() => setIsDark(!isDark)} className="flex items-center gap-1 text-emerald-800 hover:text-emerald-600 dark:text-neutral-200">
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setCartOpen(true)}
              className="flex items-center gap-1 text-emerald-800 hover:text-emerald-600 dark:text-neutral-200 relative"
            >
              <ShoppingCart className="w-5 h-5" />
              {cart.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {cart.length}
                </span>
              )}
              <span className="hidden sm:inline">장바구니</span>
            </button>
            <button className="flex items-center gap-1 text-emerald-800 hover:text-emerald-600 dark:text-neutral-200">
              <Wallet className="w-5 h-5" />
              <span className="hidden sm:inline">지갑 연결</span>
            </button>
          </nav>
        </Container>
      </header>

      {/* 히어로 섹션 */}
      <section className="bg-gradient-to-r from-emerald-50 to-emerald-100 dark:from-neutral-900 dark:to-neutral-900 py-12">
        <Container>
          <div className="text-center">
            <h1 className="text-4xl font-extrabold mb-4 text-emerald-900 dark:text-neutral-100">
              디지털 쿠폰으로 신선한 농산물 구매
            </h1>
            <p className="text-lg text-emerald-900/80 dark:text-neutral-300 mb-6">
              Algorand 블록체인 기반 투명하고 안전한 거래
            </p>
            <div className="inline-flex items-center gap-2 bg-emerald-600 text-white px-6 py-3 rounded-full">
              <Sparkles className="w-5 h-5" />
              <span>오늘의 특가 상품</span>
            </div>
          </div>
        </Container>
      </section>

      {/* 상품 그리드 */}
      <section className="py-12">
        <Container>
          <h2 className="text-3xl font-bold mb-8 text-emerald-900 dark:text-neutral-100">디지털 쿠폰 사용 가능 상품</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {products.map((product) => (
              <ProductCard
                key={product.product_id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        </Container>
      </section>

      {/* 장바구니 모달 */}
      <CartModal
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cartItems={cart}
        onRemoveItem={handleRemoveFromCart}
        onCheckout={handleCheckout}
        userAddress={userAddress}
      />

      {/* 주문 완료 알림 */}
      {orderComplete && (
        <div className="fixed bottom-4 right-4 bg-emerald-600 text-white px-6 py-4 rounded-xl shadow-lg flex items-center gap-3 z-50">
          <Check className="w-6 h-6" />
          <div>
            <p className="font-bold">주문이 완료되었습니다!</p>
            <p className="text-sm">블록체인에 기록되었습니다</p>
          </div>
        </div>
      )}

      {/* 푸터 */}
      <footer className="border-t bg-emerald-50 dark:bg-neutral-900 dark:border-neutral-800 mt-12">
        <Container className="py-8">
          <div className="text-center text-sm text-emerald-900/70 dark:text-neutral-400">
            <p className="mb-2">© {new Date().getFullYear()} PAM MALL. Powered by Algorand Blockchain.</p>
            <p>디지털 쿠폰으로 안전하고 투명한 거래를 경험하세요</p>
          </div>
        </Container>
      </footer>
    </div>
  )
}
