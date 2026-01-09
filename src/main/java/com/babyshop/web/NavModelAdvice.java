package com.babyshop.web;

import com.babyshop.auth.AuthSession;
import com.babyshop.cart.Cart;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

@ControllerAdvice
public class NavModelAdvice {
    private final Cart cart;
    private final HttpSession session;

    public NavModelAdvice(Cart cart, HttpSession session) {
        this.cart = cart;
        this.session = session;
    }

    @ModelAttribute("cartItemCount")
    public int cartItemCount() {
        return cart.getItemCount();
    }

    @ModelAttribute("isLoggedIn")
    public boolean isLoggedIn() {
        return session.getAttribute(AuthSession.USER_ID) != null;
    }

    @ModelAttribute("currentUserEmail")
    public String currentUserEmail() {
        Object email = session.getAttribute(AuthSession.USER_EMAIL);
        return email == null ? "" : String.valueOf(email);
    }
}

