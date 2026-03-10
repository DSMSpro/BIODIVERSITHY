const speciesDropdown = document.getElementById("speciesDropdown");
const stateDropdown = document.getElementById("stateDropdown");

const floraBtn = document.getElementById("floraBtn");
const faunaBtn = document.getElementById("faunaBtn");
const analyzeBtn = document.getElementById("analyzeBtn");

let category = "flora";

const map = L.map("map").setView([22.5, 80], 5);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

let marker = null;


// Load Options from Backend
async function loadOptions() {

  const res = await fetch(
    `http://127.0.0.1:8000/options?category=${category}`
  );

  const data = await res.json();

  // Species
  speciesDropdown.innerHTML = "";
  data.species.forEach(sp => {
    let opt = document.createElement("option");
    opt.value = sp;
    opt.textContent = sp;
    speciesDropdown.appendChild(opt);
  });

  // States
  stateDropdown.innerHTML = "";
  data.states.forEach(st => {
    let opt = document.createElement("option");
    opt.value = st;
    opt.textContent = st;
    stateDropdown.appendChild(opt);
  });
}


// Tabs
floraBtn.onclick = () => {
  category = "flora";
  floraBtn.classList.add("active");
  faunaBtn.classList.remove("active");
  loadOptions();
};

faunaBtn.onclick = () => {
  category = "fauna";
  faunaBtn.classList.add("active");
  floraBtn.classList.remove("active");
  loadOptions();
};


// Analyze
analyzeBtn.onclick = async () => {

  const species = speciesDropdown.value;
  const state = stateDropdown.value;

  const res = await fetch(
    `http://127.0.0.1:8000/analyze?species=${species}&state=${state}&category=${category}`
  );

  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  // Table Fill
  document.getElementById("tSpecies").innerText = data.species;
  document.getElementById("tState").innerText = data.state;
  document.getElementById("tTemp").innerText = data.temperature + " °C";
  document.getElementById("tAQI").innerText = data.aqi;
  document.getElementById("tThreat").innerText = data.threat_status;
  document.getElementById("tRisk").innerText = data.ml_risk;
  document.getElementById("tAction").innerText = data.rl_action;

  // Map Marker
  if (marker) map.removeLayer(marker);

  marker = L.marker([data.lat, data.lon])
    .addTo(map)
    .bindPopup(`${data.species}<br>${data.ml_risk}`)
    .openPopup();

  map.setView([data.lat, data.lon], 6);
};


// Start
loadOptions();
