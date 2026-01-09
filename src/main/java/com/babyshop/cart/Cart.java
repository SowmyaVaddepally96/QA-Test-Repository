package com.babyshop.cart;

import com.babyshop.catalog.Product;

import java.math.BigDecimal;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;

public class Cart {
    private final Map<Long, CartItem> itemsByProductId = new LinkedHashMap<>();

    public void add(Product product, int quantity) {
        int qty = Math.max(1, quantity);
        CartItem existing = itemsByProductId.get(product.getId());
        if (existing == null) {
            itemsByProductId.put(product.getId(), new CartItem(product, qty));
        } else {
            existing.setQuantity(existing.getQuantity() + qty);
        }
    }

    public void setQuantity(long productId, int quantity) {
        if (quantity <= 0) {
            itemsByProductId.remove(productId);
            return;
        }
        CartItem item = itemsByProductId.get(productId);
        if (item != null) {
            item.setQuantity(quantity);
        }
    }

    public void remove(long productId) {
        itemsByProductId.remove(productId);
    }

    public void clear() {
        itemsByProductId.clear();
    }

    public Collection<CartItem> getItems() {
        return itemsByProductId.values();
    }

    public int getItemCount() {
        return itemsByProductId.values().stream().mapToInt(CartItem::getQuantity).sum();
    }

    public BigDecimal getSubtotal() {
        return itemsByProductId.values().stream()
                .map(CartItem::getLineTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

