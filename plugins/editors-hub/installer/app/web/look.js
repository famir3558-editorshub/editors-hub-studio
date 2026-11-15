// The studio's look, before the page draws (so it never flashes the other one). Aurora unless this browser chose the
// classic look in Settings > Look; "still" turns off the moving red glow.
(function () {
  var look = "aurora", still = false;
  try {
    look = localStorage.getItem("eh-look") || "aurora";
    still = localStorage.getItem("eh-still") === "1";
  } catch (e) { /* private window: the default look */ }
  var c = document.documentElement.classList;
  c.toggle("aurora", look === "aurora");
  c.toggle("still", still);
  window.ehLook = function () { return { aurora: c.contains("aurora"), still: c.contains("still") }; };
  window.ehSetLook = function (aurora, stillNow) {
    try {
      localStorage.setItem("eh-look", aurora ? "aurora" : "classic");
      localStorage.setItem("eh-still", stillNow ? "1" : "0");
    } catch (e) { /* kept for this page only */ }
    c.toggle("aurora", !!aurora);
    c.toggle("still", !!stillNow);
  };
})();
