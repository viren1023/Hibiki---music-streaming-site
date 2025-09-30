let addTrack = null

// function toggleMenu(e, index) {
//   console.log("playlist toggleMenu")
//   e.stopPropagation() // prevent row click
//   const menu = document.getElementById(`dotmenu-${index}`)
//   const allMenus = document.querySelectorAll(".dotmenu")
//   allMenus.forEach((m) => {
//     if (m !== menu) m.style.display = "none"
//   })
//   menu.style.display = menu.style.display === "block" ? "none" : "block"
//   // console.log(e)
//   // console.log(index)
// }

function toggleMenu(e, index) {
  console.log("playlist toggleMenu")
  e.stopPropagation() // stop button click bubbling

  const menu = document.getElementById(`dotmenu-${index}`)
  const allMenus = document.querySelectorAll(".dotmenu")

  // Close all other menus
  allMenus.forEach((m) => {
    if (m !== menu) m.style.display = "none"
  })

  // Toggle current menu
  const isOpen = menu.style.display === "block"
  menu.style.display = isOpen ? "none" : "block"

  if (!isOpen) {
    // Add a one-time document click listener to close menu
    const closeOnOutsideClick = (event) => {
      if (!menu.contains(event.target)) {
        menu.style.display = "none"
        document.removeEventListener("click", closeOnOutsideClick)
      }
    }
    document.addEventListener("click", closeOnOutsideClick)
  }

  // Close if menu itself is clicked
  menu.onclick = (ev) => {
    ev.stopPropagation()
    menu.style.display = "none"
    document.removeEventListener("click", closeOnOutsideClick)
  }
}

// function addToPlaylistfromplaylist(res) {
//     addTrack = null
//     addTrack = res
//     console.log("hello")
//     console.log(typeof (res))
//     document.getElementById("playlistModal").style.display = "flex";
//     _loadPlaylists()
// }

function closeModal() {
  document.getElementById("playlistModal").style.display = "none"
}

function fun() {
  console.log("hello")
}

document.addEventListener("DOMContentLoaded", () => {
  const backdrop = document.getElementById("playlistBackdrop")
  const list = document.getElementById("playlistList")
  const noPlaylists = document.getElementById("noPlaylists")

  // Open modal
  window.addToPlaylistfromplaylist = (e, res) => {
    e.stopPropagation()
    console.log("playlist addToPlaylistfromplaylist")

    if (!isUserLoggedIn()) {
      showLoginPrompt()
      return
    }

    if (!backdrop) return console.error("playlistBackdrop not found")
    backdrop.classList.add("open")

    addTrack = res
    _loadPlaylists() // Load playlists dynamically
  }

  // Close modal
  window.closeModal = () => {
    if (!backdrop) return
    backdrop.classList.remove("open")
  }

  // Load playlists dynamically
  function _loadPlaylists() {
    console.log("playlist _loadPlaylists")
    fetch("/show-playlist/")
      .then((response) => response.json())
      .then((data) => {
        list.innerHTML = ""

        if (!data.playlists || data.playlists.length === 0) {
          noPlaylists.style.display = "block"
          return
        }

        noPlaylists.style.display = "none"

        data.playlists.forEach((p) => {
          const li = document.createElement("li")
          li.textContent = `${p.name} (${p.total_songs} songs)`

          li.addEventListener("click", () => {
            _playlistClicked(p.id, p.name)
          })

          list.appendChild(li)
        })
      })
      .catch((err) => console.error("Error loading playlists:", err))
  }

  // Example function when a playlist is clicked
  function _playlistClicked(id, name) {
    console.log("playlist _playlistClicked")
    fetch("/add_to_playlist/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        playlist_id: id,
        track: addTrack,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          alert(`Track added to ${name}`)
          closeModal() // optionally close modal after adding
        } else {
          alert(data.message || "Error adding track")
        }
      })
      .catch((err) => console.error(err))
    closeModal() // optionally close modal after selection
  }
})
