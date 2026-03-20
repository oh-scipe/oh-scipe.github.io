document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar-offcanvas");

  if (!sidebar) {
    return;
  }

  const toggleButtons = document.querySelectorAll("button.btn-findpage");

  for (const button of toggleButtons) {
    button.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }
});
