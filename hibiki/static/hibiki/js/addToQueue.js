function addToQueue(e, newTrackIndex) {
    e.stopPropagation()
    newTrack = window.tracks[newTrackIndex]
    window.tracks.push(newTrack)
    console.log(window.tracks)
}