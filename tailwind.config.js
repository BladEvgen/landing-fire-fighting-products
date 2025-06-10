module.exports = {
  content: ["./core/templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        "fire-primary": "#0d1b2a", // тёмный фон/текст
        "fire-accent": "#ff6b00", // оранжевый акцент
        "fire-bg": "#f9fafb", // светлый фон секций
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        brand: ["Montserrat Alternates", "Inter", "sans-serif"],
      },
      boxShadow: {
        fire: "0 8px 24px rgba(0,0,0,0.08)",
      },
      borderRadius: {
        brand: "1rem",
      },
    },
  },
  plugins: [],
};
