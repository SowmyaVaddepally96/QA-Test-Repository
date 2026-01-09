package com.babyshop.web;

import com.babyshop.catalog.Product;
import com.babyshop.catalog.ProductService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.Optional;

@Controller
public class CatalogController {
    private final ProductService productService;

    public CatalogController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/products")
    public String products(@RequestParam(name = "q", required = false) String q, Model model) {
        model.addAttribute("q", q == null ? "" : q);
        model.addAttribute("products", productService.listProducts(Optional.ofNullable(q)));
        return "products";
    }

    @GetMapping("/products/{id}")
    public String product(@PathVariable("id") long id, Model model) {
        Product product = productService.getById(id);
        model.addAttribute("product", product);
        return "product";
    }
}

