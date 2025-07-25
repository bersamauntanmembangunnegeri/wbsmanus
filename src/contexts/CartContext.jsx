import { createContext, useContext, useState, useEffect } from 'react'

const CartContext = createContext()

export function useCart() {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState([])
  const [loading, setLoading] = useState(false)

  const API_BASE = '/api'

  useEffect(() => {
    fetchCart()
  }, [])

  const fetchCart = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/cart`)
      
      if (response.ok) {
        const data = await response.json()
        setCartItems(data)
      }
    } catch (error) {
      console.error('Error fetching cart:', error)
    } finally {
      setLoading(false)
    }
  }

  const addToCart = async (productId, quantity = 1) => {
    try {
      const response = await fetch(`${API_BASE}/cart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId, quantity })
      })

      if (response.ok) {
        await fetchCart() // Refresh cart
        return { success: true }
      } else {
        const data = await response.json()
        return { success: false, error: data.error }
      }
    } catch (error) {
      return { success: false, error: 'Network error' }
    }
  }

  const updateCartItem = async (itemId, quantity) => {
    try {
      const response = await fetch(`${API_BASE}/cart/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity })
      })

      if (response.ok) {
        await fetchCart() // Refresh cart
        return { success: true }
      } else {
        const data = await response.json()
        return { success: false, error: data.error }
      }
    } catch (error) {
      return { success: false, error: 'Network error' }
    }
  }

  const removeFromCart = async (itemId) => {
    try {
      const response = await fetch(`${API_BASE}/cart/${itemId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        await fetchCart() // Refresh cart
        return { success: true }
      } else {
        return { success: false, error: 'Failed to remove item' }
      }
    } catch (error) {
      return { success: false, error: 'Network error' }
    }
  }

  const clearCart = async () => {
    try {
      const response = await fetch(`${API_BASE}/cart/clear`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setCartItems([])
        return { success: true }
      } else {
        return { success: false, error: 'Failed to clear cart' }
      }
    } catch (error) {
      return { success: false, error: 'Network error' }
    }
  }

  const getCartTotal = () => {
    return cartItems.reduce((total, item) => {
      return total + (item.product?.price || 0) * item.quantity
    }, 0)
  }

  const getCartItemCount = () => {
    return cartItems.reduce((total, item) => total + item.quantity, 0)
  }

  const value = {
    cartItems,
    loading,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    getCartTotal,
    getCartItemCount,
    refreshCart: fetchCart
  }

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  )
}

