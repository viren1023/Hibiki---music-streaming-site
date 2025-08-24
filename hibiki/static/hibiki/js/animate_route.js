document.addEventListener("DOMContentLoaded", function () {
  // Remove fade-out once the page has fully loaded
  document.body.classList.remove("fade-out");
});

window.addEventListener("beforeunload", function () {
  // Add fade-out before leaving the page
  document.body.classList.add("fade-out");
});