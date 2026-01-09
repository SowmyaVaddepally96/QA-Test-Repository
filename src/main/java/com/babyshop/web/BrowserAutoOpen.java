package com.babyshop.web;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.boot.web.context.WebServerInitializedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import java.awt.Desktop;
import java.io.IOException;
import java.net.URI;
import java.util.Locale;

@Component
public class BrowserAutoOpen {

    private volatile int localPort = 8080;

    @Value("${app.open-browser:false}")
    private boolean openBrowser;

    @Value("${app.open-browser-path:/products}")
    private String path;

    @EventListener
    public void onWebServerReady(WebServerInitializedEvent event) {
        this.localPort = event.getWebServer().getPort();
    }

    @EventListener
    public void onAppReady(ApplicationReadyEvent event) {
        if (!openBrowser) {
            return;
        }

        String normalizedPath = (path == null || path.isBlank()) ? "/" : path.trim();
        if (!normalizedPath.startsWith("/")) {
            normalizedPath = "/" + normalizedPath;
        }

        URI url = URI.create("http://localhost:" + localPort + normalizedPath);

        // Try Java Desktop first.
        try {
            if (Desktop.isDesktopSupported()) {
                Desktop.getDesktop().browse(url);
                return;
            }
        } catch (Exception ignored) {
            // fall through
        }

        // Fall back to OS-specific commands.
        try {
            openWithCommand(url.toString());
        } catch (IOException ignored) {
            // If we can't open a browser (e.g., headless environment), we silently ignore.
        }
    }

    private static void openWithCommand(String url) throws IOException {
        String os = System.getProperty("os.name", "").toLowerCase(Locale.ROOT);
        if (os.contains("mac")) {
            new ProcessBuilder("open", url).start();
            return;
        }
        if (os.contains("win")) {
            new ProcessBuilder("cmd", "/c", "start", url).start();
            return;
        }
        // Linux / others
        new ProcessBuilder("xdg-open", url).start();
    }
}

