/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [
    require("daisyui")
  ],
  daisyui: {
    themes: [
      {
        dark_drexel: {
          ...require("daisyui/src/theming/themes")["dark"],
          "primary": "#0D2C54",
          "secondary": "yellow",
          "accent": "lightblue"
        },
        light_drexel: {
          ...require("daisyui/src/theming/themes")["light"],
          "primary": "#0D2C54",
          "secondary": "yellow",
          "accent": "lightblue"
        },
      },
      "light",
      "dark"
    ]
  }
}

