var regionList = [
    {"id": "RO-AB", "name": "Alba"},
    {"id": "RO-AR", "name": "Arad"},
    {"id": "RO-AG", "name": "Argeș"},
    {"id": "RO-BC", "name": "Bacău"},
    {"id": "RO-BH", "name": "Bihor"},
    {"id": "RO-BN", "name": "Bistrița-Năsăud"},
    {"id": "RO-BT", "name": "Botoșani"},
    {"id": "RO-BV", "name": "Brașov"},
    {"id": "RO-BR", "name": "Brăila"},
    {"id": "RO-BZ", "name": "Buzău"},
    {"id": "RO-CS", "name": "Caraș-Severin"},
    {"id": "RO-CL", "name": "Călărași"},
    {"id": "RO-CJ", "name": "Cluj"},
    {"id": "RO-CT", "name": "Constanța"},
    {"id": "RO-CV", "name": "Covasna"},
    {"id": "RO-DB", "name": "Dâmbovița"},
    {"id": "RO-DJ", "name": "Dolj"},
    {"id": "RO-GL", "name": "Galați"},
    {"id": "RO-GR", "name": "Giurgiu"},
    {"id": "RO-GJ", "name": "Gorj"},
    {"id": "RO-HR", "name": "Harghita"},
    {"id": "RO-HD", "name": "Hunedoara"},
    {"id": "RO-IL", "name": "Ialomița"},
    {"id": "RO-IS", "name": "Iași"},
    {"id": "RO-IF", "name": "Ilfov"},
    {"id": "RO-MM", "name": "Maramureș"},
    {"id": "RO-MH", "name": "Mehedinți"},
    {"id": "RO-MS", "name": "Mureș"},
    {"id": "RO-NT", "name": "Neamț"},
    {"id": "RO-OT", "name": "Olt"},
    {"id": "RO-PH", "name": "Prahova"},
    {"id": "RO-SM", "name": "Satu Mare"},
    {"id": "RO-SJ", "name": "Sălaj"},
    {"id": "RO-SB", "name": "Sibiu"},
    {"id": "RO-SV", "name": "Suceava"},
    {"id": "RO-TR", "name": "Teleorman"},
    {"id": "RO-TM", "name": "Timiș"},
    {"id": "RO-TL", "name": "Tulcea"},
    {"id": "RO-VS", "name": "Vaslui"},
    {"id": "RO-VL", "name": "Vâlcea"},
    {"id": "RO-VN", "name": "Vrancea"},
    {"id": "RO-B", "name": "Bucharest (Municipality)"}
];

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
            <li>Dezastru: ${details.disaster.value}</li>
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
  var changeSelector = document.getElementById("regionChange");
  

    const select = document.getElementById('regionChange');

    
    regionList.forEach(item => {
      console.log("aici");
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.name;
      select.appendChild(option);  // Append the option to the select element
    });
  
  
  loadMap();
};


function updateMapColor(iso) {
  $.ajax({
      url: '/change-color',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ 'iso': iso }),
      success: function(response) {
          console.log('Success:', response);
          // Update the SVG content on the page
          $('#mapContainer').html(response.svgContent);
      },
      error: function(error) {
          console.log('Am ajuns aici');
          console.log('Error:', error);
      }
  });
        }

 function changeColorByIso(elementId, isoCode, color) {
var map = document.getElementById(elementId).contentDocument.querySelector("svg");
var paths = map.querySelectorAll("path");
console.log("reached color change function in js");
paths.forEach(function (path) {
  var pathIsoCode = path.getAttribute("iso_3166_2");

  if (pathIsoCode === isoCode) {
    path.setAttribute("fill", color);
  }
});

 }

 function sleep(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

 async function testButton(iso){
  await sleep(3000);
  console.log(iso)
  console.log("Upload Button Clicked!")
  console.log(iso)
  updateMapColor(iso);

  changeColorByIso('map',iso,"#EE4E4E");
  
}

/* form */


/* form end*/

function toggleNotificationBar() {
  const notificationBar = document.querySelector('.notification-bar');
  notificationBar.classList.toggle('active');
}



async function fetchAlerts() {
  try {
      // Fetch user data (admin status) from session or another endpoint
      const userResponse = await fetch('/get_user_data');
      const userData = await userResponse.json();
      const isAdmin = userData.isAdmin;

      // Fetch alerts
      const response = await fetch('/alerts');
      const alerts = await response.json();

      const alertList = document.getElementById('alert-list');
      alertList.innerHTML = ''; // Clear existing content

      if (alerts.length > 0) {
          alerts.forEach(alert => {
              const alertItem = document.createElement('div');
              alertItem.className = 'alert-item';

              const alertImage = document.createElement('img');
              alertImage.src = `data:image/jpeg;base64,${alert.image}`;
              alertItem.appendChild(alertImage);

              const alertInfo = document.createElement('div');
              alertInfo.className = 'alert-info';

              const alertText = document.createElement('p');
              alertText.textContent = `${alert.disaster} in ${alert.region}`;
              alertInfo.appendChild(alertText);

              const alertTime = document.createElement('p');
              alertTime.className = 'alert-time';
              alertTime.textContent = `${alert.time}`; // TODO: add TIME to Database and display it here
              alertInfo.appendChild(alertTime);

              alertItem.appendChild(alertInfo);

              // Conditionally add delete button if user is admin
              if (isAdmin) {
                  const deleteButton = document.createElement('button');
                  deleteButton.innerHTML = '&#10060;';
                  deleteButton.className = 'delete-button';
                  deleteButton.onclick = () => deleteAlert(alert.id);
                  alertItem.appendChild(deleteButton);
              }

              alertList.appendChild(alertItem);
          });
      } else {
          const noAlert = document.createElement('p');
          noAlert.textContent = 'Nu sunt alerte active';
          alertList.appendChild(noAlert);
      }
  } catch (error) {
      console.error('Error fetching alerts:', error);
  }
}

// Function to fetch user data
async function getUserData() {
  const response = await fetch('/get_user_data');
  return await response.json();
}


async function deleteAlert(alertId) {
  try {
    const response = await fetch(`/alerts/${alertId}`, {
      method: 'DELETE',
    });
    if (response.ok) {
      fetchAlerts(); // Refresh the alert list after deletion
      //location.reload();
      var mapElement = document.getElementById('map');
      var currentData = mapElement.getAttribute('data');
      var updatedData = currentData.split('?')[0] + '?t=' + new Date().getTime();
      mapElement.setAttribute('data', updatedData);

      // Wait for the new map content to load before calling loadMap
      mapElement.addEventListener('load', () => {
        loadMap();
      }, { once: true });
    } else {
      console.error('Failed to delete alert');
    }
  } catch (error) {
    console.error('Error deleting alert:', error);
  }
}


// Fetch alerts when the page loads
document.addEventListener('DOMContentLoaded', fetchAlerts);
