package com.babyshop.web;

import com.babyshop.cart.Cart;
import com.babyshop.order.CheckoutForm;
import com.babyshop.order.CustomerOrder;
import com.babyshop.order.OrderService;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class CheckoutController {
    private final Cart cart;
    private final OrderService orderService;

    public CheckoutController(Cart cart, OrderService orderService) {
        this.cart = cart;
        this.orderService = orderService;
    }

    @GetMapping("/checkout")
    public String checkout(Model model) {
        if (cart.getItems().isEmpty()) {
            return "redirect:/products";
        }
        if (!model.containsAttribute("checkoutForm")) {
            model.addAttribute("checkoutForm", new CheckoutForm());
        }
        model.addAttribute("cart", cart);
        return "checkout";
    }

    @PostMapping("/checkout")
    public String placeOrder(@Valid @ModelAttribute CheckoutForm checkoutForm,
                             BindingResult bindingResult,
                             Model model,
                             RedirectAttributes redirectAttributes) {
        if (cart.getItems().isEmpty()) {
            return "redirect:/products";
        }
        if (bindingResult.hasErrors()) {
            model.addAttribute("cart", cart);
            return "checkout";
        }

        CustomerOrder order = orderService.placeOrder(checkoutForm, cart);
        cart.clear();
        redirectAttributes.addFlashAttribute("orderId", order.getId());
        return "redirect:/order-confirmation";
    }

    @GetMapping("/order-confirmation")
    public String confirmation(Model model) {
        Object orderId = model.asMap().get("orderId");
        if (orderId == null) {
            return "redirect:/products";
        }
        model.addAttribute("orderId", orderId);
        return "order-confirmation";
    }
}

