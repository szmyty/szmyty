/**
 * Progressive enhancement — no framework, no runtime API calls.
 *
 * This script adds:
 *   1. Light/dark theme toggle with localStorage persistence.
 *   2. Active navigation link highlighting based on scroll position.
 *
 * The page must be fully usable without JavaScript.
 */

(function () {
  "use strict";

  // ── 1. Theme toggle ────────────────────────────────────────────────────────

  const THEME_KEY = "site-theme";
  const html = document.documentElement;
  const themeButton = document.getElementById("theme-toggle");

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (_) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_) {
      // Storage unavailable — silently ignore.
    }
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      html.setAttribute("data-theme", "dark");
    } else if (theme === "light") {
      html.setAttribute("data-theme", "light");
    } else {
      html.removeAttribute("data-theme");
    }
    if (themeButton) {
      themeButton.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      themeButton.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light theme" : "Switch to dark theme"
      );
    }
  }

  // Apply stored preference on load (before first paint where possible).
  const storedTheme = getStoredTheme();
  if (storedTheme) {
    applyTheme(storedTheme);
  }

  if (themeButton) {
    themeButton.addEventListener("click", function () {
      const current = html.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      setStoredTheme(next);
    });
  }

  // ── 2. Active nav link on scroll ───────────────────────────────────────────

  var sections = document.querySelectorAll("section[id]");
  var navLinks = document.querySelectorAll("header nav a[href^='#']");

  if (sections.length > 0 && navLinks.length > 0 && "IntersectionObserver" in window) {
    var activeId = null;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            activeId = entry.target.id;
            navLinks.forEach(function (link) {
              var isActive = link.getAttribute("href") === "#" + activeId;
              if (isActive) {
                link.setAttribute("aria-current", "true");
              } else {
                link.removeAttribute("aria-current");
              }
            });
          }
        });
      },
      { rootMargin: "0px 0px -60% 0px", threshold: 0 }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }
})();
