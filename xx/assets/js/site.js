const nav = document.querySelector(".nav");
const menuToggle = document.querySelector("[data-menu-toggle]");
const modal = document.querySelector("[data-modal]");

if (menuToggle && nav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });
}

document.querySelectorAll("[data-modal-open]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    modal?.classList.add("is-open");
  });
});

document.querySelectorAll("[data-modal-close]").forEach((button) => {
  button.addEventListener("click", () => modal?.classList.remove("is-open"));
});

modal?.addEventListener("click", (event) => {
  if (event.target === modal) modal.classList.remove("is-open");
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") modal?.classList.remove("is-open");
});
