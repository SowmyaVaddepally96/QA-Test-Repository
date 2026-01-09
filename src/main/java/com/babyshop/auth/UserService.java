package com.babyshop.auth;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Optional;

@Service
public class UserService {
    private final UserAccountRepository userAccountRepository;
    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public UserService(UserAccountRepository userAccountRepository) {
        this.userAccountRepository = userAccountRepository;
    }

    public Optional<UserAccount> authenticate(String email, String rawPassword) {
        if (email == null || rawPassword == null) {
            return Optional.empty();
        }
        return userAccountRepository.findByEmailIgnoreCase(email.trim())
                .filter(u -> passwordEncoder.matches(rawPassword, u.getPasswordHash()));
    }

    @Transactional
    public UserAccount signup(String email, String rawPassword) {
        String normalizedEmail = normalizeEmail(email);
        if (userAccountRepository.existsByEmailIgnoreCase(normalizedEmail)) {
            throw new IllegalArgumentException("An account with this email already exists");
        }
        String hash = passwordEncoder.encode(rawPassword);
        return userAccountRepository.save(new UserAccount(normalizedEmail, hash, Instant.now()));
    }

    private static String normalizeEmail(String email) {
        if (email == null) {
            throw new IllegalArgumentException("Email is required");
        }
        String trimmed = email.trim();
        if (trimmed.isBlank()) {
            throw new IllegalArgumentException("Email is required");
        }
        return trimmed;
    }
}

