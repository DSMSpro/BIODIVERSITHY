const speciesDropdown = document.getElementById("speciesDropdown");
const stateDropdown = document.getElementById("stateDropdown");

const floraBtn = document.getElementById("floraBtn");
const faunaBtn = document.getElementById("faunaBtn");
const analyzeBtn = document.getElementById("analyzeBtn");

const loader = document.getElementById("loadingContainer");

let category="flora";

const map=L.map("map").setView([22.5,80],5);

L.tileLayer(
"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
).addTo(map);

let markers=[];


/* Wikipedia popup */

async function fetchWikiSummary(species){

const url=
`https://en.wikipedia.org/api/rest_v1/page/summary/${species.replace(/ /g,"_")}`;

const res=await fetch(url);

const data=await res.json();

document.getElementById("wikiTitle").innerText=data.title||species;

document.getElementById("wikiSummary").innerText=data.extract||"No description available";

if(data.thumbnail){
document.getElementById("wikiImage").src=data.thumbnail.source;
}

document.getElementById("wikiLink").href=
data.content_urls?.desktop?.page||
`https://en.wikipedia.org/wiki/${species.replace(/ /g,"_")}`;

document.getElementById("wikiPopup").style.display="block";

}

document.getElementById("closePopup").onclick=function(){
document.getElementById("wikiPopup").style.display="none";
};



/* Load dropdown options */

async function loadOptions(){

const res=await fetch(
`http://127.0.0.1:8000/options?category=${category}&t=${Date.now()}`
);

const data=await res.json();

speciesDropdown.innerHTML="";
stateDropdown.innerHTML="";

data.species.forEach(sp=>{
const opt=document.createElement("option");
opt.value=sp;
opt.textContent=sp;
speciesDropdown.appendChild(opt);
});

const allOpt=document.createElement("option");
allOpt.value="all";
allOpt.textContent="All States";
stateDropdown.appendChild(allOpt);

data.states.forEach(st=>{
const opt=document.createElement("option");
opt.value=st;
opt.textContent=st;
stateDropdown.appendChild(opt);
});

}



/* Category switching */

floraBtn.onclick=()=>{
category="flora";
floraBtn.classList.add("active");
faunaBtn.classList.remove("active");
loadOptions();
};

faunaBtn.onclick=()=>{
category="fauna";
faunaBtn.classList.add("active");
floraBtn.classList.remove("active");
loadOptions();
};



/* Analyze */

analyzeBtn.onclick=async function(){

loader.style.display="block";

analyzeBtn.disabled=true;
analyzeBtn.innerText="Analyzing...";

try{

const species=speciesDropdown.value;
const state=stateDropdown.value;

const res=await fetch(
`http://127.0.0.1:8000/analyze?species=${species}&state=${state}&category=${category}`
);

const data=await res.json();

const tbody=document.querySelector("tbody");
tbody.innerHTML="";

markers.forEach(m=>map.removeLayer(m));
markers=[];

data.forEach(item=>{

const row=`
<tr>
<td>
<span class="species-link"
onclick="fetchWikiSummary('${item.species}')">
${item.species}
</span>
</td>
<td>${item.state}</td>
<td>${item.temperature} °C</td>
<td>${item.aqi}</td>
<td>${item.threat_status}</td>
<td>${item.ml_risk}</td>
<td>${item.rl_action}</td>
</tr>
`;

tbody.innerHTML+=row;

const marker=L.marker([item.lat,item.lon])
.addTo(map)
.bindPopup(
`<b>${item.species}</b><br>
${item.state}<br>
ML Risk: ${item.ml_risk}`
);

markers.push(marker);

});

if(data.length){
map.setView([data[0].lat,data[0].lon],5);
}

}
catch(err){

alert("Error fetching biodiversity data");

}

loader.style.display="none";

analyzeBtn.disabled=false;
analyzeBtn.innerText="Analyze Risk";

};



/* Start */

loadOptions();