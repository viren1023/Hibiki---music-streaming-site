function showToast(message) {
  const toast = document.createElement("div")
  toast.className = "toast"
  toast.innerHTML = message // ✅ render HTML like <b>
  document.body.appendChild(toast)

  setTimeout(() => toast.classList.add("show"), 100)

  setTimeout(() => {
    toast.classList.remove("show")
    setTimeout(() => toast.remove(), 300)
  }, 5000) // I also suggest using a reasonable duration
}
