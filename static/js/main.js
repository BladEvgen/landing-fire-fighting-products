document.addEventListener("DOMContentLoaded", function () {
  initProductSwiper();
  initCatalogSwiper();
  initCertificatesSwiper(); // Новый слайдер сертификатов
  initSmoothScroll();
  initScrollAnimations();
  initSearchForm();
  initModals();
  initScrollToTop();
  initLazyLoading();
  initPhoneMasks();
  initFireAnimations(); // Новые огненные анимации
});

// Слайдер продукции
function initProductSwiper() {
  const productSwiperEl = document.querySelector(".product-swiper");
  if (!productSwiperEl) return;

  new Swiper(".product-swiper", {
    loop: true,
    autoplay: {
      delay: 4000,
      disableOnInteraction: false,
    },
    slidesPerView: 1,
    spaceBetween: 24,
    breakpoints: {
      640: {
        slidesPerView: 2,
      },
      1024: {
        slidesPerView: 3,
      },
      1280: {
        slidesPerView: 4,
      },
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
      dynamicBullets: true,
      bulletActiveClass: "swiper-pagination-bullet-active",
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    effect: "slide",
    speed: 600,
    // Кастомные стили для пагинации
    on: {
      init: function () {
        const bullets = this.pagination.el.querySelectorAll(
          ".swiper-pagination-bullet"
        );
        bullets.forEach((bullet) => {
          bullet.style.background = "#ff6b00";
          bullet.style.opacity = "0.5";
        });
      },
      paginationUpdate: function () {
        const bullets = this.pagination.el.querySelectorAll(
          ".swiper-pagination-bullet"
        );
        bullets.forEach((bullet) => {
          bullet.style.background = "#ff6b00";
          bullet.style.opacity = bullet.classList.contains(
            "swiper-pagination-bullet-active"
          )
            ? "1"
            : "0.5";
        });
      },
    },
  });
}

// Слайдер каталога
function initCatalogSwiper() {
  const catalogSwiperEl = document.querySelector(".catalog-swiper");
  if (!catalogSwiperEl) return;

  new Swiper(".catalog-swiper", {
    slidesPerView: 1,
    spaceBetween: 20,
    breakpoints: {
      768: {
        slidesPerView: 2,
      },
      1024: {
        slidesPerView: 3,
      },
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    on: {
      init: function () {
        const bullets = this.pagination.el.querySelectorAll(
          ".swiper-pagination-bullet"
        );
        bullets.forEach((bullet) => {
          bullet.style.background = "#ff6b00";
          bullet.style.opacity = "0.5";
        });
      },
    },
  });
}

// Новый слайдер сертификатов с центрированием и затемнением
function initCertificatesSwiper() {
  const certificatesSwiperEl = document.querySelector(".certificates-swiper");
  if (!certificatesSwiperEl) return;

  new Swiper(".certificates-swiper", {
    centeredSlides: true,
    loop: true,
    autoplay: {
      delay: 3000,
      disableOnInteraction: false,
    },
    slidesPerView: 1,
    spaceBetween: 20,
    breakpoints: {
      640: {
        slidesPerView: 1.5,
        spaceBetween: 30,
      },
      768: {
        slidesPerView: 2.5,
        spaceBetween: 30,
      },
      1024: {
        slidesPerView: 3.5,
        spaceBetween: 40,
      },
      1280: {
        slidesPerView: 4.5,
        spaceBetween: 40,
      },
    },
    pagination: {
      el: ".certificates-pagination",
      clickable: true,
      dynamicBullets: true,
    },
    navigation: {
      nextEl: ".certificates-next",
      prevEl: ".certificates-prev",
    },
    speed: 800,
    // Эффект затемнения неактивных слайдов
    on: {
      init: function () {
        this.updateSlidesOpacity();
      },
      slideChange: function () {
        this.updateSlidesOpacity();
      },
      transitionEnd: function () {
        this.updateSlidesOpacity();
      },
    },
  });

  // Добавляем функцию для обновления прозрачности слайдов
  if (window.Swiper) {
    Swiper.prototype.updateSlidesOpacity = function () {
      this.slides.forEach((slide, index) => {
        if (slide.classList.contains("swiper-slide-active")) {
          slide.style.opacity = "1";
          slide.style.transform = "scale(1)";
        } else {
          slide.style.opacity = "0.6";
          slide.style.transform = "scale(0.9)";
        }
        slide.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      });
    };
  }
}

// Плавная прокрутка
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        const headerHeight = document.querySelector("header").offsetHeight;
        const targetPosition = target.offsetTop - headerHeight;

        window.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        });
      }
    });
  });
}

// Анимации при скролле
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate__animated", "animate__fadeInUp");

        // Специальная анимация для карточек с огненным эффектом
        if (entry.target.classList.contains("fire-card")) {
          entry.target.style.boxShadow = "0 10px 40px rgba(255, 107, 0, 0.3)";
          entry.target.style.transform = "translateY(0)";
        }

        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll(".animate-on-scroll").forEach((el) => {
    // Подготавливаем элементы для анимации
    if (el.classList.contains("fire-card")) {
      el.style.transform = "translateY(20px)";
      el.style.transition = "all 0.6s ease";
    }
    observer.observe(el);
  });
}

// Поиск
function initSearchForm() {
  const searchForm = document.querySelector("#search-form");
  const searchInput = document.querySelector("#search-input");

  if (!searchForm || !searchInput) return;

  searchInput.addEventListener("input", function () {
    const query = this.value.trim();
    if (query.length > 2) {
      console.log("Search query:", query);
    }
  });
}

// Модальные окна
function initModals() {
  document.querySelectorAll("[data-modal-trigger]").forEach((trigger) => {
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      const modalId = this.getAttribute("data-modal-trigger");
      const modal = document.querySelector(`#${modalId}`);
      if (modal) {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
        document.body.style.overflow = "hidden";
      }
    });
  });

  document.querySelectorAll("[data-modal-close]").forEach((closeBtn) => {
    closeBtn.addEventListener("click", function () {
      const modal = this.closest(".modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        document.body.style.overflow = "";
      }
    });
  });

  document.querySelectorAll(".modal").forEach((modal) => {
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        this.classList.add("hidden");
        this.classList.remove("flex");
        document.body.style.overflow = "";
      }
    });
  });
}

// Кнопка "Наверх" с правильным позиционированием
function initScrollToTop() {
  let scrollTopBtn = document.querySelector("#backToTop");

  if (!scrollTopBtn) {
    scrollTopBtn = document.createElement("button");
    scrollTopBtn.id = "backToTop";
    scrollTopBtn.className =
      "fixed w-12 h-12 text-white rounded-full transition-all duration-300 opacity-0 invisible hover:scale-110 z-40";
    scrollTopBtn.style.cssText = `
      bottom: 6rem; 
      right: 1rem; 
      background: linear-gradient(135deg, #ff6b00 0%, #ff4500 100%);
      box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
    `;
    scrollTopBtn.innerHTML = `
      <svg class="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
      </svg>
    `;
    document.body.appendChild(scrollTopBtn);
  }

  // Адаптивное позиционирование
  function updateButtonPosition() {
    if (window.innerWidth >= 1024) {
      scrollTopBtn.style.bottom = "1.5rem";
      scrollTopBtn.style.right = "1.5rem";
    } else {
      scrollTopBtn.style.bottom = "6rem"; // Отступ от мобильной навигации
      scrollTopBtn.style.right = "1rem";
    }
  }

  updateButtonPosition();
  window.addEventListener("resize", updateButtonPosition);

  window.addEventListener("scroll", function () {
    if (window.pageYOffset > 300) {
      scrollTopBtn.classList.remove("opacity-0", "invisible");
      scrollTopBtn.classList.add("opacity-100", "visible");
    } else {
      scrollTopBtn.classList.add("opacity-0", "invisible");
      scrollTopBtn.classList.remove("opacity-100", "visible");
    }
  });

  scrollTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Анимация свечения при наведении
  scrollTopBtn.addEventListener("mouseenter", function () {
    this.style.background = "linear-gradient(135deg, #ff4500 0%, #d51b1b 100%)";
    this.style.boxShadow = "0 8px 25px rgba(255, 107, 0, 0.5)";
  });

  scrollTopBtn.addEventListener("mouseleave", function () {
    this.style.background = "linear-gradient(135deg, #ff6b00 0%, #ff4500 100%)";
    this.style.boxShadow = "0 4px 15px rgba(255, 107, 0, 0.3)";
  });
}

// Ленивая загрузка изображений
function initLazyLoading() {
  const images = document.querySelectorAll("img[data-src]");

  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");

        // Добавляем плавное появление
        img.style.opacity = "0";
        img.style.transition = "opacity 0.3s ease";
        img.onload = function () {
          this.style.opacity = "1";
        };

        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach((img) => imageObserver.observe(img));
}

// Маска для телефона с улучшенным стилем
function initPhoneMasks() {
  const phoneInputs = document.querySelectorAll('input[type="tel"]');

  phoneInputs.forEach((input) => {
    // Добавляем классы для стилизации
    input.classList.add("phone-input");

    input.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, "");
      if (value.startsWith("7")) value = value.substring(1);
      if (value.startsWith("8")) value = value.substring(1);

      let formattedValue = "+7";
      if (value.length > 0) {
        formattedValue += " (" + value.substring(0, 3);
      }
      if (value.length >= 4) {
        formattedValue += ") " + value.substring(3, 6);
      }
      if (value.length >= 7) {
        formattedValue += "-" + value.substring(6, 8);
      }
      if (value.length >= 9) {
        formattedValue += "-" + value.substring(8, 10);
      }

      e.target.value = formattedValue;
    });

    // Анимация фокуса
    input.addEventListener("focus", function () {
      this.style.borderColor = "#ff6b00";
      this.style.boxShadow = "0 0 0 3px rgba(255, 107, 0, 0.1)";
    });

    input.addEventListener("blur", function () {
      this.style.borderColor = "rgba(112, 128, 144, 0.3)";
      this.style.boxShadow = "none";
    });
  });
}

// Новые огненные анимации
function initFireAnimations() {
  // Анимация мерцания для элементов с классом fire-glow
  const fireElements = document.querySelectorAll(".fire-glow");
  fireElements.forEach((element) => {
    element.style.animation = "fire-pulse 2s ease-in-out infinite";
  });

  // Анимация для кнопок
  const fireButtons = document.querySelectorAll(".btn-fire, .fire-button");
  fireButtons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.boxShadow = "0 8px 25px rgba(255, 107, 0, 0.4)";
      this.style.transform = "translateY(-2px)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.boxShadow = "0 4px 15px rgba(255, 107, 0, 0.3)";
      this.style.transform = "translateY(0)";
    });
  });

  // Добавляем CSS анимации
  if (!document.querySelector("#fire-animations-style")) {
    const style = document.createElement("style");
    style.id = "fire-animations-style";
    style.textContent = `
      @keyframes fire-pulse {
        0%, 100% { 
          box-shadow: 0 0 20px rgba(255, 107, 0, 0.3);
          filter: brightness(1);
        }
        50% { 
          box-shadow: 0 0 30px rgba(255, 107, 0, 0.6);
          filter: brightness(1.1);
        }
      }

      .fire-card {
        transition: all 0.3s ease;
      }

      .fire-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(255, 107, 0, 0.2);
      }

      .phone-input {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(112, 128, 144, 0.3);
        transition: all 0.3s ease;
      }

      .certificates-swiper .swiper-slide {
        transition: opacity 0.3s ease, transform 0.3s ease;
      }

      .certificates-swiper .swiper-slide:not(.swiper-slide-active) {
        opacity: 0.6;
        transform: scale(0.9);
      }

      .certificates-swiper .swiper-slide-active {
        opacity: 1;
        transform: scale(1);
      }
    `;
    document.head.appendChild(style);
  }
}

// Утилиты
const Utils = {
  debounce: function (func, wait, immediate) {
    let timeout;
    return function executedFunction() {
      const context = this;
      const args = arguments;
      const later = function () {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  },

  throttle: function (func, limit) {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },

  isMobile: function () {
    return window.innerWidth <= 768;
  },

  // Новая утилита для огненных эффектов
  addFireEffect: function (element) {
    element.classList.add("fire-glow");
    element.style.transition = "all 0.3s ease";
    element.addEventListener("mouseenter", function () {
      this.style.filter =
        "brightness(1.1) drop-shadow(0 0 10px rgba(255, 107, 0, 0.5))";
    });
    element.addEventListener("mouseleave", function () {
      this.style.filter = "brightness(1)";
    });
  },
};

// Глобальные функции
window.VympelJS = {
  Utils,
  initProductSwiper,
  initCatalogSwiper,
  initCertificatesSwiper,
  initSmoothScroll,
  initScrollAnimations,
  initFireAnimations,
};

// Экспорт функции форматирования телефона для использования в шаблонах
window.formatPhone = function (input) {
  let value = input.value.replace(/\D/g, "");
  if (value.startsWith("7")) value = value.substring(1);
  if (value.startsWith("8")) value = value.substring(1);

  let formattedValue = "+7";
  if (value.length > 0) {
    formattedValue += " (" + value.substring(0, 3);
  }
  if (value.length >= 4) {
    formattedValue += ") " + value.substring(3, 6);
  }
  if (value.length >= 7) {
    formattedValue += "-" + value.substring(6, 8);
  }
  if (value.length >= 9) {
    formattedValue += "-" + value.substring(8, 10);
  }

  input.value = formattedValue;
};
