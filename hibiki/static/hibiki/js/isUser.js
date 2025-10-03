function isUserLoggedIn() {
  console.log("isUser function used")
  console.log(document.cookie)
  return document.cookie.split("; ").some(row => row.startsWith("HIBIKI_USERNAME="))
}

function showLoginPrompt() {
  const prompt = document.getElementById("loginPrompt")
  prompt.style.display = "flex"

  // Attach actions
  document.getElementById("cancelLogin").onclick = () => {
    prompt.style.display = "none"
  }
  document.getElementById("goToLogin").onclick = () => {
    window.location.href = "/login/"   // adjust to your login URL
  }
}