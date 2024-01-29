

function loadMap() {
  var map = document.getElementById("map").contentDocument.querySelector("svg");
  var toolTip = document.getElementById("toolTip");

  // Add event listeners to map element
  if (!/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    // If user agent is not mobile add click listener (for wikidata links)
    map.addEventListener("click", handleClick, false);
  }
  map.addEventListener("mousemove", mouseEntered, false);
  map.addEventListener("mouseout", mouseGone, false);

  // Show tooltip on mousemove
  function mouseEntered(e) {
    var target = e.target;
    if (target.nodeName == "path") {
      target.style.opacity = 0.6;
      var details = e.target.attributes;

      // Follow cursor
      toolTip.style.transform = `translate(${e.offsetX}px, ${e.offsetY}px)`;

      // Tooltip data
      toolTip.innerHTML = `
        <ul>
            <li><b>${details.gn_name.value}</b></li>
            <li>Population: ${details.population.value}</li>
            <li>Prescurtare: ${details.postal.value}</li>
            <li class="details-text">Click for details</li>
        </ul>`;
    }
  }

  // Clear tooltip on mouseout
  function mouseGone(e) {
    var target = e.target;
    if (target.nodeName == "path") {
      target.style.opacity = 1;
      toolTip.innerHTML = "";
    }
  }

  // Go to wikidata page onclick
  function handleClick(e) {
    if (e.target.nodeName == "path") {
      var details = e.target.attributes;
      window.open(`https://www.wikidata.org/wiki/${details.wikidataid.value}`, "_blank");
    }
  }
}

// Calls init function on window load
window.onload = function () {
  loadMap();
};


function changeColorByIso(elementId, isoCode, color) {
  var map = document.getElementById(elementId).contentDocument.querySelector("svg");
  var paths = map.querySelectorAll("path");

  paths.forEach(function (path) {
    var pathIsoCode = path.getAttribute("iso_3166_2");

    if (pathIsoCode === isoCode) {
      path.setAttribute("fill", color);
    }
  });
}
