let projects = [];
let currentIndex = 0;
let previewImages = [];
let currentImageIndex = 0;

const canvas = document.querySelector("#webgl");
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const logoGroup = new THREE.Group();
scene.add(logoGroup);

const dbMaterial = new THREE.MeshStandardMaterial({ color: 0xe48e00, roughness: 0.2, metalness: 0.1 }); 
const dbGeo = new THREE.CylinderGeometry(0.7, 0.7, 0.3, 64); 
for (let i = -1; i <= 1; i++) {
  const disc = new THREE.Mesh(dbGeo, dbMaterial);
  disc.position.y = i * 0.4;
  logoGroup.add(disc);
}

const pyBlueMat = new THREE.MeshStandardMaterial({ color: 0x306998, roughness: 0.1, metalness: 0.2 });
const pyYellowMat = new THREE.MeshStandardMaterial({ color: 0xFFD43B, roughness: 0.1, metalness: 0.2 });
const ringGeo = new THREE.TorusGeometry(1.2, 0.15, 32, 100); 

const blueRing = new THREE.Mesh(ringGeo, pyBlueMat);
blueRing.rotation.x = 1.5;
blueRing.rotation.y = 0.5;
logoGroup.add(blueRing);

const yellowRing = new THREE.Mesh(ringGeo, pyYellowMat);
yellowRing.rotation.x = -1.5;
yellowRing.rotation.y = -0.5;
logoGroup.add(yellowRing);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

function animate() {
  requestAnimationFrame(animate);
  
  // SLOWED DOWN: Gentle, premium spin
  logoGroup.rotation.y += 0.0015;
  
  // SLOWED DOWN: Relaxed up and down levitation
  logoGroup.position.y = -0.2 + Math.sin(Date.now() * 0.0008) * 0.15; 
  
  renderer.render(scene, camera);
}
animate();

function adjustCamera() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.position.z = window.innerWidth > 768 ? 9 : 7.5; 
  camera.position.y = 0; 
}
window.addEventListener("resize", adjustCamera);
adjustCamera(); 

document.getElementById("btn-start").addEventListener("click", () => {
  document.getElementById("intro-screen").classList.add("unlocked");
  document.body.classList.add("started");
});

const kebabBtn = document.getElementById("btn-menu");
const closeSideBtn = document.getElementById("btn-close");
const sideMenu = document.getElementById("side-menu");
const overlay = document.getElementById("menu-overlay");

function toggleMenu(show) {
  if (show) {
    sideMenu.classList.add("open");
    overlay.classList.add("active");
  } else {
    sideMenu.classList.remove("open");
    overlay.classList.remove("active");
  }
}
kebabBtn.addEventListener("click", () => toggleMenu(true));
closeSideBtn.addEventListener("click", () => toggleMenu(false));
overlay.addEventListener("click", () => toggleMenu(false));

function updateMenuState() {
  const listItems = document.querySelectorAll("#project-list li");
  listItems.forEach((li, idx) => {
    idx === currentIndex ? li.classList.add("active") : li.classList.remove("active");
  });
}

function updateUI() {
  const p = projects[currentIndex];
  if (!p) return;
  document.getElementById("proj-category").textContent = p.category;
  document.getElementById("proj-title").textContent = p.title;
  document.getElementById("proj-desc").textContent = p.description;
  document.getElementById("proj-indicator").textContent = `${currentIndex + 1} / ${projects.length}`;
  
  updateMenuState();
  
  previewImages = [
    `https://placehold.co/800x500/ffb703/1a1a1a.png?text=${encodeURIComponent(p.title)}+Preview+1`,
    `https://placehold.co/800x500/8e4b3e/ffffff.png?text=${encodeURIComponent(p.title)}+Preview+2`
  ];
  currentImageIndex = 0;
}

function buildMenu() {
  const list = document.getElementById("project-list");
  list.innerHTML = "";
  projects.forEach((p, index) => {
    const li = document.createElement("li");
    li.textContent = p.title;
    li.addEventListener("click", () => {
      currentIndex = index;
      updateUI();
      toggleMenu(false);
    });
    list.appendChild(li);
  });
}

fetch("/api/projects").then(res => res.json()).then(data => { projects = data; buildMenu(); updateUI(); });

document.getElementById("btn-prev").addEventListener("click", () => {
  if (projects.length === 0) return;
  currentIndex = (currentIndex - 1 + projects.length) % projects.length;
  updateUI();
});
document.getElementById("btn-next").addEventListener("click", () => {
  if (projects.length === 0) return;
  currentIndex = (currentIndex + 1) % projects.length;
  updateUI();
});
document.getElementById("btn-download").addEventListener("click", () => {
  const p = projects[currentIndex];
  if (p) window.location.href = `/api/download/${p.id}`;
});

const previewModal = document.getElementById("preview-modal");
const previewImg = document.getElementById("preview-image");
const modalIndicator = document.getElementById("modal-indicator");

function updateModalImage() {
  previewImg.src = previewImages[currentImageIndex];
  modalIndicator.textContent = `${currentImageIndex + 1} / ${previewImages.length}`;
}

document.getElementById("btn-preview").addEventListener("click", () => {
  updateModalImage();
  previewModal.classList.add("active");
});
document.getElementById("close-modal").addEventListener("click", () => {
  previewModal.classList.remove("active");
});
document.getElementById("modal-prev").addEventListener("click", () => {
  currentImageIndex = (currentImageIndex - 1 + previewImages.length) % previewImages.length;
  updateModalImage();
});
document.getElementById("modal-next").addEventListener("click", () => {
  currentImageIndex = (currentImageIndex + 1) % previewImages.length;
  updateModalImage();
});
