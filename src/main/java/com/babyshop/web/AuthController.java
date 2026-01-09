package com.babyshop.web;

import com.babyshop.auth.AuthSession;
import com.babyshop.auth.LoginForm;
import com.babyshop.auth.SignupForm;
import com.babyshop.auth.UserAccount;
import com.babyshop.auth.UserService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.Optional;

@Controller
public class AuthController {
    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/auth")
    public String auth(@RequestParam(name = "mode", required = false, defaultValue = "login") String mode,
                       Model model) {
        String normalizedMode = normalizeMode(mode);
        model.addAttribute("mode", normalizedMode);
        if (!model.containsAttribute("loginForm")) {
            model.addAttribute("loginForm", new LoginForm());
        }
        if (!model.containsAttribute("signupForm")) {
            model.addAttribute("signupForm", new SignupForm());
        }
        return "auth";
    }

    @PostMapping("/auth/login")
    public String login(@Valid @ModelAttribute("loginForm") LoginForm loginForm,
                        BindingResult bindingResult,
                        HttpSession session,
                        RedirectAttributes redirectAttributes,
                        Model model) {
        if (bindingResult.hasErrors()) {
            model.addAttribute("mode", "login");
            return "auth";
        }

        Optional<UserAccount> user = userService.authenticate(loginForm.getEmail(), loginForm.getPassword());
        if (user.isEmpty()) {
            model.addAttribute("mode", "login");
            model.addAttribute("authError", "Invalid credentials");
            return "auth";
        }

        session.setAttribute(AuthSession.USER_ID, user.get().getId());
        session.setAttribute(AuthSession.USER_EMAIL, user.get().getEmail());
        redirectAttributes.addFlashAttribute("toast", "Logged in");
        return "redirect:/products";
    }

    @PostMapping("/auth/signup")
    public String signup(@Valid @ModelAttribute("signupForm") SignupForm signupForm,
                         BindingResult bindingResult,
                         HttpSession session,
                         RedirectAttributes redirectAttributes,
                         Model model) {
        if (!bindingResult.hasErrors()) {
            if (!signupForm.getPassword().equals(signupForm.getConfirmPassword())) {
                bindingResult.rejectValue("confirmPassword", "mismatch", "Passwords do not match");
            }
        }

        if (bindingResult.hasErrors()) {
            model.addAttribute("mode", "signup");
            return "auth";
        }

        try {
            UserAccount created = userService.signup(signupForm.getEmail(), signupForm.getPassword());
            // Auto-login is allowed per acceptance criteria.
            session.setAttribute(AuthSession.USER_ID, created.getId());
            session.setAttribute(AuthSession.USER_EMAIL, created.getEmail());
            redirectAttributes.addFlashAttribute("toast", "Account created");
            return "redirect:/products";
        } catch (IllegalArgumentException ex) {
            model.addAttribute("mode", "signup");
            model.addAttribute("authError", ex.getMessage());
            return "auth";
        }
    }

    @PostMapping("/logout")
    public String logout(HttpSession session, RedirectAttributes redirectAttributes) {
        session.removeAttribute(AuthSession.USER_ID);
        session.removeAttribute(AuthSession.USER_EMAIL);
        redirectAttributes.addFlashAttribute("toast", "Logged out");
        return "redirect:/products";
    }

    private static String normalizeMode(String mode) {
        String m = (mode == null) ? "login" : mode.trim().toLowerCase();
        return (m.equals("signup") || m.equals("sign-up")) ? "signup" : "login";
    }
}

