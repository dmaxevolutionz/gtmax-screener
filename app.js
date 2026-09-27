let globalStockData = null;

// Mengambil data dari data.json
async function fetchDashboardData() {
    try {
        const response = await fetch('data.json');
        globalStockData = await response.json();

        // Update Header & Info IHSG
        document.getElementById('last-updated').innerText = `Terakhir diperbarui: ${globalStockData.updated_at || '-'}`;
        document.getElementById('ihsg-val').innerText = globalStockData.ihsg.value;
        document.getElementById('ihsg-status').innerText = globalStockData.ihsg.status;

        // Render Tampilan Awal (Semua Saham)
        renderStocks(globalStockData.all_stocks);
    } catch (error) {
        console.error('Gagal membaca data.json:', error);
        document.getElementById('stock-container').innerHTML = `
            <p class="text-red-500 col-span-3 text-center py-8">Gagal memuat data dari data.json. Pastikan file tersedia.</p>
        `;
    }
}

// Menampilkan daftar saham ke kontainer
function renderStocks(stocksList) {
    const container = document.getElementById('stock-container');
    if (!stocksList || stocksList.length === 0) {
        container.innerHTML = `<p class="text-gray-500 col-span-3 text-center py-8">Tidak ada emiten ditemukan.</p>`;
        return;
    }
    
    // Menggunakan modul stockCard.js
    container.innerHTML = stocksList.map(stock => createStockCardElement(stock)).join('');
}

// Logika Filter Tab Button
function filterStocks(type) {
    if (!globalStockData) return;

    if (type === 'all') renderStocks(globalStockData.all_stocks);
    else if (type === 'top_10') renderStocks(globalStockData.top_10_entry);
    else if (type === 'swing') renderStocks(globalStockData.swing_setup);
}

// Jalankan otomatis saat halaman selesai dimuat
document.addEventListener('DOMContentLoaded', fetchDashboardData);