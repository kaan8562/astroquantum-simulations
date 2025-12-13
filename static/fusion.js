document.addEventListener('DOMContentLoaded', function() {
    // Slider event listener'ları
    document.getElementById('temperature').addEventListener('input', function() {
        document.getElementById('temp-value').textContent = this.value;
    });

    document.getElementById('gamow-energy').addEventListener('input', function() {
        document.getElementById('gamow-value').textContent = this.value;
    });

    // İlk grafiği çiz
    updateFusionGraph();
});

async function updateFusionGraph() {
    const loading = document.getElementById('loading');
    const graph = document.getElementById('fusion-graph');
    
    loading.style.display = 'block';
    graph.style.opacity = '0.5';
    
    const data = {
        T: parseFloat(document.getElementById('temperature').value) * 1e6,
        E_G: parseFloat(document.getElementById('gamow-energy').value)
    };
    
    try {
        const response = await fetch('/fusion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Grafiği güncelle
        graph.src = 'data:image/png;base64,' + result.graph;
        graph.style.opacity = '1';
        
        // Gamow Peak'i göster
        document.getElementById('peak-result').textContent = result.peak;
        
    } catch (error) {
        console.error('Hata:', error);
        alert('Grafik güncellenirken bir hata oluştu. Lütfen konsolu kontrol edin.');
    } finally {
        loading.style.display = 'none';
    }
}

function resetFusion() {
    document.getElementById('temperature').value = 15;
    document.getElementById('gamow-energy').value = 500;
    
    document.getElementById('temp-value').textContent = '15.0';
    document.getElementById('gamow-value').textContent = '500';
    
    updateFusionGraph();
}