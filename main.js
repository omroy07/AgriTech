window.addEventListener("offline", () => {
  alert("You are offline. Cached content is being shown.");
});

window.addEventListener("online", () => {
  alert("You are back online.");
});
