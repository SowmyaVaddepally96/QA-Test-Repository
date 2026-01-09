package com.babyshop.cart;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.context.annotation.SessionScope;

@Configuration
public class CartConfig {

    @Bean
    @SessionScope
    public Cart cart() {
        return new Cart();
    }
}

