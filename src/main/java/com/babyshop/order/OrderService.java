package com.babyshop.order;

import com.babyshop.cart.Cart;
import com.babyshop.cart.CartItem;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
public class OrderService {
    private final CustomerOrderRepository customerOrderRepository;

    public OrderService(CustomerOrderRepository customerOrderRepository) {
        this.customerOrderRepository = customerOrderRepository;
    }

    @Transactional
    public CustomerOrder placeOrder(CheckoutForm form, Cart cart) {
        if (cart.getItems().isEmpty()) {
            throw new IllegalStateException("Cart is empty");
        }

        CustomerOrder order = new CustomerOrder(
                Instant.now(),
                form.getFullName().trim(),
                form.getEmail().trim(),
                form.getAddress().trim(),
                form.getCity().trim(),
                form.getPostalCode().trim(),
                cart.getSubtotal()
        );

        for (CartItem cartItem : cart.getItems()) {
            order.addItem(new OrderItem(
                    cartItem.getProduct().getId(),
                    cartItem.getProduct().getName(),
                    cartItem.getProduct().getCategory(),
                    cartItem.getProduct().getPrice(),
                    cartItem.getQuantity()
            ));
        }

        return customerOrderRepository.save(order);
    }
}

