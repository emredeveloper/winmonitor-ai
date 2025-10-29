# -*- coding: utf-8 -*-
import platform
import psutil
import requests
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from win10toast import ToastNotifier

def get_system_info(include_ip=True, ip_timeout=3):
    """Sistem bilgilerini toplar ve formatlar."""
    info = []
    warnings = []
    info.append(f"İşletim Sistemi: {platform.system()} {platform.release()}")
    info.append(f"Bilgisayar Adı: {platform.node()}")
    info.append(f"CPU Kullanımı: {psutil.cpu_percent():.1f}%")
    info.append(f"RAM Kullanımı: {psutil.virtual_memory().percent:.1f}%")

    if include_ip:
        try:
            response = requests.get(
                'https://api.ipify.org',
                timeout=ip_timeout,
                headers={'User-Agent': 'SystemInfo/1.0'}
            )
            response.raise_for_status()
            ip = response.text
            if ip.count('.') == 4 and ip.replace('.', '').isdigit():
                info.append(f"IP Adresiniz: {ip}")
            else:
                warnings.append("IP adresi geçersiz bir format döndürdü.")
        except Exception as exc:
            warnings.append(f"IP adresi alınamadı: {exc}")

    return "\n".join(info), warnings

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
    warnings = []
    if platform.system() != 'Windows':
        warnings.append("İşlemci sıcaklığı bu sistemde desteklenmiyor.")
        return "", warnings

    try:
        temps = psutil.sensors_temperatures()
        for entry in temps.get('Coretemp-isa-0028', []):
            if entry.label == 'Core 0':
                return f"İşlemci Sıcaklığı: {entry.current}°C", warnings
        warnings.append("İşlemci sıcaklığı alınamadı.")
    except Exception as exc:
        warnings.append(f"İşlemci sıcaklığı hatası: {exc}")

    return "", warnings

def analyze_with_deepscaler(info, timeout=30):
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
    except FileNotFoundError:
        return "", "Ollama bulunamadı. Lütfen kurulumunu doğrulayın."
    except Exception as exc:
        return "", f"Ollama başlatılamadı: {exc}"

    try:
        output, error = process.communicate(input=info, timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        _, error = process.communicate()
        return "", "Ollama yanıt vermedi (zaman aşımı)."
    except Exception as exc:
        process.kill()
        return "", f"Ollama iletişim hatası: {exc}"

    if process.returncode == 0:
        return output.strip()[:500], ""

    error_message = error.strip() if error else "Bilinmeyen hata."
    return "", f"Analiz hatası: {error_message}"

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

def compose_report(include_ip=True, include_network=False, include_disk=False, include_temp=False, ip_timeout=3):
    """Seçilen seçeneklere göre rapor oluşturur."""
    sections = []
    warnings = []

    system_info, system_warnings = get_system_info(include_ip=include_ip, ip_timeout=ip_timeout)
    sections.append(system_info)
    warnings.extend(system_warnings)

    if include_network:
        network_info = get_network_info()
        if network_info:
            sections.append(network_info)

    if include_disk:
        disk_info = get_disk_info()
        if disk_info:
            sections.append(disk_info)

    if include_temp:
        cpu_temp, temp_warnings = get_cpu_temp()
        if cpu_temp:
            sections.append(cpu_temp)
        warnings.extend(temp_warnings)

    report = "\n\n".join(filter(None, sections))
    return report, warnings


def customize_report():
    """Kullanıcıya rapor içeriğini özelleştirme seçeneği sunar."""
    print("\nRaporunuz için lütfen aşağıdaki seçimleri yapın:")
    print("1. Sistem Bilgisi")
    print("2. Ağ Bilgisi")
    print("3. Disk Bilgisi")
    print("4. İşlemci Sıcaklığı")
    print("5. Tümü")

    choices = input("Seçiminiz (1-5): ")

    mapping = {
        '1': dict(include_network=False, include_disk=False, include_temp=False),
        '2': dict(include_network=True, include_disk=False, include_temp=False),
        '3': dict(include_network=False, include_disk=True, include_temp=False),
        '4': dict(include_network=False, include_disk=False, include_temp=True),
        '5': dict(include_network=True, include_disk=True, include_temp=True),
    }

    options = mapping.get(choices)
    if options is None:
        print("Yanlış seçim. Varsayılan olarak tüm bilgiler eklenmiştir.")
        options = mapping['5']

    report, warnings = compose_report(include_ip=True, **options)
    for warning in warnings:
        print(f"Uyarı: {warning}")
    return report

def auto_generate_report(stop_event, config_getter, status_callback):
    """Belirli aralıklarla otomatik rapor oluşturur."""
    while not stop_event.is_set():
        config = config_getter()
        report, warnings = compose_report(
            include_ip=config.get('include_ip', True),
            include_network=config.get('include_network', False),
            include_disk=config.get('include_disk', False),
            include_temp=config.get('include_temp', False),
            ip_timeout=config.get('ip_timeout', 3)
        )

        for warning in warnings:
            status_callback(warning, level="warning")

        analysis, error = analyze_with_deepscaler(report, timeout=config.get('analysis_timeout', 30))
        if analysis:
            show_notification(analysis)
        if error:
            status_callback(error, level="error")

        interval = config.get('interval', 3600)
        if interval <= 0:
            interval = 3600

        if stop_event.wait(interval):
            break

def create_gui():
    """Grafik kullanıcı arayüzü oluşturur."""
    root = tk.Tk()
    root.title("Sistem Raporu")

    include_network_var = tk.BooleanVar(value=True)
    include_disk_var = tk.BooleanVar(value=True)
    include_temp_var = tk.BooleanVar(value=False)
    include_ip_var = tk.BooleanVar(value=True)

    interval_var = tk.StringVar(value="3600")
    ip_timeout_var = tk.StringVar(value="3")
    analysis_timeout_var = tk.StringVar(value="30")

    status_var = tk.StringVar(value="Hazır.")

    report_text = tk.Text(root, wrap=tk.WORD, height=20, width=80)
    report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

    controls_frame = ttk.Frame(root)
    controls_frame.pack(fill=tk.X, padx=10, pady=10)

    scope_frame = ttk.LabelFrame(controls_frame, text="Rapor Kapsamı")
    scope_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    ttk.Checkbutton(scope_frame, text="Ağ Bilgisi", variable=include_network_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
    ttk.Checkbutton(scope_frame, text="Disk Bilgisi", variable=include_disk_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
    ttk.Checkbutton(scope_frame, text="İşlemci Sıcaklığı", variable=include_temp_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
    ttk.Checkbutton(scope_frame, text="IP Adresini Dahil Et", variable=include_ip_var).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)

    schedule_frame = ttk.LabelFrame(controls_frame, text="Otomatik Oluşturma")
    schedule_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    ttk.Label(schedule_frame, text="Sıklık (sn)").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
    interval_box = ttk.Combobox(
        schedule_frame,
        textvariable=interval_var,
        values=["300", "900", "1800", "3600", "7200"],
        state="readonly"
    )
    interval_box.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

    ttk.Label(schedule_frame, text="IP Zaman Aşımı (sn)").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
    ip_timeout_entry = ttk.Entry(schedule_frame, textvariable=ip_timeout_var, width=6)
    ip_timeout_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

    ttk.Label(schedule_frame, text="Ollama Zaman Aşımı (sn)").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
    analysis_timeout_entry = ttk.Entry(schedule_frame, textvariable=analysis_timeout_var, width=6)
    analysis_timeout_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

    schedule_frame.columnconfigure(1, weight=1)

    stop_event = threading.Event()
    auto_thread = {'thread': None}
    auto_running = tk.BooleanVar(value=False)

    def notify(message, level="info", popup=True):
        def _show():
            status_var.set(message)
            if popup and level == "warning":
                messagebox.showwarning("Sistem Raporu", message)
            elif popup and level == "error":
                messagebox.showerror("Sistem Raporu", message)

        if threading.current_thread() is threading.main_thread():
            _show()
        else:
            root.after(0, _show)

    def parse_int(var, default, label):
        try:
            value = int(var.get())
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            notify(f"{label} değeri geçersiz, {default} kullanılıyor.", level="warning", popup=False)
            return default

    def get_current_config():
        return {
            'include_network': include_network_var.get(),
            'include_disk': include_disk_var.get(),
            'include_temp': include_temp_var.get(),
            'include_ip': include_ip_var.get(),
            'interval': parse_int(interval_var, 3600, "Sıklık"),
            'ip_timeout': parse_int(ip_timeout_var, 3, "IP zaman aşımı"),
            'analysis_timeout': parse_int(analysis_timeout_var, 30, "Ollama zaman aşımı"),
        }

    def stop_auto_generation():
        stop_event.set()
        thread_obj = auto_thread['thread']
        if thread_obj and thread_obj.is_alive():
            thread_obj.join(timeout=1)
        auto_thread['thread'] = None
        auto_running.set(False)
        auto_button.config(text="Otomatik Raporu Başlat")
        notify("Otomatik rapor durduruldu.", popup=False)

    def start_auto_generation():
        if auto_running.get():
            return
        stop_event.clear()
        thread_obj = threading.Thread(
            target=auto_generate_report,
            args=(stop_event, get_current_config, lambda msg, level='info': notify(msg, level, popup=False)),
            daemon=True
        )
        auto_thread['thread'] = thread_obj
        thread_obj.start()
        auto_running.set(True)
        auto_button.config(text="Otomatik Raporu Durdur")
        notify("Otomatik rapor başlatıldı.", popup=False)

    def toggle_auto_generation():
        if auto_running.get():
            stop_auto_generation()
        else:
            start_auto_generation()

    def generate_report():
        config = get_current_config()
        report, warnings = compose_report(
            include_ip=config['include_ip'],
            include_network=config['include_network'],
            include_disk=config['include_disk'],
            include_temp=config['include_temp'],
            ip_timeout=config['ip_timeout']
        )

        report_text.delete(1.0, tk.END)
        report_text.insert(tk.END, report)

        if warnings:
            notify("\n".join(warnings), level="warning")

        analysis, error = analyze_with_deepscaler(report, timeout=config['analysis_timeout'])
        if analysis:
            report_text.insert(tk.END, "\n\nOllama Analizi:\n" + analysis)
        if error:
            notify(error, level="error")
        else:
            notify("Rapor oluşturuldu.", popup=False)

    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    generate_button = ttk.Button(buttons_frame, text="Raporu Oluştur", command=generate_report)
    generate_button.pack(side=tk.LEFT)

    auto_button = ttk.Button(buttons_frame, text="Otomatik Raporu Başlat", command=toggle_auto_generation)
    auto_button.pack(side=tk.LEFT, padx=5)

    status_label = ttk.Label(root, textvariable=status_var, anchor=tk.W)
    status_label.pack(fill=tk.X, padx=10, pady=(0, 10))

    def on_close():
        if auto_running.get():
            stop_auto_generation()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    print("Sistem Raporu Uygulaması")
    print("-------------------------")

    report, warnings = compose_report(
        include_ip=True,
        include_network=True,
        include_disk=True,
        include_temp=True
    )
    print("\nSistem Bilgileri:\n", report)
    if warnings:
        for warning in warnings:
            print(f"Uyarı: {warning}")

    analysis_result, analysis_error = analyze_with_deepscaler(report)
    if analysis_result:
        print("\nAnaliz Sonucu:\n", analysis_result)
    if analysis_error:
        print("\nOllama Hatası:\n", analysis_error)

    save_report_to_file(report)

    if analysis_result:
        show_notification(analysis_result[:256])

    create_gui()
