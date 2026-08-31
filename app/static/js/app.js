document.documentElement.dataset.ready = "true";

const flash = document.querySelector("[data-flash]");
if (flash) {
  window.setTimeout(() => {
    flash.setAttribute("hidden", "");
  }, 4000);
}

const copyButton = document.querySelector("[data-copy]");
const copySource = document.querySelector("[data-copy-source]");
if (copyButton && copySource) {
  const defaultLabel = copyButton.getAttribute("data-copy-label") || "Copy";

  const fallbackCopy = (text) => {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "absolute";
    field.style.left = "-9999px";
    document.body.appendChild(field);
    field.select();
    document.execCommand("copy");
    field.remove();
  };

  copyButton.addEventListener("click", async () => {
    const text = copySource.textContent || "";
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        fallbackCopy(text);
      }
      copyButton.textContent = "Copied";
      window.setTimeout(() => {
        copyButton.textContent = defaultLabel;
      }, 2000);
    } catch {
      copyButton.textContent = "Copy failed";
      window.setTimeout(() => {
        copyButton.textContent = defaultLabel;
      }, 2000);
    }
  });
}
