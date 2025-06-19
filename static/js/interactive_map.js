// static/js/interactive_map.js

// Deklarasi variabel global untuk mengelola state
let activeCard = null;
let mapWrapper = null; 

// Inisialisasi mapWrapper setelah DOM sepenuhnya dimuat
document.addEventListener('DOMContentLoaded', () => {
    mapWrapper = document.getElementById('route-visual-wrapper');
    // Jika mapWrapper tidak ditemukan, berarti halaman ini tidak membutuhkannya (misal: halaman harga)
    // atau ada masalah di HTML. Log peringatan saja.
    if (!mapWrapper) {
        console.warn("Element with ID 'route-visual-wrapper' not found. Interactive map features might not work on this page.");
    }
});


function toggleRoute(cardElement) {
    if (!mapWrapper) {
        console.error("mapWrapper not initialized. Cannot toggle route. Make sure DOM is loaded and element exists.");
        return;
    }

    // Jika card yang sama diklik lagi, sembunyikan peta
    if (activeCard === cardElement) {
        mapWrapper.classList.add('visual-wrapper-hidden');
        cardElement.classList.remove('active-card');
        activeCard = null;
        return;
    }
    
    // Jika ada card lain yang aktif, nonaktifkan dulu
    if (activeCard) {
        activeCard.classList.remove('active-card');
    }
    
    // Set card yang baru diklik sebagai aktif
    activeCard = cardElement;
    activeCard.classList.add('active-card');
    
    // Pindahkan wrapper peta ke setelah card yang aktif
    cardElement.insertAdjacentElement('afterend', mapWrapper);
    
    // Pastikan data-toko-info ada dan valid JSON
    let tokoInfo;
    try {
        tokoInfo = JSON.parse(cardElement.dataset.tokoInfo);
    } catch (e) {
        console.error("Error parsing tokoInfo from data-attribute:", e);
        console.error("Raw data-toko-info:", cardElement.dataset.tokoInfo);
        return; // Hentikan eksekusi jika parsing gagal
    }
    
    // Tampilkan wrapper peta
    mapWrapper.classList.remove('visual-wrapper-hidden');
    
    // Set nama toko di judul visualisasi
    // Pastikan ID 'toko-tujuan-nama' ada di HTML
    const tokoTujuanNamaElement = document.getElementById('toko-tujuan-nama');
    if (tokoTujuanNamaElement) {
        tokoTujuanNamaElement.innerText = tokoInfo.nama;
    } else {
        console.warn("Element with ID 'toko-tujuan-nama' not found.");
    }
    
    // Gambar peta dengan rute
    drawMap(tokoInfo);

    // Gulir ke tampilan peta (opsional, bisa diaktifkan jika perlu)
    // mapWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


function drawMap(tokoInfo) {
    const canvas = document.getElementById('mapCanvas');
    if (!canvas) {
        console.error("Canvas element not found.");
        return;
    }
    
    const ctx = canvas.getContext('2d');

    let grid;
    let mapImageUrl;
    let rumahAsal;

    try {
        grid = JSON.parse(canvas.dataset.grid);
        mapImageUrl = canvas.dataset.mapImage;
        rumahAsal = JSON.parse(canvas.dataset.rumahAsal);
    } catch (e) {
        console.error("Error parsing map data from canvas dataset:", e);
        return;
    }
    
    const path = tokoInfo.jalur;
    const endNode = tokoInfo.lokasi;
    const startNode = rumahAsal.lokasi;

    const mapImage = new Image();
    mapImage.src = mapImageUrl;

    mapImage.onload = () => {
        const container = mapWrapper; 
        if (!container) {
            console.error("Map wrapper container not found.");
            return;
        }
        canvas.width = container.offsetWidth - 48; 
        canvas.height = (canvas.width / mapImage.naturalWidth) * mapImage.naturalHeight;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);
        
        drawLocationNode(ctx, grid, canvas, startNode, '#10b981', rumahAsal.nama);
        drawLocationNode(ctx, grid, canvas, endNode, '#ef4444', tokoInfo.nama);

        if (path && path.length > 0) {
            animatePath(ctx, grid, canvas, path, 0);
        } else {
            console.warn("⚠️ PERINGATAN: Animasi rute tidak tersedia atau kosong.");
        }
    };
    
    mapImage.onerror = () => console.error("❌ GAGAL: Gambar peta tidak bisa dimuat. Pastikan jalur gambar benar.");
}

function animatePath(ctx, grid, canvas, path, index) {
    if (index >= path.length) {
        return Promise.resolve();
    }
    return new Promise(resolve => {
        const cellSizeX = canvas.width / grid[0].length;
        const cellSizeY = canvas.height / grid.length;
        
        if (index > 0) {
            const [prevX, prevY] = path[index - 1];
            const [currX, currY] = path[index];
            const prevCanvasX = prevX * cellSizeX + cellSizeX / 2;
            const prevCanvasY = prevY * cellSizeY + cellSizeY / 2;
            const currCanvasX = currX * cellSizeX + cellSizeX / 2;
            const currCanvasY = currY * cellSizeY + cellSizeY / 2;
            
            ctx.beginPath();
            ctx.moveTo(prevCanvasX, prevCanvasY);
            ctx.lineTo(currCanvasX, currCanvasY);
            ctx.strokeStyle = '#6d28d9'; // Warna ungu
            ctx.lineWidth = Math.max(3, canvas.width / 150);
            ctx.lineCap = 'round';
            ctx.stroke();
        }
        
        setTimeout(() => {
            requestAnimationFrame(() => {
                animatePath(ctx, grid, canvas, path, index + 1).then(resolve);
            });
        }, 30);
    });
}

function drawLocationNode(ctx, grid, canvas, node, color, text) { 
    const cellSizeX = canvas.width / grid[0].length; 
    const cellSizeY = canvas.height / grid.length; 
    const [gridX, gridY] = node; 
    const x = gridX * cellSizeX + cellSizeX / 2; 
    const y = gridY * cellSizeY + cellSizeY / 2; 
    const radius = Math.max(5, canvas.width / 80); 

    ctx.fillStyle = color; 
    ctx.strokeStyle = 'white'; 
    ctx.lineWidth = Math.max(1, canvas.width / 250); 

    ctx.beginPath(); 
    ctx.arc(x, y, radius, 0, 2 * Math.PI); 
    ctx.fill(); 
    ctx.stroke(); 
    
    ctx.fillStyle = 'black'; 
    ctx.font = `bold ${Math.max(10, canvas.width/50)}px Inter`; 
    ctx.textAlign = 'center'; 
    ctx.fillText(text, x, y + radius + 15); 
}

// Event Listener untuk tombol
// Karena interactive_map.js ini untuk 'toggleRoute' di rekomendasi/hasil_terdekat,
// tidak ada event listener untuk tombol di sini.