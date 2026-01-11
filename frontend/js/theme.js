/**
 * ICH Detection System - Theme Manager
 * File: frontend/js/theme.js
 * Handles dark/light mode switching with localStorage persistence
 */

class ThemeManager {
  constructor() {
    this.themeToggle = document.getElementById("theme-toggle");
    this.themeIcon = document.querySelector(".theme-icon");
    this.currentTheme = this.getStoredTheme();

    this.init();
  }

  /**
   * Initialize theme manager
   */
  init() {
    // Apply stored theme immediately
    this.applyTheme(this.currentTheme);

    // Setup toggle button event listener
    if (this.themeToggle) {
      this.themeToggle.addEventListener("click", () => this.toggleTheme());
    }

    // Listen to system theme changes
    if (window.matchMedia) {
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", (e) => {
          // Only auto-switch if user hasn't manually set a preference
          if (!localStorage.getItem("theme")) {
            this.applyTheme(e.matches ? "dark" : "light");
          }
        });
    }
  }

  /**
   * Get stored theme preference
   * Priority: localStorage > system preference > default (light)
   */
  getStoredTheme() {
    // Check localStorage first
    const stored = localStorage.getItem("theme");
    if (stored) {
      return stored;
    }

    // Check system preference
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      return "dark";
    }

    // Default to light
    return "light";
  }

  /**
   * Apply theme to document
   */
  applyTheme(theme) {
    // Set data attribute on html element
    document.documentElement.setAttribute("data-theme", theme);

    // Update current theme
    this.currentTheme = theme;

    // Update icon
    this.updateIcon(theme);

    // Store in localStorage
    localStorage.setItem("theme", theme);

    console.log(`Theme applied: ${theme}`);
  }

  /**
   * Update theme toggle icon
   */
  updateIcon(theme) {
    if (this.themeIcon) {
      // Dark mode shows sun icon (to switch to light)
      // Light mode shows moon icon (to switch to dark)
      this.themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
  }

  /**
   * Toggle between light and dark themes
   */
  toggleTheme() {
    const newTheme = this.currentTheme === "light" ? "dark" : "light";
    this.applyTheme(newTheme);

    // Add smooth transition
    document.body.style.transition =
      "background-color 0.3s ease, color 0.3s ease";

    // Log for debugging
    console.log(`Theme toggled to: ${newTheme}`);
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return this.currentTheme;
  }
}

// Initialize theme manager when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.themeManager = new ThemeManager();
  console.log("Theme manager initialized");
});
