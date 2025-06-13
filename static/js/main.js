document.addEventListener("DOMContentLoaded", function () {
  initProductSwiper();
  initCatalogSwiper();
  initSmoothScroll();
  initScrollAnimations();
  initSearchForm();
  initModals();
  initScrollToTop();
  initLazyLoading();
  initPhoneMasks();
  initFireAnimations();
});

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
      640: { slidesPerView: 2 },
      1024: { slidesPerView: 3 },
      1280: { slidesPerView: 4 },
    },
    navigation: {
      nextEl: ".product-next",
      prevEl: ".product-prev",
    },
  });
}

function initCatalogSwiper() {
  const catalogSwiperEl = document.querySelector(".catalog-swiper");
  if (!catalogSwiperEl) return;

  new Swiper(".catalog-swiper", {
    slidesPerView: 1,
    spaceBetween: 24,
    navigation: {
      nextEl: ".catalog-next",
      prevEl: ".catalog-prev",
    },
    breakpoints: {
      640: { slidesPerView: 2 },
      1024: { slidesPerView: 3 },
      1280: { slidesPerView: 4 },
    },
  });
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href")).scrollIntoView({
        behavior: "smooth",
      });
    });
  });
}

function initScrollAnimations() {
  const animateOnScrollElements =
    document.querySelectorAll(".animate-on-scroll");
  const observerOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0.1,
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in-up-visible");
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  animateOnScrollElements.forEach((el) => observer.observe(el));
}

function initSearchForm() {
  const searchButton = document.getElementById("search-button");
  const searchInput = document.getElementById("search-input");
  const searchForm = document.getElementById("search-form");

  if (searchButton && searchInput && searchForm) {
    searchButton.addEventListener("click", function () {
      searchForm.classList.toggle("active");
      if (searchForm.classList.contains("active")) {
        searchInput.focus();
      }
    });

    document.addEventListener("click", function (event) {
      if (
        !searchForm.contains(event.target) &&
        !searchButton.contains(event.target)
      ) {
        searchForm.classList.remove("active");
      }
    });

    searchInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        console.log("Searching for:", searchInput.value);
      }
    });
  }
}

function initModals() {
  const openModalButtons = document.querySelectorAll("[data-modal-target]");
  const closeModalButtons = document.querySelectorAll("[data-close-button]");
  const overlays = document.querySelectorAll("#overlay");

  openModalButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const modal = document.querySelector(button.dataset.modalTarget);
      openModal(modal);
    });
  });

  overlays.forEach((overlay) => {
    overlay.addEventListener("click", () => {
      const modals = document.querySelectorAll(".modal.active");
      modals.forEach((modal) => closeModal(modal));
    });
  });

  closeModalButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const modal = button.closest(".modal");
      closeModal(modal);
    });
  });

  function openModal(modal) {
    if (modal == null) return;
    modal.classList.add("active");
    document.body.classList.add("overflow-hidden");
    overlays.forEach((overlay) => overlay.classList.add("active"));
  }

  function closeModal(modal) {
    if (modal == null) return;
    modal.classList.remove("active");
    document.body.classList.remove("overflow-hidden");
    overlays.forEach((overlay) => overlay.classList.remove("active"));
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      const activeModals = document.querySelectorAll(".modal.active");
      activeModals.forEach((modal) => closeModal(modal));
    }
  });
}

function initScrollToTop() {
  const scrollToTopBtn = document.getElementById("backToTop");

  if (scrollToTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        scrollToTopBtn.classList.remove("opacity-0", "invisible");
        scrollToTopBtn.classList.add("opacity-100", "visible");
      } else {
        scrollToTopBtn.classList.add("opacity-0", "invisible");
        scrollToTopBtn.classList.remove("opacity-100", "visible");
      }
    });

    scrollToTopBtn.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }
}

function initLazyLoading() {
  const lazyImages = document.querySelectorAll("img.lazyload");

  if ("IntersectionObserver" in window) {
    let lazyImageObserver = new IntersectionObserver(function (
      entries,
      observer
    ) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          let lazyImage = entry.target;
          lazyImage.src = lazyImage.dataset.src;
          if (lazyImage.dataset.srcset) {
            lazyImage.srcset = lazyImage.dataset.srcset;
          }
          lazyImage.classList.remove("lazyload");
          lazyImageObserver.unobserve(lazyImage);
        }
      });
    });

    lazyImages.forEach(function (lazyImage) {
      lazyImageObserver.observe(lazyImage);
    });
  } else {
    lazyImages.forEach(function (lazyImage) {
      lazyImage.src = lazyImage.dataset.src;
      if (lazyImage.dataset.srcset) {
        lazyImage.srcset = lazyImage.dataset.srcset;
      }
      lazyImage.classList.remove("lazyload");
    });
  }
}

function initPhoneMasks() {
  document.querySelectorAll('input[type="tel"]').forEach((input) => {
    input.addEventListener("input", function (event) {
      formatPhone(this);
    });
    if (input.value) {
      formatPhone(input);
    }
  });
}

function initFireAnimations() {
  const fireCards = document.querySelectorAll(".fire-card");
  const btnFires = document.querySelectorAll(".btn-fire");
  const fireInputs = document.querySelectorAll(".fire-input");

  fireCards.forEach((card) => Utils.addFireEffect(card));
  btnFires.forEach((btn) => Utils.addFireEffect(btn));
  fireInputs.forEach((input) => Utils.addFireEffect(input));
}

window.VympelJS = {
  Utils,
  initProductSwiper,
  initCatalogSwiper,
  initSmoothScroll,
  initScrollAnimations,
  initFireAnimations,
};

window.formatPhone = function (input) {
  let value = input.value.replace(/\D/g, "");
  if (value.startsWith("7")) value = value.substring(1);
  if (value.startsWith("8")) value = value.substring(1);

  if (value.length > 0) {
    value = "+7 (" + value.substring(0, 3);
    if (value.length > 6) {
      value += ") " + value.substring(6, 9);
    }
    if (value.length > 13) {
      value += "-" + value.substring(13, 15);
    }
    if (value.length > 16) {
      value += "-" + value.substring(16, 18);
    }
  }
  input.value = value;
};

const Utils = {
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
