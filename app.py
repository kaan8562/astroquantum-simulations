from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random

app = Flask(__name__)

# ========== FÜZYON SİMÜLASYONU ==========
@app.route('/fusion', methods=['POST'])
def fusion():
    data = request.json
    T = float(data.get('T', 15e6))
    E_G = float(data.get('E_G', 500))
    
    # formüller
    E = np.linspace(1, 50, 300)
    P_tunnel = np.exp(-np.sqrt(E_G/E))
    k_B = 8.617e-8  # Boltzmann sabiti
    f_MB = np.sqrt(E) * np.exp(-E/(k_B*T))  # Maxwell-Boltzmann
    fusion_prob = P_tunnel * f_MB
    
    # Grafik
    plt.figure(figsize=(10, 6))
    plt.plot(E, P_tunnel, 'b-', linewidth=2, label='Tünelleme Olasılığı (P_tunnel)')
    plt.plot(E, f_MB/f_MB.max(), 'g-', linewidth=2, label='Maxwell-Boltzmann Dağılımı (f_MB)')
    plt.plot(E, fusion_prob/fusion_prob.max(), 'r-', linewidth=3, label='Füzyon Olasılığı')
    
    # Gamow Peak
    peak_idx = np.argmax(fusion_prob)
    peak_energy = E[peak_idx]
    plt.plot(peak_energy, fusion_prob[peak_idx]/fusion_prob.max(), 'ro', markersize=10)
    plt.annotate(f'Gamow Peak: {peak_energy:.1f} keV', 
                 xy=(peak_energy, fusion_prob[peak_idx]/fusion_prob.max()),
                 xytext=(peak_energy+5, fusion_prob[peak_idx]/fusion_prob.max()),
                 arrowprops=dict(arrowstyle='->', color='red'))
    
    plt.xlabel('Enerji (keV)', fontsize=12)
    plt.ylabel('Normalize Olasılık', fontsize=12)
    plt.title(f'Gamow Penceresi Simülasyonu (T={T/1e6:.1f} MK, E_G={E_G} keV)', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # görsel üretme
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    
    return jsonify({'graph': img_base64, 'peak': f'{peak_energy:.1f}'})

# ========== TÜNELLEME SİMÜLASYONU ==========
@app.route('/tunneling', methods=['POST'])
def tunneling():
    data = request.json
    V0 = float(data.get('V0', 10))
    L = float(data.get('L', 1e-10))
    N0 = int(data.get('N0', 1000))
    
    # 1. Tünelleme Grafiği
    E = np.linspace(0.1, 0.9*V0, 200)
    m = 9.11e-31
    hbar = 1.0545718e-34
    kappa = np.sqrt(2*m*(V0 - E)) / hbar
    T_prob = np.exp(-2 * kappa * L)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Tünelleme grafiği
    ax1.plot(E, T_prob, 'b-', linewidth=2)
    ax1.fill_between([0, L*1e10], [V0, V0], color='red', alpha=0.3, label=f'Bariyer: {V0} eV')
    ax1.set_xlabel('Enerji (eV)', fontsize=12)
    ax1.set_ylabel('Tünelleme Olasılığı', fontsize=12)
    ax1.set_title(f'Kuantum Tünelleme (V0={V0} eV, L={L:.1e} m)', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Alfa Bozunma Simülasyonu
    T_room = 300  # K
    eV_to_J = 1.602176634e-19
    E_avg_J = 1.5 * 8.617e-8 * T_room * eV_to_J  # Joules
    V0_J = V0 * eV_to_J
    
    if V0_J > E_avg_J:
        m_alpha = 6.644e-27  # Alpha parçacık kütlesi (kg)
        hbar = 1.0545718e-34
        kappa = np.sqrt(2 * m_alpha * (V0_J - E_avg_J)) / hbar
        tunnel_prob = np.exp(-2 * kappa * L)  # WKB tünelleme olasılığı
        tunnel_prob = np.clip(tunnel_prob, 1e-6, 0.99)  
    else:
        tunnel_prob = 0.5  # 
    
    times = []
    for _ in range(N0):
        t = 0
        while random.random() > tunnel_prob:
            t += 1
            if t > 10000:
                break
        times.append(t)
    
    half_life = np.median(times) if times else 0
    
    ax2.hist(times, bins=30, alpha=0.7, color='blue', label='Bozunma Zamanları')
    ax2.axvline(half_life, color='red', linestyle='--', linewidth=2, 
                label=f'Yarı Ömür: {half_life:.1f}')
    ax2.set_xlabel('Zaman (birim)', fontsize=12)
    ax2.set_ylabel('Çekirdek Sayısı', fontsize=12)
    ax2.set_title(f'Alfa Bozunma Simülasyonu (N0={N0}, V0={V0} eV, L={L:.1e} m)', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    # görsel üretme
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    
    return jsonify({
        'graph': img_base64, 
        'half_life': f'{half_life:.1f}',
        'decayed': len([t for t in times if t > 0])
    })

# ========== SAYFALAR ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fusion_sim')
def fusion_sim():
    return render_template('fusion.html')

@app.route('/tunneling_sim')
def tunneling_sim():
    return render_template('tunneling.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)