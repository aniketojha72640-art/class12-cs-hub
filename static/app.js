let projects = [];
let currentIndex = 0;
let previewImages = [];
let currentImageIndex = 0;

const canvas = document.querySelector("#webgl");
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// 1. Create a Texture Loader
const textureLoader = new THREE.TextureLoader();

// 2. Create an array of 6 materials (one for each face of the box)
const boxMaterials = [
  new THREE.MeshStandardMaterial({ color: 0xffb703, roughness: 0.2 }), // Right
  new THREE.MeshStandardMaterial({ color: 0xffb703, roughness: 0.2 }), // Left
  new THREE.MeshStandardMaterial({ color: 0xffb703, roughness: 0.2 }), // Top
  new THREE.MeshStandardMaterial({ color: 0xffb703, roughness: 0.2 }), // Bottom
  new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 }), // FRONT (Will hold image)
  new THREE.MeshStandardMaterial({ color: 0xffb703, roughness: 0.2 })  // Back
];

const boxGeo = new THREE.BoxGeometry(1.8, 2.6, 0.5);
const box = new THREE.Mesh(boxGeo, boxMaterials);
scene.add(box);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

function animate() {
  requestAnimationFrame(animate);
  box.rotation.y += 0.005;
  box.rotation.x = Math.sin(Date.now() * 0.002) * 0.05;
  box.position.y = -0.35 + Math.sin(Date.now() * 0.002) * 0.15; 
  renderer.render(scene, camera);
}
animate();

function adjustCamera() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.position.z = window.innerWidth > 768 ? 10 : 8.5; 
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
  
  // Update box side colors
  box.material.forEach((mat, index) => {
    if (index !== 4) mat.color.set(p.color); // Skip the front face
  });

  // Apply a dynamic cover texture to the front face (Index 4)
  // Note: For now, this loads a placeholder. When you upload your real images, put them in a folder and link them here!
  const coverUrl = `https://via.placeholder.com/400x600/ffffff/333333?text=${encodeURIComponent(p.title)}`;
  textureLoader.load(coverUrl, (texture) => {
    box.material[4].map = texture;
    box.material[4].needsUpdate = true;
  });

  updateMenuState();
  
  previewImages = [
    `https://via.placeholder.com/800x500/ffb703/1a1a1a?text=${encodeURIComponent(p.title)}+Preview+1`,
    `https://via.placeholder.com/800x500/8e4b3e/ffffff?text=${encodeURIComponent(p.title)}+Preview+2`
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
