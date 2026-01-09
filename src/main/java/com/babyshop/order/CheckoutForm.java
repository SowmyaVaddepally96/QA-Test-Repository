package com.babyshop.order;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CheckoutForm {
    @NotBlank
    @Size(max = 200)
    private String fullName;

    @NotBlank
    @Email
    @Size(max = 320)
    private String email;

    @NotBlank
    @Size(max = 2000)
    private String address;

    @NotBlank
    @Size(max = 120)
    private String city;

    @NotBlank
    @Size(max = 40)
    private String postalCode;

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getPostalCode() {
        return postalCode;
    }

    public void setPostalCode(String postalCode) {
        this.postalCode = postalCode;
    }
}

