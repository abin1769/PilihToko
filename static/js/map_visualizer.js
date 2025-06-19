window.addEventListener('load', function() {
    const canvas = document.getElementById('mapCanvas');
    if (!canvas) {
        return;
    }

    const grid = JSON.parse(canvas.dataset.grid);
    const path = JSON.parse(canvas.dataset.path);
    const startNode = JSON.parse(canvas.dataset.startNode);
    const endNode = JSON.parse(canvas.dataset.endNode);
    const mapImageUrl = canvas.dataset.mapImage;

    const ctx = canvas.getContext('2d');
    const mapImage = new Image();
    mapImage.src = mapImageUrl;

    mapImage.onload = function() {
        // Atur ukuran canvas agar responsif
        const container = document.querySelector('.route-visual-container');
        canvas.width = container.offsetWidth;
        canvas.height = (canvas.width / this.naturalWidth) * this.naturalHeight;

        // Gambar denah peta sebagai latar belakang
        ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);

        // Gambar titik Mulai dan Tujuan di atas peta
        drawLocationNode(startNode[0], startNode[1], '#10b981', 'Mulai');
        drawLocationNode(endNode[0], endNode[1], '#ef4444', 'Tujuan');
        
        // Memulai animasi menggambar jalur (jika ada)
        if (path && path.length > 0) {
            animatePath(0);
        }
    };

    // --- FUNGSI BARU UNTUK ANIMASI ---
    function animatePath(index) {
        // Hentikan animasi jika sudah mencapai akhir jalur
        if (index >= path.length) {
            return;
        }

        const cellSizeX = canvas.width / grid[0].length;
        const cellSizeY = canvas.height / grid.length;

        // Ambil titik saat ini
        const [x, y] = path[index];
        const canvasX = x * cellSizeX + cellSizeX / 2;
        const canvasY = y * cellSizeY + cellSizeY / 2;
        
        // Gambar garis dari titik sebelumnya ke titik saat ini
        if (index > 0) {
            const [prevX, prevY] = path[index - 1];
            const prevCanvasX = prevX * cellSizeX + cellSizeX / 2;
            const prevCanvasY = prevY * cellSizeY + cellSizeY / 2;

            ctx.beginPath();
            ctx.moveTo(prevCanvasX, prevCanvasY);
            ctx.lineTo(canvasX, canvasY);
            ctx.strokeStyle = '#6d28d9'; // Warna garis ungu
            ctx.lineWidth = Math.max(3, canvas.width / 150); // Garis lebih tebal
            ctx.lineCap = 'round';
            ctx.stroke();
        }

        // Atur jeda waktu sebelum menggambar segmen berikutnya
        // Angka 50 di sini adalah delay dalam milidetik (bisa diubah untuk mengatur kecepatan)
        setTimeout(function() {
            // Memanggil fungsi ini lagi untuk titik selanjutnya, menciptakan loop animasi
            requestAnimationFrame(() => animatePath(index + 1));
        }, 50); 
    }

    function drawLocationNode(gridX, gridY, color, text) {
        const cellSizeX = canvas.width / grid[0].length;
        const cellSizeY = canvas.height / grid.length;
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

    mapImage.onerror = function() {
        console.error("Gagal memuat gambar peta dari:", mapImageUrl);
    };
});