package com.babyshop.web;

import com.babyshop.cart.Cart;
import com.babyshop.catalog.Product;
import com.babyshop.catalog.ProductService;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class CartController {
    private final Cart cart;
    private final ProductService productService;

    public CartController(Cart cart, ProductService productService) {
        this.cart = cart;
        this.productService = productService;
    }

    @GetMapping("/cart")
    public String cart(Model model) {
        model.addAttribute("cart", cart);
        return "cart";
    }

    @PostMapping("/cart/add")
    public String addToCart(
            @RequestParam("productId") long productId,
            @RequestParam(name = "quantity", defaultValue = "1") @Min(1) @Max(99) int quantity,
            RedirectAttributes redirectAttributes
    ) {
        Product product = productService.getById(productId);
        cart.add(product, quantity);
        redirectAttributes.addFlashAttribute("toast", product.getName() + " added to cart");
        return "redirect:/cart";
    }

    @PostMapping("/cart/update")
    public String updateQuantity(@RequestParam("productId") long productId,
                                 @RequestParam("quantity") @Min(0) @Max(99) int quantity) {
        cart.setQuantity(productId, quantity);
        return "redirect:/cart";
    }

    @PostMapping("/cart/remove")
    public String remove(@RequestParam("productId") long productId) {
        cart.remove(productId);
        return "redirect:/cart";
    }

    @PostMapping("/cart/clear")
    public String clear() {
        cart.clear();
        return "redirect:/cart";
    }
}

