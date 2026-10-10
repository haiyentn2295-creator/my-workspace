/**
 * AI4A Count-Up Animation Engine
 * Zero-dependency, 60-120fps requestAnimationFrame counter
 * Supports: Currency (VND, USD), Percentage, Integers, Easing Deceleration
 */

class CountUpEngine {
  /**
   * Easing function: fast start, smooth exponential brake
   */
  static easeOutExpo(t) {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }

  /**
   * Animate a single element from 0 or from current to targetValue
   */
  static animate(element, config = {}) {
    const target = parseFloat(config.target ?? element.getAttribute('data-target') ?? 0);
    const duration = parseInt(config.duration ?? element.getAttribute('data-duration') ?? 1800, 10);
    const prefix = config.prefix ?? element.getAttribute('data-prefix') ?? '';
    const suffix = config.suffix ?? element.getAttribute('data-suffix') ?? '';
    const decimals = parseInt(config.decimals ?? element.getAttribute('data-decimals') ?? 0, 10);
    const locale = config.locale ?? element.getAttribute('data-locale') ?? 'vi-VN';

    const startValue = 0;
    const startTime = performance.now();

    function formatNumber(val) {
      return val.toLocaleString(locale, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
    }

    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = CountUpEngine.easeOutExpo(progress);
      const currentValue = startValue + (target - startValue) * easedProgress;

      element.textContent = `${prefix}${formatNumber(currentValue)}${suffix}`;

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = `${prefix}${formatNumber(target)}${suffix}`;
      }
    }

    requestAnimationFrame(step);
  }

  /**
   * Scan and automatically initialize all .kpi-counter elements
   * Uses IntersectionObserver to trigger animation when visible
   */
  static initAll(selector = '.kpi-counter') {
    const elements = document.querySelectorAll(selector);

    if (!('IntersectionObserver' in window)) {
      elements.forEach(el => CountUpEngine.animate(el));
      return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          CountUpEngine.animate(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    elements.forEach(el => observer.observe(el));
  }
}

// Auto-run when DOM is ready
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    CountUpEngine.initAll();
  });
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CountUpEngine;
}
