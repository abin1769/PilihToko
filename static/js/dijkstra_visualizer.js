// static/js/dijkstra_visualizer.js

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const canvas = document.getElementById('dijkstraCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startAnimationBtn');
const startNodeSelect = document.getElementById('startNodeSelect');
const endNodeSelect = document.getElementById('endNodeSelect');
const statusText = document.getElementById('statusText');
const dijkstraStepsTableBody = document.querySelector('#dijkstraStepsTable tbody');

// Ambil data grid, map image, all_graph_nodes, dan all_graph_adjacency dari atribut data- di canvas
const grid = JSON.parse(canvas.dataset.grid);
const mapImageUrl = canvas.dataset.mapImage;
const allGraphNodes = JSON.parse(canvas.dataset.allGraphNodes);
const allGraphAdjacency = JSON.parse(canvas.dataset.allGraphAdjacency);

let isAnimating = false;

// Helper untuk mendapatkan singkatan node (sesuai dengan Python)
function getAbbreviation(nodeName) {
    // Regular expression untuk mencari angka di akhir string
    const match = nodeName.match(/(\d+)$/);
    const numberSuffix = match ? match[1] : '';

    if (nodeName.startsWith("Rumah")) {
        return `R${numberSuffix}` || "R";
    } else if (nodeName.startsWith("Simpang")) {
        return `S${numberSuffix}` || "S";
    } else if (nodeName.startsWith("Toko")) {
        return `T${numberSuffix}` || "T";
    }
    // Fallback jika tidak sesuai pola
    if (nodeName.length > 4) {
        return nodeName.slice(0, 4) + "...";
    }
    return nodeName;
}


// Global variable untuk menyimpan gambar peta setelah dimuat sekali
let mapImageGlobal = new Image();

// Modifikasi initializeMap agar gambar hanya dimuat sekali dan disimpan di global
async function initializeMap() {
    return new Promise(resolve => {
        if (mapImageGlobal.complete && mapImageGlobal.naturalWidth !== 0) {
            // Gambar sudah dimuat, langsung gambar ulang
            const container = document.querySelector('.visual-wrapper');
            // Pastikan container ditemukan sebelum mengakses offsetWidth
            if (!container) {
                console.error("Visual wrapper container not found for map initialization (re-draw).");
                resolve();
                return;
            }
            canvas.width = container.offsetWidth;
            canvas.height = (canvas.width / mapImageGlobal.naturalWidth) * mapImageGlobal.naturalHeight;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(mapImageGlobal, 0, 0, canvas.width, canvas.height);
            resolve();
        } else {
            // Gambar belum dimuat, muat dulu
            mapImageGlobal.src = mapImageUrl;
            mapImageGlobal.onload = () => {
                const container = document.querySelector('.visual-wrapper');
                if (!container) {
                    console.error("Visual wrapper container not found for map initialization (first load).");
                    resolve();
                    return;
                }
                canvas.width = container.offsetWidth;
                canvas.height = (canvas.width / mapImageGlobal.naturalWidth) * mapImageGlobal.naturalHeight;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(mapImageGlobal, 0, 0, canvas.width, canvas.height);
                resolve();
            };
            mapImageGlobal.onerror = () => {
                console.error("Gagal memuat gambar peta di dijkstra_visualizer. Pastikan jalur gambar benar.");
                resolve();
            };
        }
    });
}


async function startSimulation() {
    if (isAnimating) return;
    isAnimating = true;
    startBtn.disabled = true;
    statusText.textContent = 'Mempersiapkan visualisasi...';
    dijkstraStepsTableBody.innerHTML = ''; // Bersihkan tabel sebelumnya

    const startNodeName = startNodeSelect.value;
    const endNodeName = endNodeSelect.value;

    // Validasi input node
    if (!allGraphNodes[startNodeName] || !allGraphNodes[endNodeName]) {
        statusText.textContent = "Error: Titik awal atau tujuan tidak ditemukan di data graf.";
        isAnimating = false;
        startBtn.disabled = false;
        return;
    }

    await initializeMap(); // Panggil initializeMap satu kali di awal

    try {
        const response = await fetch('/get_dijkstra_steps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_node_name: startNodeName,
                end_node_name: endNodeName
            }),
        });

        if (!response.ok) {
            const errorText = await response.text(); // Ambil teks penuh jika bukan JSON
            console.error("Server response was not OK:", response.status, errorText);
            // Coba parse JSON, jika gagal, gunakan pesan fallback
            const errorData = await response.json().catch(() => ({error: "Respon server tidak valid JSON atau ada error tidak terduga."}));
            throw new Error(`Gagal mengambil data dari server: ${errorData.error || response.statusText}`);
        }

        const data = await response.json();
        const path = data.path;
        const distance = data.distance;
        const startNodeLocation = data.start_node_location;
        const endNodeLocation = data.end_node_location;
        const dijkstraSteps = data.dijkstra_steps; // Data iterasi Dijkstra yang sudah disingkat

        statusText.textContent = `Menemukan rute (${distance} langkah). Memulai animasi...`;

        // Dapatkan semua nama node yang diurutkan dari header tabel (atribut title)
        const tableHeaders = Array.from(document.querySelectorAll('#dijkstraStepsTable thead tr:last-child th.node-header'));
        const allNodesHeaderAbbr = tableHeaders.map(th => th.textContent); // Ini sudah singkatan

        // Animasikan Tabel dan Peta Bersamaan
        for (let i = 0; i < dijkstraSteps.length; i++) {
            const step = dijkstraSteps[i];
            
            // --- BAGIAN 1: Update Tabel ---
            const row = dijkstraStepsTableBody.insertRow();
            row.insertCell().textContent = step.iteration_num;
            row.insertCell().textContent = `{${step.unvisited_q.join(', ')}}`;
            row.insertCell().textContent = `{${step.visited_s.join(', ')}}`;
            row.insertCell().textContent = step.current_node || '-';

            for (const nodeNameAbbr of allNodesHeaderAbbr) {
                const cell = row.insertCell();
                const nodeState = step.node_states[nodeNameAbbr];
                if (nodeState) {
                    const distDisplay = nodeState.dist === "∞" ? '∞' : nodeState.dist;
                    const prevDisplay = nodeState.prev === null ? '-' : nodeState.prev;
                    const updatedIterDisplay = nodeState.updated_at_iter !== null ? `|${nodeState.updated_at_iter}` : '';
                    
                    cell.textContent = `(${distDisplay}, ${prevDisplay}${updatedIterDisplay})`;

                    if (nodeState.updated_at_iter === step.iteration_num && step.iteration_num !== 0) {
                        cell.classList.add('updated-node-cell');
                    }
                } else {
                    cell.textContent = '';
                }
            }
            row.classList.add('dijkstra-step-row');

            dijkstraStepsTableBody.scrollTop = dijkstraStepsTableBody.scrollHeight;

            // --- BAGIAN 2: Update Peta Visualisasi per Iterasi ---
            ctx.clearRect(0, 0, canvas.width, canvas.height); // Bersihkan kanvas di setiap frame
            ctx.drawImage(mapImageGlobal, 0, 0, canvas.width, canvas.height); // Gambar ulang peta dasar

            // Gambar semua node di peta terlebih dahulu dengan warna abu-abu default
            for (const nodeNameFull in allGraphNodes) {
                const nodeLoc = allGraphNodes[nodeNameFull];
                drawLocationNode(ctx, grid, canvas, nodeLoc, 'rgba(128, 128, 128, 0.3)', getAbbreviation(nodeNameFull));
            }

            // Gambar visited nodes (warna hijau)
            for(const nodeNameAbbr of step.visited_s) {
                const originalNodeName = Object.keys(allGraphNodes).find(key => getAbbreviation(key) === nodeNameAbbr);
                if (originalNodeName) {
                    const nodeLoc = allGraphNodes[originalNodeName];
                    drawLocationNode(ctx, grid, canvas, nodeLoc, 'rgba(144, 238, 144, 0.5)', nodeNameAbbr);
                }
            }
            
            // Gambar current node (warna oranye)
            if (step.current_node) {
                const originalNodeName = Object.keys(allGraphNodes).find(key => getAbbreviation(key) === step.current_node);
                if (originalNodeName) {
                    const currentNodeLoc = allGraphNodes[originalNodeName];
                    drawLocationNode(ctx, grid, canvas, currentNodeLoc, 'rgba(255, 165, 0, 0.7)', step.current_node);

                    // --- Visualisasi Jalur yang Sedang Dievaluasi (Kuning Putus-putus) ---
                    const currentNeighbors = allGraphAdjacency[originalNodeName] || []; // Gunakan nama lengkap
                    for (const [neighborNameFull, weight] of currentNeighbors) {
                        const neighborLoc = allGraphNodes[neighborNameFull];
                        // Gambar jika tetangga belum visited DAN itu bukan current node itu sendiri (opsional)
                        if (neighborLoc && !step.visited_s.includes(getAbbreviation(neighborNameFull)) && neighborNameFull !== originalNodeName) {
                             drawTemporaryEdge(ctx, grid, canvas, currentNodeLoc, neighborLoc, 'rgba(255, 255, 0, 0.6)', [5, 5]); // Garis kuning putus-putus
                        }
                    }

                    // --- Visualisasi Jalur Terpendek ke Current Node (Garis Ungu Solid) ---
                    const currentNodeState = step.node_states[step.current_node]; // Ambil state current node yang sudah disingkat
                    if (currentNodeState && currentNodeState.prev && currentNodeState.prev !== '-') { // Pastikan ada predecessor
                        const prevNodeAbbr = currentNodeState.prev; // Predecessor yang sudah disingkat
                        const prevNodeFull = Object.keys(allGraphNodes).find(key => getAbbreviation(key) === prevNodeAbbr);
                        if (prevNodeFull) {
                            const prevNodeLoc = allGraphNodes[prevNodeFull];
                            if (prevNodeLoc) {
                                drawTemporaryEdge(ctx, grid, canvas, prevNodeLoc, currentNodeLoc, '#4f46e5'); // Garis ungu solid
                            }
                        }
                    }
                }
            }
            
            await sleep(300); // Jeda antar iterasi tabel
        }

        statusText.textContent = `Visualisasi Selesai! Jalur terpendek dari ${startNodeName} ke ${endNodeName} adalah ${distance} langkah.`;

        // --- Gambar Jalur Final Setelah Semua Iterasi Selesai ---
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Bersihkan peta untuk gambar jalur final
        ctx.drawImage(mapImageGlobal, 0, 0, canvas.width, canvas.height); // Gambar ulang peta dasar
        drawLocationNode(ctx, grid, canvas, startNodeLocation, '#10b981', startNodeName); // Start node final
        drawLocationNode(ctx, grid, canvas, endNodeLocation, '#ef4444', endNodeName);     // End node final
        if (path && path.length > 0) {
            await animatePath(ctx, grid, canvas, path, 0); // Animasikan jalur terakhir
        } else {
            console.warn("Jalur akhir kosong, tidak bisa dianimasikan.");
        }

    } catch (error) {
        statusText.textContent = `Error: ${error.message}`;
        console.error("Kesalahan simulasi:", error);
    } finally {
        isAnimating = false;
        startBtn.disabled = false;
    }
}

// Fungsi-fungsi pembantu
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

// Fungsi helper untuk menggambar garis sementara / edge
function drawTemporaryEdge(ctx, grid, canvas, startCoord, endCoord, color, dash = []) {
    const cellSizeX = canvas.width / grid[0].length;
    const cellSizeY = canvas.height / grid.length;

    const startCanvasX = startCoord[0] * cellSizeX + cellSizeX / 2;
    const startCanvasY = startCoord[1] * cellSizeY + cellSizeY / 2;
    const endCanvasX = endCoord[0] * cellSizeX + cellSizeX / 2;
    const endCanvasY = endCoord[1] * cellSizeY + cellSizeY / 2;

    ctx.beginPath();
    ctx.moveTo(startCanvasX, startCanvasY);
    ctx.lineTo(endCanvasX, endCanvasY);
    ctx.strokeStyle = color;
    ctx.lineWidth = Math.max(2, canvas.width / 200);
    ctx.lineCap = 'round';
    
    // Atur garis putus-putus jika parameter dash diberikan
    if (dash.length > 0) {
        ctx.setLineDash(dash);
    } else {
        ctx.setLineDash([]); // Reset ke garis solid
    }

    ctx.stroke();
    ctx.setLineDash([]); // Penting: Reset dash setelah stroke untuk gambar berikutnya
}


// Event Listener untuk tombol
startBtn.addEventListener('click', startSimulation);

// Inisialisasi peta saat halaman pertama kali dimuat
window.addEventListener('load', initializeMap);