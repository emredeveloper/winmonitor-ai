# Windows System Monitor & Analytics Tool 🖥️

A Python-based system monitoring tool that provides real-time system information, analysis, and notifications for Windows machines.

## Features
- 🔍 Real-time system metrics monitoring (CPU, RAM, disk, network)
- 📊 Network and disk usage analytics
- 🌡️ CPU temperature tracking (when supported by the device)
- 💾 Automated and on-demand report generation
- 🔔 Windows toast notifications for critical insights
- 📝 Custom report composition via the CLI
- 🤖 AI-powered system analysis using Ollama's `deepscaler` model
- 🖼️ Simple Tkinter-based GUI interface

## Gereksinimler
- **İşletim Sistemi:** Windows 10 veya Windows 11 (64-bit önerilir)
- **Python:** 3.10 veya üzeri (64-bit sürüm)
- **Bağımlılıklar:**
  - `psutil`
  - `requests`
  - `win10toast`
  - `tkinter` (Python ile birlikte gelir)
  - Ollama (opsiyonel, yalnızca yapay zekâ analizi için)
- **Ek Araçlar:** Ollama kullanımı için WSL2 veya Docker üzerinden kurulu Ollama CLI (detaylar aşağıda)

> ⚠️ Uygulama yalnızca Windows üzerinde test edilmiştir. `win10toast` ve `.bat` başlatma betiği gibi bileşenler Windows dışı ortamlarda çalışmaz.

## Kurulum
1. Python 3.10+ kurulu olduğundan emin olun ve "Add Python to PATH" seçeneğini işaretleyin.
2. Depoyu indirin veya klonlayın:
   ```powershell
   git clone https://github.com/<kullanici>/winmonitor-ai.git
   cd winmonitor-ai
   ```
3. (Önerilen) Sanal ortam oluşturun:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
4. Gerekli paketleri yükleyin:
   ```powershell
   pip install psutil requests win10toast
   ```
5. Ollama entegrasyonu kullanacaksanız Ollama CLI'nin sisteminizde kurulu ve `PATH` içerisinde olduğundan emin olun.

## Çalıştırma
- **Grafik Arayüzü ile:**
  ```powershell
  pythonw startup_info.pyw
  ```
  veya sağlanan `run_agent.bat` dosyasını çift tıklayın.

- **Komut Satırından:**
  ```powershell
  python startup_info.pyw
  ```
  Bu modda terminalde ayrıntılı sistem bilgileri ve Ollama analiz çıktısı görürsünüz.

> ℹ️ Uygulama başlatıldığında otomatik rapor oluşturma iş parçacığı ve Tkinter tabanlı GUI aynı anda çalışır.

## Ollama entegrasyonu nasıl etkinleştirilir?
1. Ollama CLI'yı Windows üzerinde çalıştırmak için bir arka uç sağlayın:
   - **WSL2 Tavsiyesi:** Ubuntu tabanlı bir WSL dağıtımı kurarak `curl https://ollama.ai/install.sh | sh` komutunu çalıştırın ve Ollama servisini başlatın.
   - **Docker Alternatifi:** Resmî Ollama Docker imajını kullanarak `ollama` komutunu sağlayan bir konteyner çalıştırın.
2. Windows terminalinizden `ollama --version` komutunu çalıştırarak CLI'nin erişilebilir olduğunu doğrulayın.
3. Gerekirse Ollama'nın dinlediği servisi başlatın (`ollama serve`).
4. Uygulamayı çalıştırdığınızda `analyze_with_deepscaler` fonksiyonu sistem raporunu Ollama'ya iletip özet sonucunu GUI ve bildirimde gösterecektir.

> 💡 Ollama entegrasyonu isteğe bağlıdır. CLI bulunamazsa fonksiyon hata mesajı döndürür ve uygulama temel sistem raporlama özellikleriyle çalışmaya devam eder.

## Windows dışı ortamlarda desteklenmeyen özellikler
- **Bildirimler:** `win10toast` yalnızca Windows Bildirim Merkezi ile çalışır. Diğer platformlarda bildirim modülü import hatası verir. Çözüm olarak platforma özel bir bildirim kütüphanesi (`plyer`, `notify2` vb.) ile koşullu import ekleyebilirsiniz.
- **.bat Başlatma Betiği:** `run_agent.bat` yalnızca Windows komut işlemcisiyle uyumludur. Linux/macOS üzerinde `.sh` betiği oluşturarak eşdeğer başlatma adımlarını tanımlayabilirsiniz.
- **CPU Sıcaklığı:** `psutil.sensors_temperatures()` tüm cihazlarda veri döndürmeyebilir. Laptop veya bazı masaüstlerinde BIOS kısıtlamaları sebebiyle sıcaklık değeri alınamayabilir.

## Sık karşılaşılan hatalar
- **"ModuleNotFoundError: No module named 'win10toast'"**
  - Çözüm: `pip install win10toast` komutunu çalıştırın ve doğru Python ortamında olduğunuzu doğrulayın.
- **"Ollama işlemi sırasında bir hata oluştu" veya `Analiz Hatası` mesajları**
  - Çözüm: `ollama` komutunun terminalden çalıştığını, `ollama serve` servisinin aktif olduğunu ve `deepscaler` modelinin yüklü olduğunu (`ollama pull deepscaler`) kontrol edin.
- **GUI açılmıyor veya donuyor**
  - Çözüm: Uygulamayı `python startup_info.pyw` yerine `pythonw` ile çalıştırmayı deneyin. Ayrıca antivirüs veya güvenlik yazılımlarının Tkinter uygulamalarını engellemediğinden emin olun.
- **"İşlemci sıcaklığı hatası" mesajı**
  - Çözüm: CPU sıcaklığı verisi donanım/BIOS tarafından expose edilmemiş olabilir. Desteklenen bir sensör sürücüsü olmadıkça hata mesajı bilgi amaçlıdır ve uygulamanın çalışmasını etkilemez.

---

Geri bildirimlerinizi ve geliştirme önerilerinizi memnuniyetle karşılarız!
