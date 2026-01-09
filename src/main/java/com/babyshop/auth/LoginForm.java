package com.babyshop.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class LoginForm {
    @NotBlank(message = "Username/Email is required")
    @Size(max = 320)
    private String email;

    @NotBlank(message = "Password is required")
    @Size(max = 200)
    private String password;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}

