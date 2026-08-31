document.documentElement.dataset.ready = "true";

const flash = document.querySelector("[data-flash]");
if (flash) {
  window.setTimeout(() => {
    flash.setAttribute("hidden", "");
  }, 4000);
}
