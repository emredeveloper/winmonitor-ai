# -*- coding: utf-8 -*-
import platform
import psutil
import requests
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from win10toast import ToastNotifier

def get_system_info():
    """Sistem bilgilerini toplar ve formatlar."""
    info = []
    info.append(f"İşletim Sistemi: {platform.system()} {platform.release()}")
    info.append(f"Bilgisayar Adı: {platform.node()}")
    info.append(f"CPU Kullanımı: {psutil.cpu_percent():.1f}%")
    info.append(f"RAM Kullanımı: {psutil.virtual_memory().percent:.1f}%")
    
    try:
        ip = requests.get('https://api.ipify.org', timeout=3, headers={'User-Agent': 'SystemInfo/1.0'}).text
        if ip.count('.') == 4 and ip.replace('.', '').isdigit():
            info.append(f"IP Adresiniz: {ip}")
    except Exception as e:
        info.append(f"IP Adresi Alınamadı: {str(e)}")
    
    return "\n".join(info)

def get_disk_info():
    """Disk bilgilerini toplar."""
    disk_info = []
    for disk in psutil.disk_partitions():
        if disk.mountpoint in ['C:', 'C:\\']:
            usage = psutil.disk_usage(disk.mountpoint)
            disk_info.append(f"Disk {disk.mountpoint}: {usage.used//1024//1024} MB / {usage.total//1024//1024} MB")
    return "\n".join(disk_info)

def get_network_info():
    """Ağ bilgilerini toplar."""
    net_info = []
    net_io = psutil.net_io_counters()
    net_info.append(f"Toplam Gönderilen Veri: {net_io.bytes_sent} byte")
    net_info.append(f"Toplam Alınan Veri: {net_io.bytes_recv} byte")
    return "\n".join(net_info)

def get_cpu_temp():
    """İşlemci sıcaklığını ölçer."""
    try:
        if platform.system() == 'Windows':
            temps = psutil.sensors_temperatures()
            for entry in temps.get('Coretemp-isa-0028', []):
                if entry.label == 'Core 0':
                    return f"İşlemci Sıcaklığı: {entry.current}°C"
            return "İşlemci sıcaklığı alınamadı."
        return "İşlemci sıcaklığı bu sistemde desteklenmiyor."
    except Exception as e:
        return f"İşlemci sıcaklığı hatası: {str(e)}"

def analyze_with_deepscaler(info):
    """Verilen metni ollama ile analiz eder ve özetler."""
    try:
        process = subprocess.Popen(
            ['ollama', 'run', 'deepscaler'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        output, error = process.communicate(input=info, timeout=30)
        
        if process.returncode == 0:
            return output.strip()[:500]
        return f"Analiz Hatası: {error.strip()}"
    
    except subprocess.SubprocessError:
        return "Ollama işlemi sırasında bir hata oluştu."
    except Exception as e:
        return f"Genel hata: {str(e)}"

def show_notification(message, duration=10, icon_path=None):
    """Windows bildirimini gösterir."""
    try:
        toast = ToastNotifier()
        if len(message) > 256:
            message = message[:253] + "..."
        toast.show_toast(
            "Sistem Raporu",
            message,
            duration=duration,
            icon_path=icon_path,
            threaded=True
        )
        return True
    except Exception as e:
        print(f"Bildirim hatası: {str(e)}")
        return False

def save_report_to_file(report, filename="system_report"):
    """Raporu metin dosyasına kaydeder."""
    try:
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_'))
        if not filename:
            filename = "system_report"
        
        with open(f"{filename}.txt", "w", encoding="utf-8") as file:
            file.write(report)
        print(f"Rapor {filename}.txt dosyasına kaydedildi.")
        return True
    except Exception as e:
        print(f"Dosya kaydedilirken hata oluştu: {str(e)}")
        return False

def customize_report():
    """Kullanıcıya rapor içeriğini özelleştirme seçeneği sunar."""
    print("\nRaporunuz için lütfen aşağıdaki seçimleri yapın:")
    print("1. Sistem Bilgisi")
    print("2. Ağ Bilgisi")
    print("3. Disk Bilgisi")
    print("4. İşlemci Sıcaklığı")
    print("5. Tümü")
    
    choices = input("Seçiminiz (1-5): ")
    selected = []
    
    if choices == '1':
        selected.append(get_system_info())
    elif choices == '2':
        selected.append(get_network_info())
    elif choices == '3':
        selected.append(get_disk_info())
    elif choices == '4':
        selected.append(get_cpu_temp())
    elif choices == '5':
        selected = [get_system_info(), get_network_info(), get_disk_info(), get_cpu_temp()]
    else:
        print("Yanlış seçim. Varsayılan olarak tüm bilgiler eklenmiştir.")
        selected = [get_system_info(), get_network_info(), get_disk_info(), get_cpu_temp()]
    
    return "\n".join(selected)

def auto_generate_report():
    """Belirli aralıklarla otomatik rapor oluşturur."""
    while True:
        system_info = get_system_info()
        analysis_result = analyze_with_deepscaler(system_info)
        show_notification(analysis_result)
        threading.Event().wait(3600)  # 1 saat bekle

def create_gui():
    """Grafik kullanıcı arayüzü oluşturur."""
    root = tk.Tk()
    root.title("Sistem Raporu")
    
    report_text = tk.Text(root, wrap=tk.WORD)
    report_text.pack(padx=10, pady=10)
    
    def generate_report():
        report = get_system_info()
        report_text.delete(1.0, tk.END)
        report_text.insert(tk.END, report)
    
    generate_button = ttk.Button(root, text="Raporu Oluştur", command=generate_report)
    generate_button.pack(pady=10)
    
    root.mainloop()

def main():
    print("Sistem Raporu Uygulaması")
    print("-------------------------")

    system_info = get_system_info()
    print("\nSistem Bilgileri:\n", system_info)

    analysis_result = analyze_with_deepscaler(system_info)
    print("\nAnaliz Sonucu:\n", analysis_result)

    save_report_to_file(system_info)

    threading.Thread(target=auto_generate_report, daemon=True).start()

    create_gui()

    show_notification(analysis_result[:256])


if __name__ == "__main__":
    main()
