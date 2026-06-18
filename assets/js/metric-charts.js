/**
 * metric-charts.js — Dynamic Chart.js renderer for market health report charts.
 *
 * Initializes Chart.js charts from JSON data embedded in metric_chart shortcodes.
 * Uses IntersectionObserver for lazy initialization so charts only render when
 * scrolled into view, improving page load performance for reports with many charts.
 *
 * Depends on chart.js already present in assets/js/chart.js.
 */

(function () {
  "use strict";

  /**
   * Default chart options shared across all chart types.
   * Supports light and dark mode via CSS media query detection.
   */
  function getDefaultOptions() {
    var isDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    var textColor = isDark ? "#c9d1d9" : "#333";
    var gridColor = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";

    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: textColor, padding: 16 },
        },
        title: {
          display: false,
          color: textColor,
          font: { size: 14, weight: "bold" },
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      elements: {
        point: { radius: 0, hoverRadius: 4 },
        line: { tension: 0.2, borderWidth: 2 },
      },
      scales: {
        x: {
          ticks: {
            color: textColor,
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: 15,
          },
          grid: { color: gridColor },
        },
        y: {
          ticks: { color: textColor },
          grid: { color: gridColor },
        },
      },
    };
  }

  /**
   * Deep merge two objects. Values in `src` override those in `target`.
   */
  function deepMerge(target, src) {
    var result = {};
    var key;
    for (key in target) {
      if (target.hasOwnProperty(key)) {
        result[key] = target[key];
      }
    }
    for (key in src) {
      if (src.hasOwnProperty(key)) {
        if (
          typeof src[key] === "object" &&
          src[key] !== null &&
          !Array.isArray(src[key]) &&
          typeof result[key] === "object" &&
          result[key] !== null &&
          !Array.isArray(result[key])
        ) {
          result[key] = deepMerge(result[key], src[key]);
        } else {
          result[key] = src[key];
        }
      }
    }
    return result;
  }

  /**
   * Initialize a single metric chart from a container element.
   * Reads chart configuration from the data-chart-config attribute.
   */
  function initChart(container) {
    if (container.dataset.chartInitialized === "true") return;

    var canvas = container.querySelector("canvas");
    if (!canvas) return;

    var configStr = container.getAttribute("data-chart-config");
    if (!configStr) return;

    var config;
    try {
      config = JSON.parse(configStr);
    } catch (e) {
      console.error("metric-charts: invalid JSON config for", canvas.id, e);
      return;
    }

    var chartType = config.type || "line";
    var chartData = config.data || {};
    var customOptions = config.options || {};
    var defaults = getDefaultOptions();

    // Merge custom options on top of defaults
    var mergedOptions = deepMerge(defaults, customOptions);

    // If title is provided in config, enable it
    if (config.title) {
      mergedOptions.plugins = mergedOptions.plugins || {};
      mergedOptions.plugins.title = {
        display: true,
        text: config.title,
        color: mergedOptions.plugins.title
          ? mergedOptions.plugins.title.color
          : "#333",
        font: { size: 14, weight: "bold" },
      };
    }

    var ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: chartType,
      data: chartData,
      options: mergedOptions,
    });

    container.dataset.chartInitialized = "true";
  }

  /**
   * Initialize all metric charts on the page, using IntersectionObserver
   * for lazy loading when available.
   */
  function initAllCharts() {
    var containers = document.querySelectorAll(".metric-chart-container");
    if (!containers.length) return;

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              initChart(entry.target);
              observer.unobserve(entry.target);
            }
          });
        },
        { rootMargin: "200px" }
      );

      containers.forEach(function (container) {
        observer.observe(container);
      });
    } else {
      // Fallback: initialize all immediately
      containers.forEach(function (container) {
        initChart(container);
      });
    }
  }

  // Run on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAllCharts, {
      passive: true,
    });
  } else {
    initAllCharts();
  }
})();
