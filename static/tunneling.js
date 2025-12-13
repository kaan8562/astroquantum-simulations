// Slider değerlerini güncelle
document.addEventListener('DOMContentLoaded', function() {
    // Slider event listener'ları
    const sliders = [
        {id: 'barrier-height', valueId: 'height-value'},
        {id: 'barrier-width', valueId: 'width-value'},
        {id: 'nuclei-count', valueId: 'nuclei-value'},
        {id: 'decay-prob', valueId: 'prob-value'}
    ];

    sliders.forEach(slider => {
        const element = document.getElementById(slider.id);
        if (element) {
            element.addEventListener('input', function() {
                document.getElementById(slider.valueId).textContent = this.value;
            });
        }
    });

    // İlk grafiği çiz
    updateTunnelingGraph();
});

// Tünelleme grafiğini güncelle
async function updateTunnelingGraph() {
    const loading = document.getElementById('loading');
    const graph = document.getElementById('tunneling-graph');
    
    loading.style.display = 'block';
    graph.style.opacity = '0.5';
    
    const data = {
        V0: parseFloat(document.getElementById('barrier-height').value),
        L: parseFloat(document.getElementById('barrier-width').value) * 1e-10,
        N0: parseInt(document.getElementById('nuclei-count').value),
        p: parseFloat(document.getElementById('decay-prob').value)
    };
    
    try {
        const response = await fetch('/tunneling', {
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
        
        // Yarı ömrü göster
        document.getElementById('half-life-result').textContent = result.half_life;
        
    } catch (error) {
        console.error('Hata:', error);
        alert('Simülasyon çalıştırılırken bir hata oluştu. Lütfen konsolu kontrol edin.');
    } finally {
        loading.style.display = 'none';
    }
}

// Parametreleri sıfırla
function resetTunneling() {
    document.getElementById('barrier-height').value = 10;
    document.getElementById('barrier-width').value = 1.0;
    document.getElementById('nuclei-count').value = 1000;
    document.getElementById('decay-prob').value = 0.01;
    
    document.getElementById('height-value').textContent = '10';
    document.getElementById('width-value').textContent = '1.0';
    document.getElementById('nuclei-value').textContent = '1000';
    document.getElementById('prob-value').textContent = '0.01';
    
    updateTunnelingGraph();
}