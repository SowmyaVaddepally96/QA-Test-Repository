package com.babyshop.catalog;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ProductService {
    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> listProducts(Optional<String> q) {
        if (q.isPresent() && !q.get().isBlank()) {
            return productRepository.search(q.get().trim());
        }
        return productRepository.findAllByOrderByNameAsc();
    }

    public Product getById(long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Product not found: " + id));
    }
}

