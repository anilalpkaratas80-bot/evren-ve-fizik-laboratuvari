import ctypes
import math
import random
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser


GENISLIK = 900
YUKSEKLIK = 610
ARKA_PLAN = "#050816"
PANEL = "#101827"
BEYAZ = "#f8fafc"
SOLUK = "#c7d2e0"
MAVI = "#38bdf8"
TURUNCU = "#fbbf24"
YESIL = "#34d399"
MOR = "#a78bfa"
PEMBE = "#fb7185"
GPC_METRE = 1476.6250385
MPC_METRE = 3.085677581491367e22
RADYAN_TO_UAS = 206264806247.09636
APP_NAME = "Evren ve Fizik Laboratuvarı"
APP_VERSION = "1.0.0"


def dolasik_cift_olc(aci_a, aci_b):
    """Tekilci spin durumu için ideal kuantum ölçüm sonuçlarından bir çift üretir."""
    sonuc_a = random.choice((-1, 1))
    aci_farki = math.radians(aci_a - aci_b)
    zit_sonuc_olasiligi = (1 + math.cos(aci_farki)) / 2
    sonuc_b = -sonuc_a if random.random() < zit_sonuc_olasiligi else sonuc_a
    return sonuc_a, sonuc_b


def kara_delik_olculeri(kutle_gunes, spin, uzaklik_mpc):
    """Basit Kerr ufku ve Schwarzschild-benzeri gölge ölçeğini hesaplar."""
    if kutle_gunes <= 0 or uzaklik_mpc <= 0:
        raise ValueError("Kütle ve uzaklık sıfırdan büyük olmalıdır.")
    if not 0 <= spin < 1:
        raise ValueError("Spin parametresi 0 ile 1 arasında olmalıdır.")

    rg = GPC_METRE * kutle_gunes
    ufuk_yaricap = rg * (1 + math.sqrt(1 - spin ** 2))
    golge_cap = 10.4 * rg
    acisal_cap = golge_cap / (uzaklik_mpc * MPC_METRE) * RADYAN_TO_UAS
    return ufuk_yaricap, golge_cap, acisal_cap


def windows_dpi_ayarla():
    if sys.platform == "win32":
        basarili = ctypes.windll.user32.SetProcessDPIAware()
        if not basarili:
            raise ctypes.WinError()


class DolasiklikSunumu:
    def __init__(self, pencere):
        self.pencere = pencere
        self.uygulama_adi = APP_NAME
        self.pencere.title(f"{self.uygulama_adi} v{APP_VERSION}")
        self.pencere.configure(bg=ARKA_PLAN)
        self.pencere.geometry("1080x900")
        self.pencere.minsize(980, 820)

        stil = ttk.Style(self.pencere)
        stil.theme_use("clam")
        stil.configure("TFrame", background=ARKA_PLAN)
        stil.configure("Card.TFrame", background=PANEL)
        stil.configure(
            "TLabel",
            background=ARKA_PLAN,
            foreground=BEYAZ,
            font=("Segoe UI", 11),
        )
        stil.configure("Card.TLabel", background=PANEL, foreground=BEYAZ)
        stil.configure(
            "Muted.TLabel", background=ARKA_PLAN, foreground=SOLUK
        )
        stil.configure(
            "Accent.TButton",
            background="#075985",
            foreground=BEYAZ,
            padding=(12, 7),
            borderwidth=0,
        )
        stil.map(
            "Accent.TButton",
            background=[("active", "#0e7490"), ("pressed", "#155e75")],
            foreground=[("active", BEYAZ)],
        )
        stil.configure(
            "TButton",
            background=PANEL,
            foreground=BEYAZ,
            padding=(10, 6),
            borderwidth=1,
        )
        stil.map(
            "TButton",
            background=[("active", "#1a2d45"), ("pressed", "#27425f")],
            foreground=[("active", MAVI), ("disabled", SOLUK)],
        )
        stil.configure(
            "TNotebook",
            background=ARKA_PLAN,
            borderwidth=0,
            tabmargins=(6, 8, 6, 0),
        )
        stil.configure(
            "TNotebook.Tab",
            background="#111827",
            foreground=SOLUK,
            padding=(18, 11),
            font=("Segoe UI", 10, "bold"),
        )
        stil.map(
            "TNotebook.Tab",
            background=[("selected", "#12334a"), ("active", "#17263b")],
            foreground=[("selected", MAVI), ("active", BEYAZ)],
        )
        stil.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=BEYAZ,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        stil.configure(
            "Treeview.Heading",
            background="#1a2d45",
            foreground=MAVI,
            font=("Segoe UI", 10, "bold"),
        )
        stil.map(
            "Treeview",
            background=[("selected", "#164e63")],
            foreground=[("selected", BEYAZ)],
        )

        self.aci_a = 0
        self.aci_b = 0
        self.toplam = 0
        self.toplam_carpim = 0
        self.sayilar_a = {-1: 0, 1: 0}
        self.sayilar_b = {-1: 0, 1: 0}
        self.son_cift = None

        self.ust_bant = tk.Canvas(
            pencere,
            height=130,
            bg=ARKA_PLAN,
            highlightthickness=0,
        )
        self.ust_bant.pack(fill=tk.X, padx=18, pady=(14, 8))
        self.ust_bant.bind("<Configure>", self.ust_bant_ciz)

        self.sekmeler = ttk.Notebook(pencere)
        self.sekmeler.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 16))
        self.simulasyon_sekmesi = ttk.Frame(self.sekmeler)
        self.kvantum_sekmesi = ttk.Frame(self.sekmeler)
        self.konular_sekmesi = ttk.Frame(self.sekmeler)
        self.terimler_sekmesi = ttk.Frame(self.sekmeler)
        self.deneyler_sekmesi = ttk.Frame(self.sekmeler)
        self.oduller_sekmesi = ttk.Frame(self.sekmeler)
        self.kaynaklar_sekmesi = ttk.Frame(self.sekmeler)
        self.sekmeler.add(self.simulasyon_sekmesi, text="Kara Delik Laboratuvarı")
        self.sekmeler.add(
            self.kvantum_sekmesi, text="Kuantum Araştırma Laboratuvarı"
        )
        self.sekmeler.add(self.konular_sekmesi, text="Konular")
        self.sekmeler.add(self.terimler_sekmesi, text="Terimler + Anlatım")
        self.sekmeler.add(self.deneyler_sekmesi, text="Deneyler")
        self.sekmeler.add(self.oduller_sekmesi, text="Nobel ve Ödüller")
        self.sekmeler.add(self.kaynaklar_sekmesi, text="Kaynaklar")

        self.kvantum_ic_sekmeler = ttk.Notebook(self.kvantum_sekmesi)
        self.kvantum_ic_sekmeler.pack(
            fill=tk.BOTH, expand=True, padx=8, pady=8
        )
        self.dolasiklik_sekmesi = ttk.Frame(self.kvantum_ic_sekmeler)
        self.cift_yarik_sekmesi = ttk.Frame(self.kvantum_ic_sekmeler)
        self.spin_lab_sekmesi = ttk.Frame(self.kvantum_ic_sekmeler)
        self.kvantum_ic_sekmeler.add(
            self.dolasiklik_sekmesi, text="Dolaşıklık / Bell"
        )
        self.kvantum_ic_sekmeler.add(
            self.cift_yarik_sekmesi, text="Çift yarık"
        )
        self.kvantum_ic_sekmeler.add(
            self.spin_lab_sekmesi, text="Spin ölçümü"
        )

        self.kanvas = tk.Canvas(
            self.dolasiklik_sekmesi,
            width=GENISLIK,
            height=YUKSEKLIK,
            bg=ARKA_PLAN,
            highlightthickness=0,
        )
        self.kanvas.pack()

        kontroller = ttk.Frame(self.dolasiklik_sekmesi, padding=8)
        kontroller.pack()
        tuslar = [
            ("A acisi -10", lambda: self.aci_degistir("a", -10)),
            ("A acisi +10", lambda: self.aci_degistir("a", 10)),
            ("B acisi -10", lambda: self.aci_degistir("b", -10)),
            ("B acisi +10", lambda: self.aci_degistir("b", 10)),
            ("1 cift olc", self.bir_cift_olc),
            ("1000 cift olc", self.bin_cift_olc),
            ("Sifirla", self.sifirla),
        ]
        for yazi, komut in tuslar:
            dugme_stili = (
                "Accent.TButton" if yazi in ("1 cift olc", "1000 cift olc")
                else "TButton"
            )
            ttk.Button(
                kontroller, text=yazi, command=komut, style=dugme_stili
            ).pack(side=tk.LEFT, padx=4)

        tk.Label(
            self.dolasiklik_sekmesi,
            text=(
                "Tek taraftaki sonuc rastgeledir. Korelasyonu anlamak icin iki tarafin "
                "kayitlari sonradan karsilastirilir; bu karsilastirma normal iletisim gerektirir."
            ),
            font=("Segoe UI", 9),
            fg=BEYAZ,
            bg=ARKA_PLAN,
            wraplength=850,
            justify=tk.CENTER,
        ).pack(pady=(2, 8))

        self.kara_delik_lab_hazirla()
        self.kara_delik_test_asamalari_hazirla()
        self.konulari_hazirla()
        self.terimleri_hazirla()
        self.anlatimi_hazirla()
        self.deneyleri_hazirla()
        self.odulleri_hazirla()
        self.kaynaklari_hazirla()
        self.cift_yarik_lab_hazirla()
        self.spin_lab_hazirla()
        self.ciz()

    def kara_delik_lab_hazirla(self):
        self.kara_delik_lab_ic_sekmeler = ttk.Notebook(self.simulasyon_sekmesi)
        self.kara_delik_lab_ic_sekmeler.pack(
            fill=tk.BOTH, expand=True, padx=8, pady=8
        )
        self.kara_delik_gorsel_sekmesi = ttk.Frame(
            self.kara_delik_lab_ic_sekmeler
        )
        self.kara_delik_test_sekmesi = ttk.Frame(
            self.kara_delik_lab_ic_sekmeler
        )
        self.kara_delik_lab_ic_sekmeler.add(
            self.kara_delik_gorsel_sekmesi, text="3B Laboratuvar"
        )
        self.kara_delik_lab_ic_sekmeler.add(
            self.kara_delik_test_sekmesi, text="Aşamalı gözlem testi"
        )
        govde = ttk.Frame(self.kara_delik_gorsel_sekmesi, padding=12)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)

        ttk.Label(
            govde,
            text="Kara Delik Laboratuvarı",
            font=("Segoe UI", 19, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            govde,
            text=(
                "Parametreleri değiştir, kuramsal ölçekleri izle ve hangi gözlemlerin "
                "ne söyleyebileceğini karşılaştır."
            ),
            style="Muted.TLabel",
            wraplength=900,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(31, 12))

        ayarlar = ttk.Frame(govde, style="Card.TFrame", padding=14)
        ayarlar.grid(row=1, column=0, sticky="nsw", padx=(0, 12))
        ttk.Label(
            ayarlar, text="Kara deliği ayarla", style="Card.TLabel",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.kutle_log = tk.DoubleVar(value=9.8)
        self.spin = tk.DoubleVar(value=0.7)
        self.egim = tk.DoubleVar(value=60)
        self.uzaklik_log = tk.DoubleVar(value=math.log10(16.8))
        self.kara_delik_gozlem_verileri = {
            "Sagittarius A* — Samanyolu": (
                51.8,
                2.3,
                "EHT 2022, ApJL 930 L12",
                "https://iopscience.iop.org/article/10.3847/2041-8213/ac6674",
            ),
            "M87* — Messier 87": (
                42.0,
                3.0,
                "EHT 2019, ApJL 875 L1",
                "https://iopscience.iop.org/article/10.3847/2041-8213/ab0ec7",
            ),
        }
        self.kara_delik_profilleri = {
            "Özel senaryo": None,
            "Sagittarius A* — Samanyolu": (
                4.0e6,
                0.0082,
                "Kütle ≈4,0 milyon M☉, uzaklık ≈8,2 kpc. EHT halka çapı "
                "51,8 ± 2,3 μas. Spin ayarı ölçülmüş profil değeri değildir.",
                "https://iopscience.iop.org/article/10.3847/2041-8213/ac6674",
            ),
            "M87* — Messier 87": (
                6.5e9,
                16.8,
                "Kütle ≈(6,5 ± 0,7) milyar M☉, uzaklık ≈16,8 Mpc. EHT halka "
                "çapı 42 ± 3 μas. Spin ayarı kullanıcı varsayımıdır.",
                "https://iopscience.iop.org/article/10.3847/2041-8213/ab0ec7",
            ),
            "TON 618 — kuasar": (
                66.0e9,
                1702.7,
                "NASA yaklaşık 66 milyar M☉ kütle bildiriyor. D_A≈1,70 Gpc, "
                "z≈2,219 ve H0=70/Ωm=0,3 varsayımlarıyla hesaplanmış "
                "modeldir; TON 618 için EHT halka ölçümü yok. Spin varsayımdır.",
                "https://science.nasa.gov/universe/black-holes/",
            ),
        }
        self.profil_yukleniyor = False
        self.kara_delik_profili = tk.StringVar(value="Özel senaryo")
        ttk.Label(
            ayarlar, text="Keşfedilmiş kara delik profili",
            style="Card.TLabel", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        self.profil_secici = ttk.Combobox(
            ayarlar,
            textvariable=self.kara_delik_profili,
            values=tuple(self.kara_delik_profilleri),
            state="readonly",
            width=28,
        )
        self.profil_secici.pack(fill=tk.X)
        self.profil_secici.bind(
            "<<ComboboxSelected>>", self.kara_delik_profil_secildi
        )
        self.profil_bilgi = ttk.Label(
            ayarlar, style="Card.TLabel", foreground="#a5f3fc",
            wraplength=265, justify=tk.LEFT,
        )
        self.profil_bilgi.pack(anchor="w", pady=(4, 8))

        def kaydirici(etiket, degisken, alt, ust, bicim):
            satir = ttk.Frame(ayarlar, style="Card.TFrame")
            satir.pack(fill=tk.X, pady=5)
            deger = tk.StringVar()
            ttk.Label(
                satir, text=etiket, style="Card.TLabel",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            ttk.Label(
                satir, textvariable=deger, style="Card.TLabel",
                foreground=MAVI,
            ).pack(anchor="e")
            ttk.Scale(
                satir,
                variable=degisken,
                from_=alt,
                to=ust,
                command=self.kara_delik_parametre_degisti,
            ).pack(fill=tk.X, pady=(2, 0))
            self.kara_delik_deger_etiketleri.append((deger, degisken, bicim))

        self.kara_delik_deger_etiketleri = []
        kaydirici("Kütle (Güneş kütlesi, log ölçek)", self.kutle_log, 1, 12,
                  lambda deger: f"{10 ** deger:,.2g} M☉")
        kaydirici("Spin (boyutsuz, 0–0,998)", self.spin, 0, 0.998,
                  lambda deger: f"a* = {deger:.3f}")
        kaydirici("Görüş eğimi (derece)", self.egim, 0, 90,
                  lambda deger: f"{deger:.0f}°")
        kaydirici("Uzaklık (Mpc, log ölçek)", self.uzaklik_log, -3, 4,
                  lambda deger: f"{10 ** deger:,.3g} Mpc")

        ttk.Label(
            ayarlar, text="Gözlem yöntemi", style="Card.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(12, 4))
        self.gozlem_yontemi = tk.StringVar(value="EHT / radyo görüntüleme")
        yontemler = ttk.Combobox(
            ayarlar,
            textvariable=self.gozlem_yontemi,
            values=(
                "EHT / radyo görüntüleme",
                "Yıldız yörüngeleri",
                "Disk tayfı",
                "Kütleçekim dalgaları",
            ),
            state="readonly",
            width=27,
        )
        yontemler.pack(fill=tk.X)
        yontemler.bind(
            "<<ComboboxSelected>>", self.kara_delik_lab_guncelle
        )
        ttk.Button(
            ayarlar,
            text="Ayarları başlangıca döndür",
            command=self.kara_delik_ayarlari_sifirla,
        ).pack(fill=tk.X, pady=(12, 0))
        self.profil_kaynak = ttk.Button(
            ayarlar, text="Seçili profilin kaynağı"
        )
        self.profil_kaynak.pack(fill=tk.X, pady=(6, 0))

        sag = ttk.Frame(govde)
        sag.grid(row=1, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(1, weight=1)
        araclar = ttk.Frame(sag, style="Card.TFrame", padding=(8, 5))
        araclar.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        self.disk_goster = tk.BooleanVar(value=True)
        self.jet_goster = tk.BooleanVar(value=True)
        self.halka_goster = tk.BooleanVar(value=True)
        for etiket, degisken in (
            ("Disk", self.disk_goster),
            ("Jet", self.jet_goster),
            ("Işık halkası", self.halka_goster),
        ):
            ttk.Checkbutton(
                araclar,
                text=etiket,
                variable=degisken,
                command=self.kara_delik_ciz,
            ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            araclar,
            text="Görünümü sıfırla",
            command=self.kara_delik_gorunum_sifirla,
        ).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(
            araclar,
            text="Raporu kaydet",
            command=self.kara_delik_raporu_kaydet,
        ).pack(side=tk.RIGHT)
        self.kara_delik_kanvasi = tk.Canvas(
            sag,
            height=365,
            bg="#030712",
            highlightthickness=1,
            highlightbackground="#243449",
        )
        self.kara_delik_kanvasi.grid(row=1, column=0, sticky="nsew")
        self.kara_delik_kanvasi.bind(
            "<Configure>", self.kara_delik_ciz
        )
        self.kara_delik_kanvasi.bind(
            "<ButtonPress-1>", self.kara_delik_surukleme_baslat
        )
        self.kara_delik_kanvasi.bind(
            "<ButtonRelease-1>", self.kara_delik_surukleme_bitir
        )
        self.kara_delik_kanvasi.bind(
            "<B1-Motion>", self.kara_delik_surukle
        )
        self.kara_delik_kanvasi.bind(
            "<MouseWheel>", self.kara_delik_yakinlastir
        )
        self.kara_delik_yaw = -0.25
        self.kara_delik_pitch = -0.35
        self.kara_delik_zoom = 1.0

        olcumler = ttk.Frame(sag, style="Card.TFrame", padding=12)
        olcumler.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        olcumler.columnconfigure(0, weight=1)
        ttk.Label(
            olcumler, text="Hesaplanan ölçekler", style="Card.TLabel",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self.kara_delik_sonuc = ttk.Label(
            olcumler, style="Card.TLabel", justify=tk.LEFT,
            font=("Segoe UI", 10), wraplength=680,
        )
        self.kara_delik_sonuc.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.kara_delik_gercek_olcum = ttk.Label(
            olcumler,
            style="Card.TLabel",
            foreground="#fde68a",
            font=("Segoe UI", 10, "bold"),
            justify=tk.LEFT,
            wraplength=680,
        )
        self.kara_delik_gercek_olcum.grid(
            row=2, column=0, sticky="ew", pady=(5, 0)
        )
        self.kara_delik_yontem_aciklama = ttk.Label(
            olcumler, style="Card.TLabel", foreground="#a5f3fc",
            font=("Segoe UI", 10), justify=tk.LEFT, wraplength=680,
        )
        self.kara_delik_yontem_aciklama.grid(
            row=3, column=0, sticky="ew", pady=(4, 0)
        )
        ttk.Label(
            olcumler,
            text=(
                "Modeldeki ~10,4 GM/c² gölge ölçeği ile EHT'nin parlak halka "
                "çapı aynı ölçüm değildir; fark resmî uyum testi sayılmaz. "
                "±, EHT makalesindeki halka çapı belirsizliğidir."
            ),
            style="Muted.TLabel",
            font=("Segoe UI", 9),
            wraplength=680,
            justify=tk.LEFT,
        ).grid(row=4, column=0, sticky="ew", pady=(5, 0))
        kaynaklar = ttk.Frame(olcumler, style="Card.TFrame")
        kaynaklar.grid(row=5, column=0, sticky="w", pady=(6, 0))
        self.eht_gozlem_kaynagi = ttk.Button(
            kaynaklar,
            text="Seçili EHT ölçüm makalesi",
            command=self.eht_makalesini_ac,
        )
        self.eht_gozlem_kaynagi.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            kaynaklar,
            text="NASA: kara delik gözlemleri",
            command=lambda: webbrowser.open(
                "https://science.nasa.gov/universe/black-holes/"
            ),
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            kaynaklar,
            text="Nobel 2020 gerekçesi",
            command=lambda: webbrowser.open(
                "https://www.nobelprize.org/prizes/physics/2020/summary/"
            ),
        ).pack(side=tk.LEFT)
        self.kara_delik_nobel_notu = ttk.Label(
            olcumler,
            style="Muted.TLabel",
            font=("Segoe UI", 9),
            wraplength=680,
            justify=tk.LEFT,
        )
        self.kara_delik_nobel_notu.grid(
            row=6, column=0, sticky="ew", pady=(5, 0)
        )

        self.kara_delik_profili_goster()
        self.kara_delik_lab_guncelle()

    def kara_delik_test_asamalari_hazirla(self):
        govde = ttk.Frame(self.kara_delik_test_sekmesi, padding=22)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Aşamalı kara delik gözlem testi",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            govde,
            text=(
                "Bir hedef seç, ölçüm türünü belirle, varsayımlarını kaydet ve "
                "gözlemle modelin aynı niceliği ölçüp ölçmediğini kontrol et."
            ),
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(34, 14))

        self.kara_delik_test_adimlari = (
            (
                "Hedefi seç",
                "Bir profil seç ve hangi değerlerin gerçekten ölçüldüğünü "
                "kaynağından ayır.\n\n"
                "Sgr A* ve M87* için EHT halka çapı verisi bu uygulamada "
                "bulunur. TON 618 profili NASA'nın yaklaşık kütle değerini "
                "kullanır; uzaklık kozmoloji varsayımına bağlı tahmindir ve "
                "bu hedef için EHT halka çapı verisi yoktur.",
            ),
            (
                "Ölçüm yöntemini belirle",
                "EHT radyo görüntüleme, yıldız yörüngeleri, disk tayfı ve "
                "kütleçekim dalgaları farklı gözlenebilirleri sınırlar.\n\n"
                "Bu laboratuvar EHT halka çapını Sgr A* / M87* profillerinde "
                "gösterir. Diğer yöntemler için açıklama eğitim amaçlıdır; "
                "uygulama gerçek teleskop verisi analiz etmez.",
            ),
            (
                "Model varsayımlarını kaydet",
                "Kütle, uzaklık, spin ve görüş eğimini kontrol et. Profil "
                "değerleri yüklenince kütle/uzaklık profilden gelir; spin ve "
                "eğim kullanıcı varsayımı olarak kalır.\n\n"
                "Özel senaryoda seçtiğin sayıları gerçek ölçüm gibi "
                "yorumlama. Yaklaşık gölge hesabı, tam relativistik ışın "
                "izleme değildir.",
            ),
            (
                "Aynı nicelikleri karşılaştır",
                "Gözlenen EHT parlak halka çapını modelin yaklaşık gölge "
                "ölçeğiyle yan yana incele. EHT'deki ± değer, makaledeki "
                "halka çapı belirsizliğidir.\n\n"
                "Parlak halka çapı ve model gölge çapı aynı nicelik değildir; "
                "ekranda gösterilen fark resmî uyum testi veya istatistiksel "
                "anlamlılık ölçüsü değildir.",
            ),
            (
                "Raporla ve sınırlılıkları yaz",
                "Raporu kaydet ve hangi verinin gözlemsel, hangisinin model "
                "çıktısı ya da varsayım olduğunu belirt.\n\n"
                "Disk, jet ve 3B görünüm şematiktir. TON 618'in bu "
                "laboratuvardaki açısal ölçeği varsayılan kozmolojiye bağlıdır; "
                "profil kaynağı NASA sayfasında kütle bilgisi içindir.",
            ),
        )
        self.kara_delik_test_tamamlanan = set()
        self.kara_delik_test_secili_adim = 0
        self.kara_delik_test_listesi = ttk.Treeview(
            govde, show="tree", height=12, selectmode="browse"
        )
        self.kara_delik_test_listesi.column("#0", width=265, stretch=False)
        self.kara_delik_test_listesi.grid(
            row=1, column=0, sticky="nsw", padx=(0, 18)
        )
        for sira, (baslik, _aciklama) in enumerate(
            self.kara_delik_test_adimlari
        ):
            self.kara_delik_test_listesi.insert(
                "", tk.END, iid=str(sira), text=f"{sira + 1}. {baslik}"
            )
        self.kara_delik_test_listesi.bind(
            "<<TreeviewSelect>>", self.kara_delik_test_secildi
        )

        panel = ttk.Frame(govde, style="Card.TFrame", padding=20)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.kara_delik_test_baslik = ttk.Label(
            panel, style="Card.TLabel", font=("Segoe UI", 16, "bold")
        )
        self.kara_delik_test_baslik.grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        self.kara_delik_test_metni = tk.Text(
            panel, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=PANEL, fg=BEYAZ, padx=20, pady=18, relief=tk.FLAT,
        )
        self.kara_delik_test_metni.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=10,
            lmargin1=5, rmargin=5,
        )
        self.kara_delik_test_metni.grid(
            row=1, column=0, sticky="nsew"
        )
        controls = ttk.Frame(panel, style="Card.TFrame")
        controls.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        controls.columnconfigure(1, weight=1)
        ttk.Button(
            controls, text="← Önceki",
            command=lambda: self.kara_delik_test_adimi_goster(
                self.kara_delik_test_secili_adim - 1
            ),
        ).grid(row=0, column=0, sticky="w")
        self.kara_delik_test_ilerleme = ttk.Label(
            controls, style="Card.TLabel", foreground="#a5f3fc"
        )
        self.kara_delik_test_ilerleme.grid(row=0, column=1, sticky="e", padx=12)
        ttk.Button(
            controls, text="Bu aşamayı tamamla ✓",
            style="Accent.TButton",
            command=self.kara_delik_test_adimini_tamamla,
        ).grid(row=0, column=2, sticky="e")
        ttk.Button(
            controls, text="Sonraki →",
            command=lambda: self.kara_delik_test_adimi_goster(
                self.kara_delik_test_secili_adim + 1
            ),
        ).grid(row=0, column=3, sticky="e", padx=(8, 0))
        self.kara_delik_test_listesi.selection_set("0")
        self.kara_delik_test_adimi_goster(0)

    def kara_delik_test_secildi(self, _olay=None):
        secim = self.kara_delik_test_listesi.selection()
        if secim:
            self.kara_delik_test_adimi_goster(int(secim[0]))

    def kara_delik_test_adimi_goster(self, sira):
        sira = max(0, min(len(self.kara_delik_test_adimlari) - 1, sira))
        self.kara_delik_test_secili_adim = sira
        baslik, aciklama = self.kara_delik_test_adimlari[sira]
        self.kara_delik_test_baslik.config(
            text=f"{sira + 1}. Aşama — {baslik}"
        )
        self.kara_delik_test_metni.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.kara_delik_test_metni, aciklama, tek_bolum="TEST NOTLARI"
        )
        self.kara_delik_test_metni.config(state=tk.DISABLED)
        self.kara_delik_test_listesi.selection_set(str(sira))
        self.kara_delik_test_listesi.see(str(sira))
        self.kara_delik_test_ilerleme.config(
            text=(
                f"{len(self.kara_delik_test_tamamlanan)}/"
                f"{len(self.kara_delik_test_adimlari)} aşama tamamlandı"
            )
        )

    def kara_delik_test_adimini_tamamla(self):
        sira = self.kara_delik_test_secili_adim
        self.kara_delik_test_tamamlanan.add(sira)
        baslik = self.kara_delik_test_adimlari[sira][0]
        self.kara_delik_test_listesi.item(
            str(sira), text=f"✓ {sira + 1}. {baslik}"
        )
        self.kara_delik_test_adimi_goster(
            min(sira + 1, len(self.kara_delik_test_adimlari) - 1)
        )

    def kara_delik_ayarlari_sifirla(self):
        self.kutle_log.set(9.8)
        self.spin.set(0.7)
        self.egim.set(60)
        self.uzaklik_log.set(math.log10(16.8))
        self.gozlem_yontemi.set("EHT / radyo görüntüleme")
        self.kara_delik_profili.set("Özel senaryo")
        self.kara_delik_profili_goster()
        self.kara_delik_gorunum_sifirla()
        self.kara_delik_lab_guncelle()

    def kara_delik_profil_secildi(self, _olay=None):
        profil = self.kara_delik_profilleri[self.kara_delik_profili.get()]
        if profil is None:
            self.kara_delik_profili_goster()
            return
        kutle, uzaklik, _aciklama, _kaynak = profil
        self.profil_yukleniyor = True
        self.kutle_log.set(math.log10(kutle))
        self.uzaklik_log.set(math.log10(uzaklik))
        self.profil_yukleniyor = False
        self.kara_delik_profili_goster()
        self.kara_delik_lab_guncelle()

    def kara_delik_profili_goster(self):
        profil = self.kara_delik_profilleri[self.kara_delik_profili.get()]
        if profil is None:
            self.profil_bilgi.config(
                text=(
                    "Kütle ve uzaklığı kendin belirle. Spin değeri her zaman "
                    "görselleştirme varsayımıdır; profillerde ölçülmüş spin "
                    "değeri atanmaz."
                )
            )
            kaynak = "https://science.nasa.gov/universe/black-holes/"
        else:
            _kutle, _uzaklik, aciklama, kaynak = profil
            self.profil_bilgi.config(text=aciklama)
        if hasattr(self, "profil_kaynak"):
            self.profil_kaynak.config(
                command=lambda adres=kaynak: webbrowser.open(adres)
            )

    def kara_delik_parametre_degisti(self, _deger=None):
        if (
            not self.profil_yukleniyor
            and self.kara_delik_profili.get() != "Özel senaryo"
        ):
            self.kara_delik_profili.set("Özel senaryo")
            self.kara_delik_profili_goster()
        self.kara_delik_lab_guncelle()

    def kara_delik_lab_guncelle(self, _olay=None):
        if not hasattr(self, "kara_delik_kanvasi"):
            return
        kutle = 10 ** self.kutle_log.get()
        uzaklik = 10 ** self.uzaklik_log.get()
        ufuk, golge_cap, acisal_cap = kara_delik_olculeri(
            kutle, self.spin.get(), uzaklik
        )
        for etiket, degisken, bicim in self.kara_delik_deger_etiketleri:
            etiket.set(bicim(degisken.get()))
        rg = GPC_METRE * kutle
        sch_radius = 2 * rg
        isik_zamani = rg / 299792458
        self.kara_delik_sonuc.config(
            text=(
                f"Kerr r+: {ufuk / 1000:,.3g} km   |   "
                f"Schwarzschild r_s: {sch_radius / 1000:,.3g} km\n"
                f"Gölge çapı ~{golge_cap / 1000:,.3g} km "
                f"({acisal_cap:,.3g} μas)   |   r_g/c: {isik_zamani:.3g} s"
            )
        )
        gozlem = self.kara_delik_gozlem_verileri.get(
            self.kara_delik_profili.get()
        )
        if gozlem is None:
            if self.kara_delik_profili.get() == "Özel senaryo":
                gozlem_notu = (
                    "GERÇEK GÖZLEM: Özel senaryonun eşleşen ölçüm verisi yok. "
                    "Sgr A* veya M87* profilini seçerek EHT sonuçlarıyla "
                    "ölçek karşılaştırmasını aç."
                )
            else:
                gozlem_notu = (
                    "GERÇEK GÖZLEM: Bu profil için EHT halka çapı verisi "
                    "tanımlı değil. TON 618 kütlesi NASA kaynağına dayanır; "
                    "açısal ölçek kozmoloji varsayımına bağlı model tahminidir."
                )
            self.kara_delik_gercek_olcum.config(
                text=gozlem_notu
            )
            self.eht_gozlem_kaynagi.config(state=tk.DISABLED)
        else:
            olculen_halka, belirsizlik, _kaynak_adi, url = gozlem
            fark = acisal_cap - olculen_halka
            self.kara_delik_gercek_olcum.config(
                text=(
                    f"EHT ölçümü — parlak halka çapı: "
                    f"{olculen_halka:.1f} ± {belirsizlik:.1f} μas\n"
                    f"Model gölge ölçeği: {acisal_cap:.1f} μas   |   "
                    f"basit sayısal fark: {fark:+.1f} μas"
                )
            )
            self.eht_gozlem_kaynagi.config(
                state=tk.NORMAL,
                command=lambda adres=url: webbrowser.open(adres),
            )
        self.kara_delik_nobel_notu.config(
            text=(
                "Nobel Fizik 2020: Penrose'un kara delik oluşumuna ilişkin "
                "kuramsal çalışması ile Genzel ve Ghez'in Samanyolu "
                "merkezindeki kompakt cisim keşfi ödüllendirildi; EHT halka "
                "çapı ölçümü ayrı bir gözlem sonucudur."
            )
        )
        yontem_aciklamalari = {
            "EHT / radyo görüntüleme": (
                "EHT radyo görüntülemesi halka/gölge ölçeğini inceler; "
                "ufkun fotoğrafını çekmez."
            ),
            "Yıldız yörüngeleri": (
                "Yıldız yörüngeleri merkezî kütleyi sınırlar; spin için "
                "genellikle ek veriler gerekir."
            ),
            "Disk tayfı": (
                "Disk tayfı sıcaklık ve hareket hakkında ipucu verir; "
                "spin çıkarımı modele bağlıdır."
            ),
            "Kütleçekim dalgaları": (
                "Birleşme dalga biçimi kütle/spin bilgisi taşır; bu araç "
                "gerçek dalga verisi çözümlemez."
            ),
        }
        self.kara_delik_yontem_aciklama.config(
            text=yontem_aciklamalari[self.gozlem_yontemi.get()]
        )
        self.kara_delik_ciz()

    def eht_makalesini_ac(self):
        gozlem = self.kara_delik_gozlem_verileri.get(
            self.kara_delik_profili.get()
        )
        if gozlem is not None:
            webbrowser.open(gozlem[3])

    def kara_delik_noktasi_3d(self, x, y, z, merkez_x, merkez_y, olcek):
        egim = math.radians(self.egim.get())
        y, z = (
            y * math.cos(egim) - z * math.sin(egim),
            y * math.sin(egim) + z * math.cos(egim),
        )
        x, y = (
            x * math.cos(self.kara_delik_yaw) - y * math.sin(self.kara_delik_yaw),
            x * math.sin(self.kara_delik_yaw) + y * math.cos(self.kara_delik_yaw),
        )
        y, derinlik = (
            y * math.cos(self.kara_delik_pitch) - z * math.sin(self.kara_delik_pitch),
            y * math.sin(self.kara_delik_pitch) + z * math.cos(self.kara_delik_pitch),
        )
        perspektif = 8.5 / (8.5 - derinlik)
        return (
            merkez_x + x * olcek * self.kara_delik_zoom * perspektif,
            merkez_y - y * olcek * self.kara_delik_zoom * perspektif,
            derinlik,
        )

    @staticmethod
    def kara_delik_renk_ac(renk, parlaklik):
        kanallar = tuple(
            int(renk[sira:sira + 2], 16) for sira in (1, 3, 5)
        )
        kanallar = tuple(
            max(0, min(255, round(kanal * parlaklik)))
            for kanal in kanallar
        )
        return "#{:02x}{:02x}{:02x}".format(*kanallar)

    def kara_delik_surukleme_baslat(self, olay):
        self.kara_delik_surukleme_noktasi = (olay.x, olay.y)
        self.kara_delik_kanvasi.configure(cursor="fleur")

    def kara_delik_surukleme_bitir(self, _olay=None):
        self.kara_delik_surukleme_noktasi = None
        self.kara_delik_kanvasi.configure(cursor="")

    def kara_delik_surukle(self, olay):
        onceki = getattr(self, "kara_delik_surukleme_noktasi", None)
        if onceki is None:
            return
        dx = olay.x - onceki[0]
        dy = olay.y - onceki[1]
        self.kara_delik_yaw += dx * 0.009
        self.kara_delik_pitch = max(
            -1.35, min(1.35, self.kara_delik_pitch + dy * 0.009)
        )
        self.kara_delik_surukleme_noktasi = (olay.x, olay.y)
        self.kara_delik_ciz()

    def kara_delik_yakinlastir(self, olay):
        carpan = 1.1 if olay.delta > 0 else 0.9
        self.kara_delik_zoom = max(
            0.55, min(1.8, self.kara_delik_zoom * carpan)
        )
        self.kara_delik_ciz()

    def kara_delik_gorunum_sifirla(self):
        self.kara_delik_yaw = -0.25
        self.kara_delik_pitch = -0.35
        self.kara_delik_zoom = 1.0
        self.kara_delik_surukleme_noktasi = None
        if hasattr(self, "kara_delik_kanvasi"):
            self.kara_delik_kanvasi.configure(cursor="")
            self.kara_delik_ciz()

    def kara_delik_raporu_kaydet(self):
        hedef = filedialog.asksaveasfilename(
            title="Laboratuvar raporunu kaydet",
            defaultextension=".txt",
            filetypes=(("Metin dosyası", "*.txt"),),
        )
        if not hedef:
            return
        kutle = 10 ** self.kutle_log.get()
        uzaklik = 10 ** self.uzaklik_log.get()
        profil = self.kara_delik_profilleri[self.kara_delik_profili.get()]
        gozlem = self.kara_delik_gozlem_verileri.get(
            self.kara_delik_profili.get()
        )
        ufuk, golge, acisal = kara_delik_olculeri(
            kutle, self.spin.get(), uzaklik
        )
        rapor = (
            f"{self.uygulama_adi} — KARA DELİK LABORATUVARI\n"
            "Eğitim amaçlı kuramsal model; gerçek gözlem verisi değildir.\n\n"
            f"Profil: {self.kara_delik_profili.get()}\n"
            f"Kütle: {kutle:.6g} Güneş kütlesi\n"
            f"Uzaklık: {uzaklik:.6g} Mpc\n"
            f"Profil notu: {profil[2] if profil else 'Kullanıcı tanımlı senaryo.'}\n"
            f"Spin varsayımı: a*={self.spin.get():.4f}\n"
            f"Görüş eğimi: {self.egim.get():.2f} derece\n"
            f"Gözlem türü: {self.gozlem_yontemi.get()}\n"
            f"Kerr ufuk yarıçapı: {ufuk / 1000:.8g} km\n"
            f"Yaklaşık gölge çapı: {golge / 1000:.8g} km\n"
            f"Yaklaşık açısal gölge çapı: {acisal:.8g} mikroark saniye\n\n"
            + (
                f"EHT parlak halka çapı: {gozlem[0]:.4g} ± "
                f"{gozlem[1]:.4g} mikroark saniye ({gozlem[2]})\n"
                f"EHT makalesi: {gozlem[3]}\n\n"
                if gozlem is not None
                else "Bu profil için EHT halka çapı ölçümü raporlanmamıştır.\n\n"
            )
            + "Not: Gölge, olay ufkunun fotoğrafı değildir. Disk, jet ve 3B "
            "görselleştirme şematiktir; relativistik ışın izleme veya "
            "teleskop verisi analizi yapılmaz. Gerçek parametre çıkarımı "
            "birden fazla veri ve model belirsizliği gerektirir.\n"
        )
        try:
            with open(hedef, "w", encoding="utf-8") as dosya:
                dosya.write(rapor)
        except OSError as hata:
            messagebox.showerror(
                "Rapor kaydedilemedi",
                f"Dosya yazılırken hata oluştu:\n{hata}",
                parent=self.pencere,
            )
            return
        messagebox.showinfo(
            "Rapor kaydedildi",
            "Parametre raporu seçtiğin konuma kaydedildi.",
            parent=self.pencere,
        )

    def kara_delik_ciz(self, _olay=None):
        c = self.kara_delik_kanvasi
        c.delete("all")
        genislik = max(c.winfo_width(), 520)
        yukseklik = max(c.winfo_height(), 320)
        merkez_x = genislik * 0.5
        merkez_y = yukseklik * 0.53
        kutle_orani = (self.kutle_log.get() - 1) / 11
        olcek = min(genislik, yukseklik) * 0.135 * (0.9 + 0.2 * kutle_orani)

        rastgele = random.Random(37)
        for _ in range(145):
            x = rastgele.randrange(genislik)
            y = rastgele.randrange(yukseklik)
            renk = rastgele.choice(("#334155", "#475569", "#64748b", "#38bdf8"))
            c.create_oval(x, y, x + 2, y + 2, fill=renk, outline="")

        c.create_text(
            16, 14,
            text="3B ETKİLEŞİMLİ MODEL  •  sürükle: döndür  •  tekerlek: yakınlaştır",
            fill="#a5f3fc", anchor="nw", font=("Segoe UI", 9, "bold"),
        )
        c.create_text(
            16, 34,
            text=(
                f"{self.kara_delik_profili.get()}   |   "
                f"M={10 ** self.kutle_log.get():.2g} M☉   |   "
                f"a*={self.spin.get():.2f}   |   "
                f"eğim={self.egim.get():.0f}°"
            ),
            fill=SOLUK, anchor="nw", font=("Segoe UI", 9),
        )

        if self.jet_goster.get():
            for yon in (-1, 1):
                for yaricap, renk in (
                    (0.34, "#12334a"),
                    (0.22, "#155e75"),
                    (0.10, "#0e7490"),
                ):
                    noktalar = []
                    for x, z in (
                        (-yaricap, yon * 0.85),
                        (yaricap, yon * 0.85),
                        (0.018, yon * 3.0),
                        (-0.018, yon * 3.0),
                    ):
                        noktalar.extend(
                            self.kara_delik_noktasi_3d(
                                x, 0, z, merkez_x, merkez_y, olcek
                            )[:2]
                        )
                    c.create_polygon(*noktalar, fill=renk, outline="")

        yuzeyler = []
        if self.disk_goster.get():
            dis_yaricap = 3.15
            ic_yaricap = 1.45
            bolumler = 7
            aci_adim = 40
            disk_renkleri = (
                "#5b21b6", "#7c2d12", "#b45309", "#d97706",
                "#f59e0b", "#fcd34d", "#fff1b8",
            )
            for halka in range(bolumler):
                r0 = ic_yaricap + (dis_yaricap - ic_yaricap) * halka / bolumler
                r1 = ic_yaricap + (dis_yaricap - ic_yaricap) * (halka + 1) / bolumler
                renk = disk_renkleri[halka]
                for parca in range(aci_adim):
                    a0 = 2 * math.pi * parca / aci_adim
                    a1 = 2 * math.pi * (parca + 1) / aci_adim
                    kose_noktalar = (
                        (r0 * math.cos(a0), r0 * math.sin(a0), 0),
                        (r1 * math.cos(a0), r1 * math.sin(a0), 0),
                        (r1 * math.cos(a1), r1 * math.sin(a1), 0),
                        (r0 * math.cos(a1), r0 * math.sin(a1), 0),
                    )
                    izdususler = [
                        self.kara_delik_noktasi_3d(
                            x, y, z, merkez_x, merkez_y, olcek
                        )
                        for x, y, z in kose_noktalar
                    ]
                    derinlik = sum(nokta[2] for nokta in izdususler) / 4
                    parlaklik = max(0.55, min(1.35, 0.88 + derinlik * 0.12))
                    yuzeyler.append(
                        (
                            derinlik,
                            [koordinat for nokta in izdususler for koordinat in nokta[:2]],
                            self.kara_delik_renk_ac(renk, parlaklik),
                        )
                    )

        ufuk_orani = (1 + math.sqrt(1 - self.spin.get() ** 2)) / 2
        ufuk_yaricap = 0.86 * ufuk_orani
        enlem_adim = 9
        boylam_adim = 24
        enlemler = [
            -math.pi / 2 + math.pi * sira / enlem_adim
            for sira in range(enlem_adim + 1)
        ]
        boylamlar = [
            2 * math.pi * sira / boylam_adim
            for sira in range(boylam_adim + 1)
        ]
        for enlem_sira in range(enlem_adim):
            for boylam_sira in range(boylam_adim):
                kose_noktalar = []
                for enlem, boylam in (
                    (enlemler[enlem_sira], boylamlar[boylam_sira]),
                    (enlemler[enlem_sira + 1], boylamlar[boylam_sira]),
                    (enlemler[enlem_sira + 1], boylamlar[boylam_sira + 1]),
                    (enlemler[enlem_sira], boylamlar[boylam_sira + 1]),
                ):
                    kose_noktalar.append(
                        (
                            ufuk_yaricap * math.cos(enlem) * math.cos(boylam),
                            ufuk_yaricap * math.cos(enlem) * math.sin(boylam),
                            ufuk_yaricap * math.sin(enlem),
                        )
                    )
                izdususler = [
                    self.kara_delik_noktasi_3d(
                        x, y, z, merkez_x, merkez_y, olcek
                    )
                    for x, y, z in kose_noktalar
                ]
                derinlik = sum(nokta[2] for nokta in izdususler) / 4
                parlaklik = max(0.5, min(1.15, 0.65 + derinlik * 0.12))
                yuzeyler.append(
                    (
                        derinlik,
                        [koordinat for nokta in izdususler for koordinat in nokta[:2]],
                        self.kara_delik_renk_ac("#101827", parlaklik),
                    )
                )

        for _derinlik, noktalar, renk in sorted(yuzeyler, key=lambda yuzey: yuzey[0]):
            c.create_polygon(noktalar, fill=renk, outline="")

        if self.halka_goster.get():
            halka_noktalar = []
            halka_adim = 96
            for sira in range(halka_adim + 1):
                aci = 2 * math.pi * sira / halka_adim
                halka_noktalar.append(
                    self.kara_delik_noktasi_3d(
                        1.38 * math.cos(aci),
                        1.38 * math.sin(aci),
                        0.02,
                        merkez_x,
                        merkez_y,
                        olcek,
                    )
                )
            for onceki, sonraki in zip(halka_noktalar, halka_noktalar[1:]):
                renk = "#fde68a" if (onceki[2] + sonraki[2]) > 0 else "#f97316"
                c.create_line(
                    onceki[0], onceki[1], sonraki[0], sonraki[1],
                    fill=renk, width=2.2,
                )

        c.create_text(
            merkez_x + olcek * 1.55, merkez_y - olcek * 0.7,
            text="foton halkası", fill="#fde68a", anchor="w",
            font=("Segoe UI", 8),
        )
        c.create_text(
            merkez_x, merkez_y + olcek * 1.05,
            text="olay ufku (şematik)", fill=BEYAZ,
            font=("Segoe UI", 8),
        )
        c.create_text(
            16, yukseklik - 12,
            text="Görsel ölçekli fizik simülasyonu değildir; gölge, ufkun fotoğrafı değildir.",
            fill="#94a3b8", anchor="sw", font=("Segoe UI", 8),
        )

    def ust_bant_ciz(self, _olay=None):
        c = self.ust_bant
        c.delete("all")
        genislik = max(c.winfo_width(), 900)
        yukseklik = 130
        sol = (10, 28, 52)
        sag = (13, 61, 78)
        adim = 2

        for x in range(0, genislik, adim):
            oran = x / max(genislik - 1, 1)
            renk = tuple(
                round(sol[i] + (sag[i] - sol[i]) * oran) for i in range(3)
            )
            renk_hex = "#{:02x}{:02x}{:02x}".format(*renk)
            c.create_rectangle(x, 0, x + adim, yukseklik, fill=renk_hex, outline="")

        rastgele = random.Random(23)
        yildiz_renkleri = ("#64748b", "#94a3b8", "#67e8f9", "#c4b5fd")
        for _ in range(52):
            x = rastgele.uniform(genislik * 0.60, genislik - 16)
            y = rastgele.uniform(12, yukseklik - 12)
            yari_cap = rastgele.choice((1, 1, 1, 2))
            renk = rastgele.choice(yildiz_renkleri)
            c.create_oval(
                x - yari_cap, y - yari_cap, x + yari_cap, y + yari_cap,
                fill=renk, outline=""
            )

        c.create_oval(
            genislik - 190, 43, genislik - 182, 51,
            fill="#fef3c7", outline=""
        )
        c.create_line(
            genislik - 186, 36, genislik - 186, 58,
            fill="#fef3c7", width=1
        )
        c.create_line(
            genislik - 197, 47, genislik - 175, 47,
            fill="#fef3c7", width=1
        )

        c.create_text(
            28, 23,             text="KUANTUM  /  UZAY  /  BİLİM",
            fill="#a5f3fc", anchor="w", font=("Segoe UI", 10, "bold")
        )
        c.create_text(
            28, 57, text=self.uygulama_adi,
            fill=BEYAZ, anchor="w", font=("Segoe UI", 26, "bold")
        )
        c.create_text(
            30, 91,
            text="Tam sürüm  /  Kara delik, kuantum ve bilim deneyleri",
            fill="#dbeafe", anchor="w", font=("Segoe UI", 11)
        )

        rozet_yazi = f"TAM SÜRÜM {APP_VERSION} • EĞİTİM MODELİ"
        rozet_genislik = 270
        rozet_x = genislik - rozet_genislik - 24
        c.create_rectangle(
            rozet_x, 18, rozet_x + rozet_genislik, 45,
            fill="#0f2940", outline="#38bdf8", width=1
        )
        c.create_text(
            rozet_x + rozet_genislik / 2, 31,
            text=rozet_yazi, fill="#7dd3fc",
            font=("Segoe UI", 9, "bold")
        )

    def konu_destek_verileri(self):
        return {
            "Kuantum dünyasına giriş": (
                "particles",
                "Benzetme (sınırlı): Hava durumu haritası yağmuru göstermez; yağmur olasılığını gösterir. Elektron bulutu da olası ölçüm konumlarını anlatır.",
                "Mini etkinlik: Simülasyonda aynı ayarla 1000 çift ölç; tek sonuç yerine toplam örüntüye bak.",
            ),
            "Dalga fonksiyonu ve olasılık": (
                "probability",
                "Benzetme: Bir şehir haritasındaki yoğunluk renkleri gibi, olasılık bulutu da nerede ölçüm sonucu çıkmasının daha olası olduğunu gösterir.",
                "Mini etkinlik: Görseldeki noktaların her birini bir ölçüm örneği say; daha çok örnekle dağılımın nasıl belirginleştiğini incele.",
            ),
            "Spin ve ölçüm": (
                "axes",
                "Benzetme (sınırlı): Bir cetveli farklı yöne çevirmek gibi ölçüm eksenini değiştiriyoruz; spin, dönen minik bir top değildir.",
                "Mini etkinlik: A ve B açılarını aynı yapıp sonra aralarını aç; ölçülen korelasyonun değişimini gözle.",
            ),
            "Dolanıklık ve korelasyon": (
                "entanglement",
                "Benzetme (sınırlı): Eşleştirilmiş iki kart gibi düşünebilirsin; ama kuantum korelasyonları önceden yazılmış kartlarla tam açıklanamaz.",
                "Mini etkinlik: Aynı açıda 1000 çift ölç; A ve B sonuçlarının çoğunlukla zıt çıktığını kontrol et.",
            ),
            "Bell deneyleri": (
                "entanglement",
                "Benzetme: Bir kuralı farklı sorularla sınamak gibi; Bell deneyleri farklı ölçüm ayarlarında sonuç örüntülerini karşılaştırır.",
                "Mini etkinlik: Farklı A/B açılarını seçip kuramsal korelasyonun nasıl değiştiğini kaydet. Bu uygulama gerçek Bell testi değildir.",
            ),
            "Süperpozisyon": (
                "probability",
                "Benzetme (sınırlı): Bir akor birkaç notayı birlikte içerir; kuantum süperpozisyonu ise klasik notaların basit toplamı değildir.",
                "Mini etkinlik: Çift yarık düzeneği için parçacığın hangi-yol bilgisinin nasıl ölçülebileceğini çiz; bunun girişim desenine etkisini tahmin et.",
            ),
            "Belirsizlik ilkesi": (
                "axes",
                "Benzetme: Kısa bir sesin frekansını kesin belirlemek zordur; bu yalnızca sezgi benzetmesidir, kuantum belirsizliğinin tam açıklaması değildir.",
                "Mini etkinlik: Ölçüm cihazı hatası ile Heisenberg belirsizliğinin farkını iki cümleyle yaz.",
            ),
            "Kuantum tünelleme": (
                "probability",
                "Benzetme (sınırlı): Sis ince bir aralığın ötesine yayılabilir; kuantum tünelleme klasik bir parçacığın duvarı delmesi değildir.",
                "Mini etkinlik: Engel yükselir veya genişlerse tünelleme olasılığının nasıl değişmesini beklediğini çiz.",
            ),
            "Dekohorens ve kuantum teknolojileri": (
                "entanglement",
                "Benzetme: Hassas bir fısıltının gürültülü odada seçilememesi gibi çevre etkileşimleri kuantum faz ilişkilerini görünmez kılabilir.",
                "Mini etkinlik: İdeal simülasyona dedektör hatası eklense gözlenen korelasyonun neden zayıflayabileceğini açıkla.",
            ),
            "Ölçekler ve uzaklıklar": (
                "scale",
                "Benzetme: Dünya haritasında şehirleri küçültmek gibi, uzay ölçeklerini de temsil için küçültürüz; burada aralıklar gerçek ölçekte değil.",
                "Mini etkinlik: Ay'a giden ışığın yaklaşık 1,3 saniyede ulaştığını araştır; uzak cisimleri geçmişteki halleriyle görmemizi bununla ilişkilendir.",
            ),
            "Işık ve yıldızların özellikleri": (
                "spectrum",
                "Benzetme: Tayftaki çizgiler maddenin barkodu gibidir; benzetme, gerçek tayf çözümlemesinin yerini tutmaz.",
                "Mini etkinlik: Görseldeki koyu/açık çizgileri incele; bir tayf çizgisi kayarsa hareket hakkında hangi soruyu sorarsın?",
            ),
            "Kara delikler ve jetler": (
                "black_hole",
                "Benzetme (sınırlı): Olay ufku tek yönlü sınır gibi düşünülebilir; kara delik uzaydaki her şeyi uzaktan içine çeken bir elektrik süpürgesi değildir.",
                "Mini etkinlik: Şemada jetleri ve olay ufkunu bul. Jet gözlemlerinin neyi gösterebileceğini ve neyi tek başına kanıtlamayacağını ayır.",
            ),
            "Karanlık madde ve karanlık enerji": (
                "orbit",
                "Benzetme: Rüzgârı görmeden yaprakların hareketinden varlığını sezmek gibi, karanlık madde de ışığıyla değil kütleçekim etkileriyle araştırılır.",
                "Mini etkinlik: Bir cismin yörünge hareketini etkileyen görünmeyen kütle için en az iki alternatif açıklama yaz.",
            ),
            "Görelilik ve ışık hızı": (
                "spacetime",
                "Benzetme: Işık konisi, bir olayın hangi başka olayları etkileyebileceğini gösteren bir neden-sonuç haritasıdır.",
                "Mini etkinlik: Diyagramda ışık çizgilerinin dışında kalan bir noktaya bak; oraya mesajın neden anında ulaşamayacağını açıkla.",
            ),
            "Yıldızların yaşam döngüsü": (
                "spectrum",
                "Benzetme: Yıldızın yaşamı kütlesine göre farklı bir yakıt ömrü gibidir; füzyon kimyasal yanma değildir.",
                "Mini etkinlik: Güneş benzeri ve çok büyük kütleli bir yıldızın olası sonlarını karşılaştıran basit bir akış şeması çiz.",
            ),
            "Galaksiler ve kozmik yapı": (
                "orbit",
                "Benzetme: Galaksilerin dağılımı kozmik ağda düğümler ve iplikçikler gibi görünür; gerçek ağ kütleçekim ve madde dağılımıdır.",
                "Mini etkinlik: Bir galaksiyi yalnız fotoğrafıyla değil, tayfı ve uzaklık ölçümüyle nasıl araştırabileceğini listele.",
            ),
            "Ötegezegenler ve keşif yöntemleri": (
                "graph",
                "Benzetme: Transit, küçük bir sineğin lambanın önünden geçerken ışığı azıcık kısması gibidir; yıldız-gezegen oranları çok farklıdır.",
                "Mini etkinlik: Yıldız parlaklığı-zaman grafiğinde gezegen geçişinin oluşturacağı küçük düşüşü çiz.",
            ),
            "Kütleçekim dalgaları": (
                "spacetime",
                "Benzetme: Bir suya düşen taşın dalgası gibi yayılır; ancak kütleçekim dalgası suyu değil uzay-zaman geometrisini değiştirir.",
                "Mini etkinlik: LIGO’nun iki dik kolu karşılaştırmasının, çok küçük bir uzunluk değişimini nasıl yakalayabileceğini şemayla göster.",
            ),
            "Birimler ve mertebeler": (
                "scale",
                "Benzetme: Bir merdivende her basamağın 10 kat değişmesi gibi, bilimsel gösterim çok büyük/küçük sayıları kıyaslamayı kolaylaştırır.",
                "Mini etkinlik: 1.616 × 10⁻³⁵ sayısındaki üs ile 10⁻¹⁰ metreyi karşılaştır; Planck ölçeğinin ölçüldüğü sonucu çıkarmamaya dikkat et.",
            ),
            "Olasılık ve örnek sayısı": (
                "graph",
                "Benzetme: Bir madeni parayı birkaç kez atınca yazı-tura oranı şaşabilir; binlerce atışta oran genellikle yarıya yaklaşır.",
                "Mini etkinlik: Simülasyonda bir çift ve 1000 çift ölçüm sonuçlarını karşılaştır; küçük örneklerdeki dalgalanmayı fark et.",
            ),
            "Korelasyon ve nedensellik": (
                "graph",
                "Benzetme: Dondurma satışıyla güneş yanığının birlikte artması, dondurmanın yanığa neden olduğunu kanıtlamaz; sıcak hava ikisini de artırabilir.",
                "Mini etkinlik: Birlikte değişen iki şey düşün; ikisini etkileyebilecek üçüncü bir etken bul.",
            ),
            "Model ve varsayımlar": (
                "flow",
                "Benzetme: Harita yolları gösterir ama her ağacı göstermez; model de soruya yarayan bazı ayrıntıları seçer, bazılarını dışarıda bırakır.",
                "Mini etkinlik: Bu simülasyonun hangi varsayımları yaptığını ve hangi gerçek deney etkilerini içermediğini listele.",
            ),
            "Ölçüm belirsizliği": (
                "graph",
                "Benzetme: Cetvelin çizgi aralığı daha ince ayrıntıları seçmeyi sınırlar; belirsizlik yalnız dikkatsizlik demek değildir.",
                "Mini etkinlik: Aynı nesneyi birkaç kez ölç, en küçük bölmeyi not et ve sonuç aralığını açıkça yaz.",
            ),
            "Grafik okuma ve veriyi sunma": (
                "graph",
                "Benzetme: Grafik bir hikâyenin haritasıdır; eksen ve birim yoksa okuyucu nerede olduğunu bilemez.",
                "Mini etkinlik: Dört açı farkında 1000’er çift ölç, ölçülen ve kuramsal korelasyonu aynı grafiğe koy.",
            ),
            "Örnekleme ve yanlılık": (
                "probability",
                "Benzetme: Torbadan yalnız üstteki boncukları seçmek, bütün torbayı temsil etmeyebilir.",
                "Mini etkinlik: Rastgele seçim ve kolayda seçim yöntemlerinin örnek oranlarını karşılaştır; seçim yöntemini raporla.",
            ),
            "Boyut analizi ve tahmin": (
                "scale",
                "Benzetme: Bir tarifte bardak ve dakika karışırsa sonuç anlamsızlaşır; fizik formüllerinde de birimler uyumlu olmalı.",
                "Mini etkinlik: Bir hız-zaman hesabı yap, birimleri sadeleştir ve sonucun neden metre çıktığını göster.",
            ),
            "Rastgele simülasyon ve Monte Carlo": (
                "graph",
                "Benzetme: Zar atışlarını çok kez tekrarlamak, rastgele bir sürecin ortalama davranışını görmeye yardım eder.",
                "Mini etkinlik: 100, 1000 ve 10.000 örnekte ölçülen korelasyonu kaydet; her boyutta birden fazla tekrar yap.",
            ),
            "Araştırma sorusu": (
                "flow",
                "Benzetme: “Uzayı anlamak” çok geniştir; “ölçüm açısı korelasyonu nasıl değiştiriyor?” daha belirli bir rota çizer.",
                "Mini etkinlik: Büyük bir merakını ölçülebilir tek cümlelik soruya dönüştür.",
            ),
            "Hipotez, model ve kuram": (
                "flow",
                "Benzetme: Hipotez sınanacak bir tahmin, model çalışma maketi, bilimsel kuram ise çok kanıtı açıklayan kapsamlı çerçevedir.",
                "Mini etkinlik: Bir iddia seç ve onu hipotez, model ya da kuram olarak sınıflandır; nedenini yaz.",
            ),
            "Deney ve tekrarlanabilirlik": (
                "graph",
                "Benzetme: Bir tarifi başka biri aynı malzemelerle yapınca benzer sonuç alabiliyorsa tarif daha tekrarlanabilirdir.",
                "Mini etkinlik: Simülasyondaki açıları ve ölçüm sayısını yaz; başka birinin aynı adımları izlemesini sağla.",
            ),
            "Kaynak ve yapay zekâ desteği": (
                "flow",
                "Benzetme: Bir ekip çalışmasında kimin hangi parçayı yaptığı belirtilir; bilimsel projede de kaynak ve araç katkıları açıkça yazılır.",
                "Mini etkinlik: Projende hangi fikir, kod ve açıklamanın sana; hangisinin bir kaynağa ya da yapay zekâ yardımına ait olduğunu not et.",
            ),
            "Değişkenler ve kontrol": (
                "flow",
                "Benzetme: Yemek tarifinde tek malzemeyi değiştirip tadı karşılaştırmak, bir seferde bir değişkeni sınamaya benzer.",
                "Mini etkinlik: Bu simülasyonda bağımsız, bağımlı ve sabit tutulan değişkenleri tanımla.",
            ),
            "Kaynak taraması ve literatür": (
                "flow",
                "Benzetme: Yeni bir patika açmadan önce haritada mevcut yolları incelemek gibi, önce önceki çalışmaları öğren.",
                "Mini etkinlik: İki güvenilir kaynağı karşılaştır; aynı bilgiyi ve farklı vurguları not et.",
            ),
            "Etik, güvenlik ve dürüst veri": (
                "flow",
                "Benzetme: Deney günlüğü bir maçın tüm skorlarını yazmak gibidir; yalnız iyi giden denemeleri seçmek adil olmaz.",
                "Mini etkinlik: Simüle edilmiş veri ile gerçek deney verisini ayıran bir etiket tasarla.",
            ),
            "Proje planı ve ölçütler": (
                "flow",
                "Benzetme: Yolculuktan önce hedefi ve rotayı seçmek, araştırma yöntemini sonuçları görmeden planlamaya benzer.",
                "Mini etkinlik: Dört açı farkı için kaç ölçüm yapacağını ve hipotezini neyin destekleyeceğini önceden yaz.",
            ),
            "Sonuçları yorumlama ve sınırlılıklar": (
                "flow",
                "Benzetme: Bir harita belli yolları gösterir ama her arazi ayrıntısını değil; sonuçların da kapsamı ve sınırları vardır.",
                "Mini etkinlik: Bir bulgu, bir sınırlılık ve bu sınırlılığı giderecek sonraki adımı yaz.",
            ),
            "Kara delik ölçekleri ve parametreler": (
                "scale",
                "Benzetme: Bir haritada ölçeksiz çizilmiş daire gerçek boyutu vermez; kara delik görselinde kütle ve uzaklık ölçeğini ayrı hesaplamak gerekir.",
                "Mini etkinlik: Aynı kütleyi iki farklı uzaklığa koy; açısal boyutun neden değiştiğini formülle açıkla.",
            ),
            "Schwarzschild ve Kerr çözümleri": (
                "black_hole",
                "Benzetme (sınırlı): Dönmeyen model basit bir küreye, dönen model ise farklı ufuk geometrisine benzetilebilir; uzay-zaman gerçek bir kumaş değildir.",
                "Mini etkinlik: Aynı kütlede spin parametresini artırıp olay ufku yarıçapının nasıl değiştiğini laboratuvarda gözle.",
            ),
            "Olay ufku ve kara delik gölgesi": (
                "black_hole",
                "Benzetme: Bir tiyatro sahnesindeki karanlık alan ile sahnenin arkasındaki sınır aynı şey değildir; gölgeyi ışığın izlediği yollar oluşturur.",
                "Mini etkinlik: Olay ufku, gölge ve parlak halkayı ayrı renklerle çizip hangisinin doğrudan yüzey olmadığını belirt.",
            ),
            "Akresyon diski ve tayf": (
                "spectrum",
                "Benzetme: Isınan metalin rengi sıcaklığı hakkında ipucu verir; disk tayfı daha karmaşık olsa da ışık dalga boyları fiziksel koşulları sınırlar.",
                "Mini etkinlik: Diskin farklı dalga boylarında farklı görünmesinin olası nedenlerini listele.",
            ),
            "Kütleçekimsel merceklenme": (
                "spacetime",
                "Benzetme (sınırlı): Eğri cam ışığın yolunu değiştirir; kütleçekimde ışığı büken şey cam değil uzay-zaman geometrisidir.",
                "Mini etkinlik: Kara delik yakınından geçen ışınların doğrusal yollar yerine bükülmesini şemada göster.",
            ),
            "Süper kütleli kara delikler: Sgr A* ve M87*": (
                "black_hole",
                "Benzetme: İki şehir fotoğrafını kıyaslamak gibi, farklı kütle ve uzaklıktaki iki kara deliğin görüntülerini ölçekleri hesaba katarak karşılaştır.",
                "Mini etkinlik: Sgr A* ve M87* için kütle, uzaklık ve gözlem yöntemlerini güvenilir kaynaklardan bulup tabloya yaz.",
            ),
            "Jetler ve manyetik alanlar": (
                "orbit",
                "Benzetme (sınırlı): Bir fıskiyedeki akış çizgileri gibi jetler dar doğrultularda ilerler; astrofiziksel jetler plazma, manyetik alan ve görelilik içerir.",
                "Mini etkinlik: Jet yönü ve parlaklığının tek başına kütle veya spin ölçmeye neden yetmediğini iki belirsizlikle açıkla.",
            ),
            "Kara delik birleşmeleri ve dalgalar": (
                "spacetime",
                "Benzetme (sınırlı): İki dönen cismin dansı gibi düşünülebilir; birleşme sinyalini su dalgası değil, uzay-zamanın değişimi taşır.",
                "Mini etkinlik: Birleşme öncesi, birleşme ve sönümlenme evrelerini dalga biçiminde etiketle.",
            ),
            "Hawking ışınımı ve kuramsal sınırlar": (
                "flow",
                "Benzetme (sınırlı): Kuantum alanlarının eğri uzay-zamandaki etkisini bir hesaplama modeli gibi düşün; bu, kara deliğin çevresinde gözlenmiş sıcak bir yüzey demek değildir.",
                "Mini etkinlik: Kuramsal öngörü, astrofiziksel gözlem ve doğrudan ölçüm ifadelerini üç sütunda ayır.",
            ),
        }

    def konulari_hazirla(self):
        konu_listesi = [
            (
                "Kuantum Fiziği",
                "Atom ve atom altı ölçekte maddenin ve ışığın davranışını inceler.",
                [
                    (
                        "Kuantum dünyasına giriş",
                        "Kuantum fiziği; atom, elektron, foton gibi çok küçük "
                        "sistemlerde ölçümlerin hangi sonuçları verebileceğini "
                        "öngören fizik çerçevesidir. Klasik bir top için çoğu zaman "
                        "konum ve hızdan sonraki hareketi hesaplarız. Kuantum "
                        "sisteminde ise kuram çoğunlukla farklı sonuçların "
                        "olasılıklarını verir; tek bir ölçümün sonucu önceden "
                        "belirlenmiş olmayabilir. Bu, parçacığın “aklına geleni "
                        "yaptığı” demek değildir: olasılıklar matematiksel kurallara "
                        "uyar ve çok sayıda tekrar ölçülebilir örüntüler oluşturur.\n\n"
                        "Gerçek deney örneği: Tek tek gönderilen elektronların "
                        "çift yarık düzeneğinde birikerek girişim deseni "
                        "oluşturması, parçacık davranışını yalnız minik bilye "
                        "resmiyle anlatamayacağımızı gösterir. Benzetme olarak "
                        "hava durumu olasılık haritasını düşün: harita tek bir "
                        "yağmur damlasının yerini söylemez, olası sonuçların "
                        "dağılımını anlatır. Kuantum benzetmeleri sınırlıdır; "
                        "gerçek sistemi formüller ve deneyler tanımlar.",
                    ),
                    (
                        "Dalga fonksiyonu ve olasılık",
                        "Dalga fonksiyonu kuantum sisteminin durumunu matematiksel "
                        "olarak tanımlar. Uygun bir ölçüm sorusu seçildiğinde, "
                        "dalga fonksiyonundan farklı sonuçların olasılıkları "
                        "hesaplanabilir. Elektron bulutu çizimleri çoğunlukla "
                        "elektronu saran gerçek bir sis değildir; elektronun "
                        "nerede bulunabileceğine ilişkin olasılık yoğunluğunu "
                        "görselleştirir. Haritadaki koyu bir bölge “daha çok "
                        "ölçümün burada çıkması beklenir” fikrini taşır.\n\n"
                        "Önemli ayrıntı: Dalga fonksiyonunun kendisi doğrudan "
                        "fotoğraf gibi görülmez; ölçüm sonuçlarının istatistiği "
                        "karşılaştırılır. Çift yarık deneyinde tek tek gelen "
                        "elektronların ekranda oluşturduğu noktalar zamanla "
                        "girişim saçakları meydana getirir. Bu, olasılık "
                        "hesabının deneyle sınanmasına örnektir; gözlemcinin "
                        "bilincinin parçacığı sihirli biçimde değiştirdiğini "
                        "kanıtlamaz.",
                    ),
                    (
                        "Spin ve ölçüm",
                        "Spin, parçacığın açısal momentumla ilgili içsel kuantum "
                        "özelliğidir. Adı dönmeyi çağrıştırsa da elektronu minik "
                        "bir top gibi düşünmek doğru değildir. Spin-1/2 "
                        "parçacığı bir eksen boyunca ölçtüğümüzde ideal sonuçlar "
                        "+1/2 veya -1/2 olur; bu uygulama bunları kolaylık için "
                        "+1 ve -1 diye yazar. Başka eksen seçilirse ölçüm "
                        "olasılıkları değişebilir.\n\n"
                        "Tarihsel deney: Stern–Gerlach ekibi 1922’de gümüş "
                        "atomlarından oluşan demeti manyetik alandan geçirip "
                        "ekranda sürekli bir iz yerine ayrılmış izler gözledi. "
                        "Bu, açısal momentumun kuantumlanmasına dair önemli "
                        "kanıtlardandı. Buradaki çizgiler ölçüm yönünü temsilen "
                        "çizilmiştir; simülasyon gerçek mıknatıs veya atom "
                        "demeti içermez.",
                    ),
                    (
                        "Dolanıklık ve korelasyon",
                        "Dolanıklıkta iki parçacığın ortak kuantum durumu, "
                        "parçacıkları birbirinden bağımsız tarif etmeye "
                        "indirgenemeyebilir. Tek tek ölçümlerin sonucu rastgele "
                        "olsa da, iki taraftaki sonuçları birlikte sayınca "
                        "kuantum kuramının öngördüğü korelasyonlar görülür. "
                        "“Birini ölçünce diğeri anında haber alıyor” ifadesi "
                        "yanıltıcıdır: B tarafı yalnız kendi kayıtlarına bakarak "
                        "A’nın hangi sonucu veya ayarı seçtiğini anlayamaz.\n\n"
                        "Örnek: Simülasyonda iki ölçüm eksenini aynı yapıp çok "
                        "sayıda çift ölç. İdeal singlet modeli sonuçların zıt "
                        "olmasını öngörür. Sonra B eksenini değiştir; tek "
                        "ölçümlerin rastgele kaldığını, fakat birlikte "
                        "hesaplanan korelasyonun değiştiğini gör. Bu kayıtları "
                        "karşılaştırmak için yine normal, ışık hızını aşmayan "
                        "iletişim gerekir.",
                    ),
                    (
                        "Bell deneyleri",
                        "John Bell, 1964’te belirli yerel gizli değişken "
                        "modellerinin ölçüm korelasyonlarına getirdiği sınırları "
                        "matematiksel eşitsizliklerle ifade etti. Kuantum "
                        "mekaniği bazı ölçüm ayarlarında bu sınırların "
                        "aşılacağını öngörür. Laboratuvarda çok sayıda parçacık "
                        "çifti hazırlanır, farklı ölçüm ayarları rastgele "
                        "seçilir ve sonuç istatistikleri karşılaştırılır. "
                        "Tek bir çiftle Bell eşitsizliği test edilemez.\n\n"
                        "Gerçek deney örneği: John Clauser’ın foton deneyleri "
                        "kuantum öngörülerini destekleyen Bell eşitsizliği "
                        "ihlalleri buldu. Alain Aspect daha sonra ölçüm "
                        "ayarlarını foton çiftleri yoldayken değiştirerek "
                        "önemli bir açığı kapattı. 2022 Nobel Fizik Ödülü "
                        "Clauser, Aspect ve Zeilinger’e bu çalışmalar için "
                        "verildi. Bu deneyler kuantum korelasyonlarını "
                        "sınar; ışıktan hızlı mesaj veya ak delik bulmaz.",
                    ),
                    (
                        "Süperpozisyon",
                        "Süperpozisyon, bir kuantum durumunun seçilen ölçüm "
                        "açısından birden fazla olası sonucun birleşimiyle "
                        "tanımlanabilmesidir. Bu, parçacığın küçük bir kutuda "
                        "gizlenmiş ama bizim bilmediğimiz klasik bir cevaba "
                        "sahip olduğu anlamına gelmek zorunda değildir. "
                        "Ölçüm düzeni ve hangi niceliği ölçtüğümüz önemlidir. "
                        "Ölçüm yapıldığında tek bir sonuç kaydedilir; "
                        "olasılıkları kuram hesaplar.\n\n"
                        "Örnek: Fotonun iki farklı yolu bir arada tutabilen "
                        "durumu bir girişimölçerde yeniden birleştirildiğinde "
                        "girişim görülebilir. Hangi-yol bilgisi elde edecek "
                        "bir düzenek eklemek girişimi değiştirebilir; bunun "
                        "nedeni insan bilinci değil, fiziksel etkileşim ve "
                        "bilginin sistemle ilişkilendirilmesidir. Benzetme: "
                        "Bir müzik akorunda birkaç nota birlikte bulunur; "
                        "kuantum süperpozisyonu ise klasik notaların "
                        "basit toplamı değildir. Bu karşılaştırma yalnızca "
                        "“birden çok olasılık birlikte tanımlanır” fikrini "
                        "hatırlatır.",
                    ),
                    (
                        "Belirsizlik ilkesi",
                        "Heisenberg belirsizlik ilkesi, konum ve momentum "
                        "gibi belirli çiftlerin aynı kuantum durumunda "
                        "keyfî kesinlikle birlikte tanımlanamayacağını "
                        "söyler. Bu yalnızca kötü cetvel veya yetersiz "
                        "cihaz sorunu değildir; kuantum kuramının "
                        "matematiksel yapısından gelir. Konum belirsizliği "
                        "azaltılan bir dalga paketi, momentum sonuçlarında "
                        "daha geniş bir dağılımla ilişkilidir.\n\n"
                        "Benzetme: Çok kısa bir ses darbesinin hangi "
                        "frekanstan oluştuğunu tam belirlemek zor olabilir; "
                        "sesin zaman ve frekans çözünürlüğü arasında "
                        "bir ödünleşim vardır. Bu yalnızca sezgi vermek "
                        "içindir; kuantum belirsizlik bağıntısının "
                        "matematiksel tanımı değildir. Etkinlik: "
                        "Simülasyonun hangi belirsizlikleri içerdiğini "
                        "ve hangilerini (örneğin konum-momentum) "
                        "hiç hesaplamadığını listele. Bir simülasyondaki "
                        "rastgelelik tek başına Heisenberg ilkesini "
                        "göstermeye yetmez.",
                    ),
                    (
                        "Kuantum tünelleme",
                        "Kuantum tünellemede parçacığın dalga fonksiyonu "
                        "bir enerji engelinin içine ve bazen ötesine "
                        "uzanır; bu nedenle klasik fiziğin sıfır dediği "
                        "geçiş olasılığı kuantum modelinde sıfırdan "
                        "farklı olabilir. Parçacık engeli klasik bir "
                        "top gibi aşmak için gizlice fazladan enerji "
                        "almaz; sonuç olasılık dağılımıyla açıklanır. "
                        "Engelin yüksekliği ve genişliği geçiş "
                        "olasılığını etkiler.\n\n"
                        "Gerçek kullanım örnekleri: Güneş ve yıldızların "
                        "çekirdeklerindeki füzyon süreçlerinde tünelleme "
                        "önemlidir; taramalı tünelleme mikroskobu "
                        "yüzeye çok yakın bir uç ile yüzey arasındaki "
                        "tünelleme akımını ölçerek atom ölçeğinde "
                        "görüntüleme yapabilir. Benzetme: İnce bir "
                        "duvarın arkasına geçen sis gibi hayal edilebilir, "
                        "ama parçacık klasik sis değildir. Bu uygulamada "
                        "tünelleme hesaplanmıyor; yalnızca kavram "
                        "açıklanıyor.",
                    ),
                    (
                        "Dekohorens ve kuantum teknolojileri",
                        "Kuantum sistemleri çevreleriyle etkileşince "
                        "faz ilişkileri çevreye dağılır; bu sürece "
                        "dekoherens denir. Büyük sistemlerin neden "
                        "çoğu zaman klasik görünmesini anlamada önemli "
                        "bir kavramdır. Dekoherens, tek başına ölçüm "
                        "probleminin tüm yorumlarını çözdüğü veya "
                        "bilincin fiziksel rolünü kanıtladığı anlamına "
                        "gelmez.\n\n"
                        "Kuantum bilgi teknolojileri süperpozisyon, "
                        "dolanıklık ve ölçüm gibi özelliklerden yararlanır. "
                        "Kuantum bilgisayarlar her problemi daha hızlı "
                        "çözmez; belirli algoritmalar için avantaj "
                        "sağlayabilir ve hata düzeltme ciddi mühendislik "
                        "gerektirir. 2022 Nobel Fizik Ödülü dolaşık "
                        "foton deneylerinin yanı sıra kuantum bilgi "
                        "biliminin gelişimine katkıları vurguladı. "
                        "Etkinlik: Simülasyonda ideal sonuçları düşün; "
                        "gerçek laboratuvarda kayıp ve gürültü eklenirse "
                        "korelasyonun neden zayıflayabileceğini tartış.",
                    ),
                ],
            ),
            (
                "Uzay ve Astrofizik",
                "Yıldızları, gezegenleri, galaksileri ve evrenin büyük ölçekli "
                "yapısını inceler.",
                [
                    (
                        "Ölçekler ve uzaklıklar",
                        "Uzayda kilometreler hızla kullanışsız büyüklüklere "
                        "dönüşür. Astronomlar Güneş Sistemi’nde kilometre ve "
                        "astronomik birim; yıldızlar arası ölçekte ışık yılı "
                        "ve parsek kullanabilir. Işık yılı zaman değil, ışığın "
                        "bir yılda aldığı mesafedir: yaklaşık 9,46 trilyon "
                        "kilometre. Güneş ışığı Dünya’ya yaklaşık 8 dakika 20 "
                        "saniyede ulaşır; bu nedenle Güneş’i tam şu andaki "
                        "haliyle değil, ışığın yola çıktığı andaki haliyle "
                        "görürüz.\n\n"
                        "Mesafe ölçmenin bir yolu paralakstır: Dünya yörüngesinin "
                        "iki farklı noktasından bakıldığında yakın yıldızın "
                        "uzak yıldızlara göre görünen konumu az miktarda kayar. "
                        "Daha uzak cisimler için değişen parlaklığı bilinen "
                        "Cepheid yıldızları ve Tip Ia süpernovalar gibi "
                        "“standart mumlar” kullanılır. Benzetme: Başparmağını "
                        "önünde tutup sırayla bir gözünü kapat; yakındaki "
                        "başparmağın arka plana göre yer değiştirir. Gerçek "
                        "astronomik ölçümler çok hassas açılar ve kalibrasyon "
                        "gerektirir.",
                    ),
                    (
                        "Işık ve yıldızların özellikleri",
                        "Yıldızlar çoğunlukla sıcak gaz/plazmadan oluşur; "
                        "çekirdeklerindeki füzyon enerji sağlar ve kütleçekimi "
                        "ile iç basınç arasında denge kurulur. Teleskop yalnız "
                        "şekil çekmez: spektrograf ışığı dalga boylarına "
                        "ayırarak tayf oluşturur. Atomlar ve iyonlar belirli "
                        "dalga boylarında ışığı soğurup yaydığı için tayftaki "
                        "çizgiler kimyasal bileşim hakkında ipucu verir. "
                        "Süreklilik tayfının rengi/sıcaklığı da yıldızın yüzey "
                        "sıcaklığı hakkında bilgi taşır.\n\n"
                        "Hareket, tayf çizgilerinin Doppler kaymasıyla "
                        "araştırılabilir: kayma kırmızıya ise kaynak bizden "
                        "uzaklaşıyor, maviye ise yaklaşıyor olabilir. Bu "
                        "ölçüm görüş doğrultusundaki hızı verir; cismin bütün "
                        "hareketini tek başına vermez. Benzetme: Tayf, "
                        "maddenin barkodu gibidir; ama barkodun çözülmesi "
                        "laboratuvar kalibrasyonu ve doğru fizik bilgisi "
                        "gerektirir. NASA’nın yıldız rehberi, yıldızların "
                        "doğumu, yaşamı ve ölümünü özetler.",
                    ),
                    (
                        "Kara delikler ve jetler",
                        "Kara delik, kütlenin çok küçük bir hacimde toplandığı "
                        "ve olay ufkunun içinden dışarı ışık sinyali "
                        "ulaştıramadığı bir uzay-zaman bölgesidir. Olay ufku "
                        "katı bir yüzey değildir. Kara delikler uzaktaki "
                        "cisimleri elektrik süpürgesi gibi çekmez; aynı "
                        "kütledeki başka bir cisimle uzaktan kütleçekimleri "
                        "aynı olur. Madde çevredeki yığılma diskinde ısınarak "
                        "ışık yayabilir; bazı aktif sistemlerde güçlü "
                        "manyetik alanlarla ilişkili, ışık hızına yakın "
                        "parçacık jetleri oluşur.\n\n"
                        "Görünmeyeni bulma örneği: Samanyolu merkezindeki "
                        "yıldızların yörüngeleri, görünmeyen çok büyük bir "
                        "kütlenin varlığını gösterdi; bu çalışma 2020 Nobel "
                        "Fizik Ödülü’nde tanındı. Başka yöntemler X-ışını "
                        "ışımasını, kütleçekimsel merceklenmeyi ve LIGO gibi "
                        "dedektörlerin kütleçekim dalgası ölçümlerini kullanır. "
                        "Jetin yönü tek başına kara deliğin tüm kütlesini ve "
                        "dönüşünü vermez; mesafe, eğim, çevre gazı ve "
                        "ölçümlerin belirsizliği de hesaba katılır.",
                    ),
                    (
                        "Karanlık madde ve karanlık enerji",
                        "Karanlık madde ve karanlık enerji adları benzer "
                        "duyulsa da aynı şey değildir. Karanlık madde, ışık "
                        "yaymayan/soğurmayan fakat kütleçekim etkisiyle "
                        "galaksilerin ve kümelerin hareketini, ayrıca "
                        "arkadaki ışığın merceklenmesini etkileyen bir "
                        "bileşendir. NASA’nın özetlediği standart kozmoloji "
                        "bütçesinde sıradan madde evrenin yaklaşık %5’ini, "
                        "karanlık madde yaklaşık %27’sini oluşturur; bunlar "
                        "doğrudan sayım değil, kozmolojik modele dayalı "
                        "tahminlerdir.\n\n"
                        "Karanlık enerji ise evrenin genişlemesinin "
                        "hızlanmasını açıklamak için kullanılan addır; "
                        "doğasının ne olduğu bilinmiyor. 1990’ların sonunda "
                        "uzak Tip Ia süpernovaların parlaklık/mesafe "
                        "ölçümleri hızlanan genişlemeye kanıt sağladı. "
                        "Ekstra boyut, yeni parçacık veya değiştirilmiş "
                        "kütleçekimi gibi açıklamalar araştırma hipotezidir; "
                        "kanıtlanmış cevap diye sunulmamalıdır.",
                    ),
                    (
                        "Görelilik ve ışık hızı",
                        "Özel görelilik, boşluktaki ışık hızını tüm eylemsiz "
                        "gözlemciler için aynı kabul eder ve uzay ile zamanı "
                        "birlikte ele alır. Kütleli cisimler ışık hızına "
                        "ulaşamaz; bu, daha fazla enerji gerektirmeleriyle "
                        "ilişkilidir. Genel görelilikte kütle ve enerji "
                        "uzay-zaman geometrisiyle bağlantılıdır; serbest "
                        "düşen cisimler bu geometride doğal yolları izler.\n\n"
                        "Test örnekleri: Uçaklarda taşınan atom saatleri "
                        "yerdeki saatlerle karşılaştırıldı; sonuçlarda "
                        "görelilik düzeltmeleri görüldü. GPS uydularındaki "
                        "atom saatleri hem özel hem genel görelilik etkileri "
                        "için düzeltilir. “Dolanıklıkta korelasyon anlık” "
                        "demek, bir gözlemcinin ışık hızını aşan kontrollü "
                        "mesaj aldığı anlamına gelmez. Işık konisi, hangi "
                        "olayların birbirine sinyal gönderebileceğini anlatan "
                        "şematik bir haritadır.",
                    ),
                    (
                        "Yıldızların yaşam döngüsü",
                        "Yıldızlar soğuk gaz ve toz bulutlarının kütleçekimiyle "
                        "çökmesiyle oluşur. Merkez yeterince ısınınca "
                        "hidrojen çekirdekleri füzyonla helyuma dönüşür. "
                        "Füzyonun dışa doğru basıncı ile kütleçekimin "
                        "içe doğru etkisi arasında uzun süreli denge "
                        "kurulur. Yıldızın kütlesi ne kadar hızlı yakıt "
                        "tükettiğini ve ömrünün sonundaki yolu belirler.\n\n"
                        "Güneş gibi düşük/orta kütleli bir yıldız sonunda "
                        "dış katmanlarını atıp beyaz cüce bırakır. Çok "
                        "büyük kütleli yıldızlar süpernova ile patlayıp "
                        "nötron yıldızı veya kara delik bırakabilir. "
                        "Bunlar genel evrim yollarıdır; gerçek son "
                        "kütleye, bileşime ve etkileşimlere bağlıdır. "
                        "NASA’nın yıldız rehberi bu aşamaları anlatır. "
                        "Benzetme: Yıldız bir yakıt deposu gibi düşünülebilir, "
                        "ama enerji üretimi kimyasal yanma değil nükleer "
                        "füzyondur.",
                    ),
                    (
                        "Galaksiler ve kozmik yapı",
                        "Galaksi; yıldızlar, gaz, toz, karanlık madde ve "
                        "başka bileşenlerin kütleçekimle bağlı olduğu "
                        "büyük sistemdir. Sarmal, eliptik ve düzensiz "
                        "şekiller görülür; galaksiler zaman içinde "
                        "çarpışıp birleşebilir. Aralarındaki boşluk "
                        "tamamen boş değildir; seyrek gaz ve büyük "
                        "ölçekli kozmik ağ yapıları bulunur.\n\n"
                        "Gökbilimciler galaksilerin ışığını, tayfını, "
                        "şeklini ve hareketini ölçer. Uzaklıklar ve "
                        "kırmızıya kaymalar birlikte kullanıldığında "
                        "evrenin genişlemesi incelenebilir. 2019 Nobel "
                        "Fizik Ödülü James Peebles’in fiziksel kozmoloji "
                        "çalışmalarını ve Michel Mayor ile Didier "
                        "Queloz’nun ötegezegen keşfini tanıdı. Benzetme: "
                        "Kozmik ağ, şehirlerin karayolu ağına benzetilebilir; "
                        "ama evrenin yapısı yollarla değil kütleçekim ve "
                        "madde dağılımıyla oluşur.",
                    ),
                    (
                        "Ötegezegenler ve keşif yöntemleri",
                        "Ötegezegen, Güneş Sistemi dışındaki gezegendir. "
                        "Çoğu doğrudan fotoğraflanmaz; yıldız ışığında "
                        "oluşturduğu küçük, tekrarlı etkilerden bulunur. "
                        "Transit yönteminde gezegen yıldızının önünden "
                        "geçerken parlaklıkta azalma ölçülür. Radyal hız "
                        "yönteminde gezegenin kütleçekimi yıldızın "
                        "hareketini ve tayf çizgilerini hafifçe değiştirir.\n\n"
                        "1995’te Michel Mayor ve Didier Queloz, Güneş benzeri "
                        "bir yıldız çevresindeki 51 Pegasi b gezegenini "
                        "duyurarak ötegezegen araştırmalarında dönüm "
                        "noktası yarattı; bu keşif 2019 Nobel Fizik "
                        "Ödülü’nde tanındı. Bir gezegenin “yaşanabilir "
                        "bölgede” olması yaşam bulunduğunu kanıtlamaz; "
                        "atmosfer, su, yıldız etkinliği ve birçok koşul "
                        "önemlidir. NASA’nın kataloğu keşif yöntemlerini "
                        "ve doğrulanmış gezegenleri günceller.",
                    ),
                    (
                        "Kütleçekim dalgaları",
                        "Kütleçekim dalgaları, ivmelenen büyük kütlelerin "
                        "uzay-zamanda oluşturduğu ve ışık hızında yayılan "
                        "dalgalanmalardır. Birbirinin çevresinde dönen "
                        "kara delikler veya nötron yıldızları enerji "
                        "kaybederek yaklaşabilir; birleşme sırasında "
                        "güçlü sinyal oluşur. Dalganın kendisi görünür "
                        "bir su dalgası değildir; dedektörler iki dik "
                        "yöndeki uzunluk değişimini lazer interferometresiyle "
                        "karşılaştırır.\n\n"
                        "LIGO, 2015’te iki kara deliğin birleşmesinden "
                        "kaynaklanan kütleçekim dalgalarını ilk kez "
                        "doğrudan gözlediğini duyurdu; sinyal çok küçük "
                        "uzunluk değişimlerini seçebilmek için hassas "
                        "ölçüm gerektiriyordu. Bu gözlem kara deliğin "
                        "fotoğrafını çekmek değildir; dalga biçiminden "
                        "kaynağın özellikleri çıkarılır. Benzetme: "
                        "Uzak bir kamyon geçerken zemindeki çok küçük "
                        "titreşimi ölçmek gibi; fakat gerçek sinyal "
                        "uzay-zamanın değişimidir. Kaynak LIGO açıklaması "
                        "bu yöntemi özetler.",
                    ),
                ],
            ),
            (
                "Matematik ve Ölçüm",
                "Fikirleri sayısal modellere dönüştürür ve sonuçların belirsizliğini "
                "değerlendirir.",
                [
                    (
                        "Birimler ve mertebeler",
                        "Her ölçüm bir sayıdan ve birimden oluşur: “5” tek "
                        "başına uzunluk mu, saniye mi söylemez. Bilimsel "
                        "gösterim çok büyük/küçük sayıları a × 10ⁿ biçiminde "
                        "yazmayı sağlar. Örneğin 0,0000001 = 1 × 10⁻⁷’dir. "
                        "Bir mertebe fark, yaklaşık 10 kat değişim demektir.\n\n"
                        "NIST’in 2022 CODATA önerilen değeri Planck "
                        "uzunluğunu yaklaşık 1,616255 × 10⁻³⁵ metre verir. "
                        "Bu, temel sabitlerden türetilen önemli bir kuramsal "
                        "ölçektir; “deneyde ölçülmüş en küçük piksel” olduğu "
                        "kanıtlanmış değildir. Atom büyüklüğü yaklaşık "
                        "10⁻¹⁰ metre mertebesindedir; Planck uzunluğuna "
                        "oranı kabaca 10²⁵ mertebesidir. Benzetme için "
                        "merdiven düşün: her basamak 10 kat küçülür. "
                        "Üsleri çıkarırken birimleri aynı tutmak ve yaklaşık "
                        "işareti gerektiğinde kullanmak önemlidir.",
                    ),
                    (
                        "Olasılık ve örnek sayısı",
                        "Olasılık, tek bir denemede sonucu kesin söylemek "
                        "yerine farklı sonuçların ne sıklıkla beklenebileceğini "
                        "anlatır. Adil para atışında yazı olasılığı 1/2’dir; "
                        "bu, her iki atışta mutlaka bir yazı geleceği anlamına "
                        "gelmez. 10 atışta 8 yazı görmek mümkün, ama çok daha "
                        "büyük tekrar sayılarında oran genellikle 1/2 çevresinde "
                        "toplanır.\n\n"
                        "Bu, büyük sayılar yasasının sezgisel sonucudur; "
                        "yakınsama tam ve düzgün ilerlemez, arada sapmalar "
                        "olur. Simülasyonda önce bir çift, sonra 1000 çift "
                        "ölçüp korelasyonları kıyasla. Daha güvenilir sonuç "
                        "için deneyi tekrar et ve değişkenliği de kaydet. "
                        "Bir grafikte örnek sayısını x, ölçülen ortalamayı "
                        "y eksenine koyabilirsin. Bu bilgisayar örnekleri "
                        "gerçek laboratuvar verisi değil, modelden üretilen "
                        "rastgele sonuçlardır.",
                    ),
                    (
                        "Korelasyon ve nedensellik",
                        "Korelasyon iki değişkenin birlikte değişme biçimini "
                        "özetler. Pozitif korelasyonda biri artarken diğeri "
                        "de artma eğilimindedir; negatif korelasyonda biri "
                        "artarken diğeri azalma eğiliminde olabilir. Sıfıra "
                        "yakın korelasyon, seçilen ölçekte doğrusal bir "
                        "ilişkinin zayıf olduğunu söyler; her tür ilişki "
                        "yok demek değildir.\n\n"
                        "Korelasyon tek başına neden-sonuç kanıtlamaz. "
                        "Örneğin yazın dondurma satışları ve güneş yanıkları "
                        "beraber artabilir; olası ortak etken sıcak ve güneşli "
                        "havadır. Nedensellik için zaman sırası, olası "
                        "karıştırıcı değişkenler ve deney düzeni incelenir. "
                        "Dolanıklık deneylerinde de korelasyon ölçülür ama "
                        "bu korelasyonla mesaj gönderildiği sonucu çıkmaz. "
                        "Grafikte eksen aralıklarını ve hangi verilerin "
                        "dışarıda kaldığını belirtmek yorumun dürüstlüğü "
                        "açısından önemlidir.",
                    ),
                    (
                        "Model ve varsayımlar",
                        "Bilimsel model, bir soruyu yanıtlamak için gerçekliğin "
                        "seçilmiş yönlerini temsil eder. Harita gibi model de "
                        "bazı ayrıntıları gösterir, bazılarını atlar. Bu "
                        "uygulamadaki olasılık modeli ideal spin-1/2 singlet "
                        "çifti, belirli ölçüm eksenleri ve ideal ölçümler "
                        "varsayar. Dedektör gürültüsü, parçacık kaybı, "
                        "laboratuvar kalibrasyonu ve deneydeki diğer "
                        "sistematik etkileri modellemez.\n\n"
                        "Bir model kurarken varsayımları, girdileri, denklemi "
                        "ve hangi durumda işe yaramayacağını yaz. Sonra "
                        "çıktıyı analitik beklenti veya güvenilir deney "
                        "verisiyle karşılaştır. Model gerçek veriye "
                        "uymazsa, bu “doğa yanıldı” demek değil; varsayım, "
                        "kod ya da ölçüm koşullarını yeniden inceleme "
                        "nedenidir. Bir bilgisayar grafiğinin güzel görünmesi "
                        "tek başına modelin doğru olduğunu kanıtlamaz.",
                    ),
                    (
                        "Ölçüm belirsizliği",
                        "Hiçbir ölçüm sonsuz basamaklı kesinlikte değildir. "
                        "Bir cetvelin çizgi aralığı, sensörün hassasiyeti, "
                        "kalibrasyon ve ölçümü yapan kişinin yöntemi sonuca "
                        "belirsizlik katar. Sonucu “12,4 ± 0,2 cm” yazmak, "
                        "ölçümün hangi aralıkta makul olduğunu ve yöntemin "
                        "çözünürlüğünü açıklar; bu aralıktaki her değer eşit "
                        "olasılıklı demek değildir.\n\n"
                        "Tekrarlı ölçümler rastgele saçılmayı gösterir; "
                        "kalibrasyon hatası gibi sistematik etkiler tekrar "
                        "sayısını artırmakla kendiliğinden kaybolmaz. "
                        "Örnek etkinlik: Bir nesneyi cetvelle birkaç kez "
                        "ölç, en küçük bölmeyi not et, ölçümlerin en küçük "
                        "ve en büyük değerini yaz. Gerçek araştırmada "
                        "belirsizlik yöntemi veriye ve ölçüm aracına göre "
                        "seçilir; sonuçtan sonra istenen cevabı verecek "
                        "şekilde uydurulmaz.",
                    ),
                    (
                        "Grafik okuma ve veriyi sunma",
                        "Grafik, sayıların örüntüsünü hızlı görmeye yardım "
                        "eder; fakat başlık, eksen etiketi ve birim yoksa "
                        "yanlış anlaşılabilir. X eksenine değiştirilen "
                        "ayarları, y eksenine ölçülen sonucu koy. Nokta "
                        "grafiği tek tek ölçümleri, çizgi grafiği zaman "
                        "içindeki değişimi, sütun grafiği kategorileri "
                        "karşılaştırmaya uygundur.\n\n"
                        "Simülasyon etkinliği: A ve B açı farkını 0°, 30°, "
                        "60°, 90° yap; her ayarda aynı sayıda çift ölç ve "
                        "ölçülen korelasyonu kaydet. Beklenen ideal değer "
                        "E = -cos(Δ) ile aynı grafikte göster. Eksen "
                        "ölçeğini sıfırdan başlatıp başlatmadığını açıkla; "
                        "başlıkta bunun simülasyon verisi olduğunu belirt. "
                        "Grafiğin çizgi tipi veya rengi, ölçüme ek kanıt "
                        "katmaz; yöntem ve ham veri önemlidir.",
                    ),
                    (
                        "Örnekleme ve yanlılık",
                        "Örnekleme, bütün evreni ölçemediğimizde ondan "
                        "bir grup seçme işlemidir. Seçim biçimi sonuçları "
                        "etkileyebilir. Yalnız kolay ulaşılan kişileri "
                        "sormak, tüm toplumu temsil etmeyebilir; yalnız "
                        "başarılı denemeleri raporlamak da sonuçları "
                        "olduğundan daha güçlü gösterir.\n\n"
                        "Fizik deneylerinde de algılama eşiğinin altındaki "
                        "olaylar, dedektörün çalışmadığı süreler veya "
                        "belirli koşullarda kaybolan parçacıklar örneklemi "
                        "etkileyebilir. Etkinlik: Bir torbadan renkli "
                        "boncukları gözleri kapalı ve sonra yalnız üstten "
                        "seçerek örnekle; iki yöntemin oranları aynı mı "
                        "karşılaştır. Gerçek deneyde seçim kuralları "
                        "önceden belirlenmeli ve kaç ölçümün dışlandığı "
                        "rapor edilmelidir.",
                    ),
                    (
                        "Boyut analizi ve tahmin",
                        "Denklemlerde birimler, formülün mantıklı olup "
                        "olmadığını kontrol etmeye yardım eder. Örneğin "
                        "hız birimi metre/saniyedir; bir uzunluk formülü "
                        "sonunda metre vermelidir. Bir denklemde metreyi "
                        "saniyeyle toplamak anlamlı değildir. Boyut analizi "
                        "sayısal katsayıları her zaman bulmaz ama birçok "
                        "yanlış formülü fark ettirir.\n\n"
                        "Önce kaba tahmin yap: Dünya’dan Ay’a ışığın "
                        "yaklaşık 1,3 saniyede ulaştığı biliniyorsa, "
                        "uzaklığın kilometre mertebesini ışık hızını "
                        "süreyle çarparak tahmin edebilirsin. Sonra "
                        "birimleri sadeleştirip sonucu kontrol et. Bu "
                        "yaklaşım, Planck ölçeği gibi çok küçük sayıları "
                        "düşünürken de kullanılır; mertebe tahmini kesin "
                        "ölçümün yerini almaz.",
                    ),
                    (
                        "Rastgele simülasyon ve Monte Carlo",
                        "Monte Carlo yöntemi, olasılıksal bir sistemi "
                        "rastgele örnekler üreterek sayısal incelemektir. "
                        "Bu uygulama ölçüm sonuçlarını olasılıklardan "
                        "örnekler; bu yüzden aynı düğmeye tekrar basınca "
                        "küçük farklar çıkabilir. Çok sayıda örnek, "
                        "kuramsal ortalama ile karşılaştırma sağlar.\n\n"
                        "Bir tekrarda aynı tohumu (seed) kullanmak "
                        "rastgele sayı dizisini tekrar üretmeye yardım "
                        "eder; farklı tohumlar yeni örnekler verir. "
                        "Etkinlik: Aynı açı farkı için 100, sonra 1000, "
                        "sonra 10.000 örneğin ölçülen korelasyonunu "
                        "karşılaştır. Yakınsama mükemmel ve tek yönlü "
                        "olmak zorunda değildir. Kodun örnekleme "
                        "kuralını açıklamak ve analitik formülle "
                        "doğrulamak gerekir.",
                    ),
                ],
            ),
            (
                "Bilimsel Yöntem ve Simülasyon",
                "Soruları sınanabilir hale getirir; kanıt, varsayım ve sonucu "
                "birbirinden ayırır.",
                [
                    (
                        "Araştırma sorusu",
                        "Araştırma sorusu merakı ölçülebilir bir hedefe "
                        "çevirir. “Kuantum çok garip mi?” çok geniş ve "
                        "kişisel bir sorudur. “İdeal singlet simülasyonunda "
                        "A ve B eksenleri arasındaki açı değişince ölçülen "
                        "korelasyon nasıl değişiyor?” ise değişkeni, "
                        "ölçümü ve çalışma sınırını belirtir.\n\n"
                        "İyi soruda kim/neyin ölçüldüğü, hangi koşulların "
                        "değiştirildiği, hangi sonucun kaydedildiği ve "
                        "ne kadar süre/örnek gerektiği anlaşılır. Önce "
                        "konuyla ilgili güvenilir kaynakları tara; "
                        "başkalarının neyi ölçtüğünü, hangi sınırlara "
                        "sahip olduğunu öğren. Sonra sorunu küçült ve "
                        "danışmanla uygulanabilirliğini konuş. Araştırma "
                        "sorusu sonuç garantisi vermez; negatif veya "
                        "beklenmeyen sonuç da öğrenme sağlar.",
                    ),
                    (
                        "Hipotez, model ve kuram",
                        "Hipotez, veriyle karşılaştırılabilen açık bir "
                        "öngörüdür. Örneğin: “Bu ideal simülasyonda "
                        "ölçüm eksenleri aynı olduğunda 1000 çiftin "
                        "korelasyonu -1’e yakın olacaktır.” Model bu "
                        "öngörüyü hesaplayan matematiksel veya bilgisayar "
                        "temsildir. Deney ise gözlem/ölçüm yoluyla "
                        "modelin öngörülerini sınar.\n\n"
                        "Bilimsel kuram, günlük dildeki tahmin anlamına "
                        "gelmez. Evrim kuramı veya genel görelilik gibi "
                        "kuramlar çok sayıda kanıtı bir araya getiren, "
                        "sürekli sınanan açıklama çerçeveleridir. Bir "
                        "simülasyona kendi adını verip “yeni teori” demek "
                        "onu bilimsel kuram yapmaz. Önce mevcut bilgiyi "
                        "öğren, özgün ve sınanabilir bir hipotez belirle, "
                        "yöntemini açıkla ve sonuçların iddianı destekleyip "
                        "desteklemediğini tarafsızca değerlendir.",
                    ),
                    (
                        "Deney ve tekrarlanabilirlik",
                        "Deney, bir soruyu gözlem ve ölçümle sınamak için "
                        "önceden planlanır. Tekrarlanabilirlik için "
                        "malzemeler, ölçüm ayarları, örnek sayısı, "
                        "veri işleme adımları ve dışlama kuralları "
                        "açıklanmalıdır. Sonuç beklenenden farklı çıkınca "
                        "başarısız denemeleri saklamak ve olası hata "
                        "kaynaklarını belirtmek gerekir.\n\n"
                        "Bell deneylerinde ekipler çok sayıda dolaşık "
                        "foton çifti ölçer; farklı ayarlar seçer ve "
                        "sonuçların istatistiklerini karşılaştırır. "
                        "Bağımsız grupların deneyleri tekrar etmesi "
                        "bulguların güvenini artırır. Evde güvenli "
                        "etkinlik: Uygulamada açıları ve örnek sayısını "
                        "önceden seç, sonucu çalıştırmadan önce tahmin "
                        "et, sonra 3 tekrar yap ve tüm sonuçları yaz. "
                        "Bu, gerçek kuantum laboratuvarı değildir; "
                        "kod simülasyonunu tekrarlama çalışmasıdır.",
                    ),
                    (
                        "Kaynak ve yapay zekâ desteği",
                        "Kaynak taraması, sorunun daha önce nasıl "
                        "çalışıldığını ve hangi bilgilerin yerleşik "
                        "olduğunu öğrenmeye yarar. Önce bilim kurumları, "
                        "hakemli makaleler ve Nobel gibi ödül sayfaları "
                        "tercih edilir; popüler yazıdaki iddialar asıl "
                        "kaynağa kadar izlenmelidir. Bu uygulamada her "
                        "bölümün altındaki kaynak bağlantısına tıklayarak "
                        "NASA, Nobel, NIST veya National Academies "
                        "sayfalarını açabilirsin.\n\n"
                        "Yapay zekâ fikir, açıklama veya kod taslağı "
                        "üretebilir; yanlış bilgi de üretebilir. Kaynağı "
                        "okumak, hesaplamayı kontrol etmek, kodu anlamak "
                        "ve AI katkısını danışmanına/kuralların istediği "
                        "şekilde açıklamak gerekir. Fikir, kod, görsel "
                        "ve metin katkılarını birbirinden ayır. Yarışma "
                        "kuralları dönemlere göre değişebileceği için "
                        "başvurmadan önce güncel TÜBİTAK kılavuzunu "
                        "öğretmeninle kontrol et.",
                    ),
                    (
                        "Değişkenler ve kontrol",
                        "Bir deneyde bağımsız değişken araştırmacının "
                        "değiştirdiği; bağımlı değişken ölçtüğü sonuçtur. "
                        "Kontrol edilen değişkenler aynı tutulmaya "
                        "çalışılır. Simülasyonda ölçüm açı farkı bağımsız "
                        "değişken, ölçülen korelasyon bağımlı değişkendir; "
                        "örnek sayısını sabit tutmak karşılaştırmayı "
                        "kolaylaştırır.\n\n"
                        "Gerçek bir düzenekte sıcaklık, ışık, cihaz "
                        "kalibrasyonu veya örnek seçimi sonucu "
                        "etkileyebilir. Bir seferde bir temel değişkeni "
                        "değiştirip diğer koşulları kaydetmek, sebebi "
                        "ayırt etmeye yardım eder. Etkinlik: 0°, 30°, "
                        "60° ve 90° açı farklarında aynı sayıda simülasyon "
                        "ölçümü yap. Her turda farklı sayıda örnek "
                        "kullanırsan açı etkisiyle örnekleme gürültüsü "
                        "birbirine karışabilir.",
                    ),
                    (
                        "Kaynak taraması ve literatür",
                        "Literatür taraması, “bu fikir kesinlikle hiç "
                        "yapılmadı” demek için değil, yakın çalışmaların "
                        "ne bulduğunu anlamak için yapılır. Başlık ve "
                        "anahtar sözcükleri farklı biçimlerde ara; "
                        "özet kadar yöntem, sonuç ve sınırlılıkları da "
                        "oku. Bir kaynağın yayın tarihi, yazar/kurum "
                        "uzmanlığı ve dayandığı makaleler önemlidir.\n\n"
                        "Örnek: Dolaşıklıkta Bell eşitsizlikleri için "
                        "2022 Nobel Fizik Ödülü sayfası deneylerin "
                        "Clauser, Aspect ve Zeilinger katkılarını "
                        "özetler. Kara delikler için NASA, karanlık "
                        "madde için NASA, temel sabitler için NIST "
                        "sayfalarını karşılaştır. Makalenin iddiasını "
                        "kaynağın gerçekten destekleyip desteklemediğini "
                        "kontrol et. Bu başlıkların çoğu onlarca yıllık "
                        "araştırma alanıdır; özgün proje, bilinen sonucu "
                        "dürüstçe yeniden incelemek veya yeni bir "
                        "sınanabilir soruyu daraltmak olabilir.",
                    ),
                    (
                        "Etik, güvenlik ve dürüst veri",
                        "Bilimsel etik; veriyi uydurmamak, değiştirmemek, "
                        "başkasının emeğini kaynak göstermeden almamak "
                        "ve sonuçları olduğundan güçlü sunmamaktır. "
                        "Beklentiyle uyuşmayan veri de raporlanır. "
                        "İnsanlardan anket alınacaksa mahremiyet ve "
                        "gerekli izinler gözetilir; deneyde tehlikeli "
                        "kimyasallar, yüksek gerilim, lazer veya "
                        "gözetimsiz araçlar kullanılmaz.\n\n"
                        "Bu proje yazılım simülasyonudur; gerçek "
                        "parçacıkları ölçmüyor. Simüle edilmiş veriyi "
                        "laboratuvar verisi diye tanıtma. Kullandığın "
                        "kodun ve görsellerin kaynağını açıkla; "
                        "öğretmeninden güvenlik ve yarışma kuralları "
                        "konusunda yardım al. Dürüst bir sınırlılık "
                        "bölümü projenin zayıflığı değil, neyi "
                        "gerçekten bildiğini gösteren güçlü bir "
                        "bilimsel alışkanlıktır.",
                    ),
                    (
                        "Proje planı ve ölçütler",
                        "Bir proje planı araştırma sorusu, kısa kaynak "
                        "özeti, hipotez, yöntem, veri tablosu, zaman "
                        "planı ve sınırlılıkları içerir. Önce hangi "
                        "sonucun hipotezi destekleyeceğini ve hangi "
                        "sonucun desteklemeyeceğini yaz. Sonra veri "
                        "toplama adımlarını önceden belirle.\n\n"
                        "Bu simülasyon için örnek ölçüt: Dört açı "
                        "farkının her birinde 1000 çift ölç; ölçülen "
                        "korelasyon ile E = -cos(Δ) beklentisinin "
                        "mutlak farkını karşılaştır. Sonuçlar rastgele "
                        "olduğu için tek koşu değil birkaç tekrar "
                        "yap; ortalama ve yayılımı belirt. Bu yalnız "
                        "bilinen ideal modeli doğrulama etkinliğidir, "
                        "yeni fizik keşfi değildir. Proje sergisi "
                        "için çalışan arayüzün yanında yöntem ve "
                        "bilimsel katkının ne olduğunu anlat.",
                    ),
                    (
                        "Sonuçları yorumlama ve sınırlılıklar",
                        "Sonuç bölümü önce ne ölçtüğünü, kaç tekrar "
                        "yaptığını ve ne bulduğunu söyler; yorum "
                        "bölümü bunun soruna ne cevap verdiğini tartışır. "
                        "Kuramsal değerle uyuşma, kullanılan modelin "
                        "beklentisini yeniden ürettiğini gösterir; "
                        "doğanın yeni bir yasasını bulduğunu tek "
                        "başına göstermez.\n\n"
                        "Sınırlılıklar açıkça yazılmalı: burada ideal "
                        "olasılık modeli kullanılıyor, gerçek foton "
                        "kaynağı veya dedektör yok; Bell eşitsizliği "
                        "için gerekli farklı ayar kombinasyonları ve "
                        "deneysel açılmalar kapsamlı biçimde "
                        "modellenmiyor. Sonraki adım önerisi bu "
                        "sınırlılıktan doğabilir: örneğin standart "
                        "Bell-CHSH istatistiğini doğru ayarlarla "
                        "hesaplamak. İddiaları kanıtın ötesine "
                        "taşımamak bilimsel güvenilirliğin temelidir.",
                    ),
                ],
            ),
            (
                "Kara Delikler: Derinlemesine",
                "Olay ufku, uzay-zaman, ışık ve gözlemleri bir araya getir. "
                "Bu bölümdeki görseller şemadır; fiziksel ölçek ve gerçek "
                "gözlem verileri ayrı ayrı değerlendirilmelidir.",
                [
                    (
                        "Kara delik ölçekleri ve parametreler",
                        "Kütle, uzaklık ve dönme birbirinden farklı parametrelerdir. "
                        "Bir kara deliğin kütlesi Güneş kütlesiyle, uzaklığı parsek "
                        "veya megaparsekle ifade edilebilir. Ufuk yarıçapı kütleyle "
                        "doğru orantılıdır; gökyüzünde kapladığı açısal ölçek ise "
                        "uzaklık arttıkça küçülür.\n\n"
                        "Laboratuvardaki kütle ve uzaklık kaydırıcıları logaritmiktir: "
                        "eşit adım sayısal değeri eşit miktarda değil, katlar "
                        "halinde değiştirir. Açısal gölge çapı, basit modelde "
                        "yaklaşık 10,4 GM/c² uzunluğunun uzaklığa oranıdır. Bu "
                        "yaklaşım, plazma, teleskop yanıtı veya ölçüm hatalarını "
                        "hesaplamaz; sonuç kuramsal ölçek tahminidir.",
                    ),
                    (
                        "Schwarzschild ve Kerr çözümleri",
                        "Schwarzschild çözümü dönmeyen, yüksüz ve çevresinde madde "
                        "bulunmayan ideal bir kara deliği tanımlar. Kerr çözümü "
                        "dönen, yüksüz ideal kara deliği ele alır. Gerçek "
                        "astrofiziksel sistemler gaz, manyetik alan ve çevre "
                        "etkileri içerdiğinden bu çözümler gözlemlerin yorumlanması "
                        "için fiziksel modellerdir.\n\n"
                        "Boyutsuz spin a* arttıkça Kerr olay ufkunun koordinat "
                        "yarıçapı azalır; laboratuvar bu ilişkiyi gösterir. Ancak "
                        "ekrandaki disk ve jet çizimleri sayısal genel görelilik "
                        "çözümü değildir. Ölçümde spin, kütle, eğim ve akış "
                        "modelinin etkileri birbirine karışabilir.",
                    ),
                    (
                        "Olay ufku ve kara delik gölgesi",
                        "Olay ufku, içinden dışarıya geleceğe yönelmiş ışık "
                        "sinyalinin ulaşamadığı sınırdır; katı bir yüzey gibi "
                        "ışık saçmaz. Teleskopta görülen karanlık gölge ise "
                        "yakın çevredeki ışığın bükülmesi, yakalanması ve "
                        "gözlemciye ulaşan ışınların geometrisiyle oluşur.\n\n"
                        "Gölgenin çevresindeki parlak halka, sıcak plazmanın "
                        "ışınımı ile kütleçekimsel merceklenmenin birleşik "
                        "sonucudur. Bu nedenle “kara deliğin fotoğrafı” ifadesi "
                        "popüler bir kısaltmadır: görüntü, olay ufkunun yüzey "
                        "fotoğrafı değil, ufuk yakınındaki çevrenin radyo "
                        "ışınımından yeniden oluşturulmuş görüntüdür.",
                    ),
                    (
                        "Akresyon diski ve tayf",
                        "Gaz kara deliğe düşerken açısal momentumu nedeniyle "
                        "hemen içeri düşmez; dönen akış oluşturabilir. Viskoz "
                        "ve manyetik süreçler enerjiyi dağıtır, gazı ısıtır "
                        "ve farklı dalga boylarında ışınım doğurur. Diskin "
                        "parlaklığı yalnız kara deliğin kütlesine bağlı değildir: "
                        "madde akış hızı, optik kalınlık ve geometri de önemlidir.\n\n"
                        "Tayf, dalga boylarına göre ışık dağılımını gösterir. "
                        "Spektral çizgilerin biçimi ve genişliği hız, sıcaklık "
                        "ve kimyasal koşullar hakkında ipucu verebilir. Disk "
                        "modelleri bu verileri yorumlar; model varsayımları "
                        "değiştiğinde çıkarılan spin veya kütle de değişebilir.",
                    ),
                    (
                        "Kütleçekimsel merceklenme",
                        "Genel göreliliğe göre kütle ve enerji uzay-zaman "
                        "geometrisiyle ilişkilidir; ışık bu geometride bükülmüş "
                        "yollar izler. Kara deliğin yakınından geçen ışık "
                        "gözlemciye farklı yollardan ulaşabilir, parlak halkalar "
                        "ve görüntü bozulmaları oluşturabilir.\n\n"
                        "Merceklenme yalnız kara deliklerin çevresinde görülmez; "
                        "galaksiler ve galaksi kümeleri de arka plan kaynaklarını "
                        "büyütüp biçimlendirebilir. Etkinlik: Düz bir ışın "
                        "çizmek yerine, kütleli cismin iki yanından geçen "
                        "ışın yolları çiz ve gözlemcinin hangi görüntüleri "
                        "alabileceğini tartış. Çizim nicel ışın izleme hesabı "
                        "değildir.",
                    ),
                    (
                        "Süper kütleli kara delikler: Sgr A* ve M87*",
                        "Samanyolu merkezindeki Sgr A* ve M87 galaksisinin "
                        "merkezindeki M87*, EHT tarafından incelenen iki "
                        "süper kütleli kara delik adayıdır. Kütleleri ve "
                        "uzaklıkları çok farklı olduğundan, gökyüzünde "
                        "kapladıkları açısal ölçekleri yalnız kütlelerine "
                        "bakarak kıyaslamak doğru olmaz.\n\n"
                        "EHT görüntülerinin elde edilmesi, farklı teleskop "
                        "istasyonlarından gelen verilerin kalibrasyonu ve "
                        "görüntü oluşturma yöntemlerini gerektirir. Sgr A* "
                        "çevresindeki gazın değişkenliği görüntü yorumunu "
                        "zorlaştırır. Karşılaştırma etkinliği: her iki kaynak "
                        "için kütle, uzaklık, dalga boyu ve görüntü ölçeğini "
                        "resmî kaynaklardan toplayıp tabloya yaz.",
                    ),
                    (
                        "Jetler ve manyetik alanlar",
                        "Bazı aktif galaksi çekirdeklerinde kara delik çevresinden "
                        "uzaklara uzanan dar plazma jetleri görülür. Jetlerin "
                        "enerji kaynağı ve oluşum ayrıntıları, akresyon diski "
                        "ile manyetik alanların ve kara deliğin dönmesinin "
                        "etkileşimini içerir. Madde olay ufkunun içinden "
                        "kaçmaz; jetler çevredeki madde ve alanlarla ilişkilidir.\n\n"
                        "Jetin parlaklığı ve yönü gözlemciye göre değişebilir. "
                        "Doppler etkisi, eğim, plazma yoğunluğu ve manyetik "
                        "geometri yorumda önemlidir. Bu yüzden tek bir jet "
                        "görüntüsü kara deliğin tüm kütlesini ve spinini "
                        "kesin olarak ölçmez. Laboratuvar jetleri yalnızca "
                        "şematik olarak çizer.",
                    ),
                    (
                        "Kara delik birleşmeleri ve dalgalar",
                        "İkili kara delikler birbirinin çevresinde dolanırken "
                        "sistemin kütleçekim dalgaları yayması beklenir. "
                        "Yörünge enerjisi azaldıkça cisimler yaklaşır, birleşir "
                        "ve oluşan cisim kısa bir sönümlenme evresi geçirir. "
                        "Dalga sinyalinin frekans ve genliği zamanla değişir.\n\n"
                        "LIGO gibi lazer interferometreleri bu dalgaların "
                        "oluşturduğu çok küçük göreli uzunluk değişimlerini "
                        "ölçer. Dedektör verisi gürültü, kalibrasyon ve "
                        "kuramsal dalga biçimleriyle birlikte analiz edilir. "
                        "Bu yöntem elektromanyetik görüntüden farklıdır: "
                        "ışık görmeden de kompakt cisimlerin birleşmesi "
                        "hakkında bilgi sağlayabilir.",
                    ),
                    (
                        "Hawking ışınımı ve kuramsal sınırlar",
                        "Kuantum alan kuramı ile eğri uzay-zamanın birlikte "
                        "incelenmesi, kara deliklerin sıcaklık ve ışınım "
                        "özellikleri olabileceğini öngörür. Bu öngörü "
                        "Hawking ışınımı olarak bilinir. Astrofiziksel kara "
                        "delikler için beklenen etki son derece zayıftır ve "
                        "bugüne dek doğrudan gözlenmiş bir kara delik "
                        "Hawking ışınımı olarak sunulmamalıdır.\n\n"
                        "Bu konu, genel görelilik, kuantum kuramı ve "
                        "termodinamiği birleştiren araştırma alanlarının "
                        "önemli bir örneğidir. Bilimsel sunumda kuramsal "
                        "öngörü, benzetim, dolaylı kanıt ve doğrudan gözlem "
                        "ifadelerini ayır. Bu uygulama Hawking ışınımını "
                        "hesaplamaz veya ölçmez.",
                    ),
                ],
            ),
        ]

        govde = ttk.Frame(self.konular_sekmesi, padding=14)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(0, weight=1)

        sol = ttk.Frame(govde)
        sol.grid(row=0, column=0, sticky="nsw", padx=(0, 14))
        kaydirma = ttk.Scrollbar(sol, orient=tk.VERTICAL)
        self.konu_listesi = ttk.Treeview(
            sol,
            show="tree",
            selectmode="browse",
            yscrollcommand=kaydirma.set,
            height=25,
        )
        kaydirma.config(command=self.konu_listesi.yview)
        self.konu_listesi.pack(side=tk.LEFT, fill=tk.Y)
        kaydirma.pack(side=tk.RIGHT, fill=tk.Y)

        sag = ttk.Frame(govde)
        sag.grid(row=0, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(2, weight=1)
        self.konu_baslik = ttk.Label(
            sag, text="Bir bölüm seç", font=("Segoe UI", 16, "bold")
        )
        self.konu_baslik.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.konu_gorsel = tk.Canvas(
            sag,
            width=600,
            height=170,
            bg=PANEL,
            highlightthickness=0,
        )
        self.konu_gorsel.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.konu_metni = tk.Text(
            sag,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg=PANEL,
            fg=BEYAZ,
            padx=24,
            pady=20,
            relief=tk.FLAT,
            height=8,
        )
        self.konu_metni.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=11,
            lmargin1=6, rmargin=6,
        )
        self.konu_metni.grid(
            row=2, column=0, sticky="nsew", pady=(8, 8)
        )
        metin_kaydirma = ttk.Scrollbar(
            sag, orient=tk.VERTICAL, command=self.konu_metni.yview
        )
        metin_kaydirma.grid(row=2, column=1, sticky="ns")
        self.konu_metni.config(yscrollcommand=metin_kaydirma.set)
        self.benzetme = ttk.Label(
            sag,
            text="",
            wraplength=590,
            justify=tk.LEFT,
            font=("Segoe UI", 11),
        )
        self.benzetme.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 3))
        self.etkinlik = ttk.Label(
            sag,
            text="",
            wraplength=590,
            justify=tk.LEFT,
            font=("Segoe UI", 11),
        )
        self.etkinlik.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(3, 0))
        self.kaynak_linki = tk.Label(
            sag,
            text="",
            bg=ARKA_PLAN,
            fg=MAVI,
            cursor="hand2",
            font=("Segoe UI", 10, "underline"),
            anchor="w",
        )
        self.kaynak_linki.grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(7, 0)
        )

        self.konu_destek = self.konu_destek_verileri()
        self.konu_kaynaklari = self.konu_kaynak_verileri()
        self.konu_icerikleri = {}
        ilk_bolum = None
        for konu_sirasi, (konu, giris, bolumler) in enumerate(konu_listesi):
            konu_id = f"konu_{konu_sirasi}"
            self.konu_listesi.insert("", tk.END, iid=konu_id, text=konu, open=True)
            self.konu_icerikleri[konu_id] = (konu, giris, "overview")
            for bolum_sirasi, (baslik, aciklama) in enumerate(bolumler):
                bolum_id = f"bolum_{konu_sirasi}_{bolum_sirasi}"
                self.konu_listesi.insert(
                    konu_id, tk.END, iid=bolum_id, text=baslik
                )
                self.konu_icerikleri[bolum_id] = (
                    baslik,
                    aciklama,
                    self.konu_destek[baslik][0],
                )
                if ilk_bolum is None:
                    ilk_bolum = bolum_id

        self.konu_listesi.bind("<<TreeviewSelect>>", self.konu_secildi)
        self.konu_listesi.selection_set(ilk_bolum)
        self.konu_goster(ilk_bolum)

    def konu_kaynak_verileri(self):
        nobel_entanglement = (
            "Nobel Fizik Ödülü 2022 — dolaşıklık ve Bell deneyleri",
            "https://www.nobelprize.org/prizes/physics/2022/press-release/",
        )
        nasa_stars = (
            "NASA — yıldızlar",
            "https://science.nasa.gov/universe/stars/",
        )
        nasa_black_holes = (
            "NASA — kara delikler",
            "https://science.nasa.gov/universe/black-holes/",
        )
        nasa_dark_matter = (
            "NASA — karanlık madde",
            "https://science.nasa.gov/dark-matter/",
        )
        nasa_dark_energy = (
            "NASA — karanlık enerji ve evrenin genişlemesi",
            "https://science.nasa.gov/dark-energy/",
        )
        nobel_cosmology = (
            "Nobel Fizik Ödülü 2019 — kozmoloji ve ötegezegenler",
            "https://www.nobelprize.org/prizes/physics/2019/press-release/",
        )
        nobel_dark_energy = (
            "Nobel Fizik Ödülü 2011 — hızlanan evren",
            "https://www.nobelprize.org/prizes/physics/2011/press-release/",
        )
        national_academies = (
            "National Academies — fen eğitimi ve bilimsel uygulamalar",
            "https://www.nationalacademies.org/projects/DBASSE-CFE-09-16/publication/13165",
        )
        eht = (
            "Event Horizon Telescope — işbirliği ve gözlemler",
            "https://eventhorizontelescope.org/",
        )
        ligo = (
            "LIGO Caltech — kütleçekim dalgaları",
            "https://www.ligo.caltech.edu/page/what-are-gw",
        )
        return {
            "Kuantum dünyasına giriş": nobel_entanglement,
            "Dalga fonksiyonu ve olasılık": nobel_entanglement,
            "Spin ve ölçüm": nobel_entanglement,
            "Dolanıklık ve korelasyon": nobel_entanglement,
            "Bell deneyleri": nobel_entanglement,
            "Süperpozisyon": nobel_entanglement,
            "Belirsizlik ilkesi": nobel_entanglement,
            "Kuantum tünelleme": national_academies,
            "Dekohorens ve kuantum teknolojileri": nobel_entanglement,
            "Ölçekler ve uzaklıklar": nasa_dark_energy,
            "Işık ve yıldızların özellikleri": nasa_stars,
            "Kara delikler ve jetler": nasa_black_holes,
            "Karanlık madde ve karanlık enerji": nasa_dark_matter,
            "Görelilik ve ışık hızı": (
                "Nobel Fizik Ödülü 2020 — kara delikler ve genel görelilik",
                "https://www.nobelprize.org/prizes/physics/2020/summary/",
            ),
            "Yıldızların yaşam döngüsü": nasa_stars,
            "Galaksiler ve kozmik yapı": nobel_cosmology,
            "Ötegezegenler ve keşif yöntemleri": (
                "NASA — ötegezegenler",
                "https://science.nasa.gov/exoplanets/",
            ),
            "Kütleçekim dalgaları": (
                "LIGO Caltech — kütleçekim dalgaları nedir?",
                "https://www.ligo.caltech.edu/page/what-are-gw",
            ),
            "Birimler ve mertebeler": (
                "NIST CODATA — Planck uzunluğunun değeri",
                "https://physics.nist.gov/cgi-bin/cuu/Value?plkl",
            ),
            "Olasılık ve örnek sayısı": (
                "National Academies — fen eğitimi ve kanıt değerlendirme çerçevesi",
                "https://www.nationalacademies.org/projects/DBASSE-CFE-09-16/publication/13165",
            ),
            "Korelasyon ve nedensellik": national_academies,
            "Model ve varsayımlar": national_academies,
            "Ölçüm belirsizliği": national_academies,
            "Grafik okuma ve veriyi sunma": national_academies,
            "Örnekleme ve yanlılık": national_academies,
            "Boyut analizi ve tahmin": (
                "NIST CODATA — temel sabitler ve birimler",
                "https://physics.nist.gov/cuu/Constants/",
            ),
            "Rastgele simülasyon ve Monte Carlo": national_academies,
            "Araştırma sorusu": national_academies,
            "Hipotez, model ve kuram": national_academies,
            "Deney ve tekrarlanabilirlik": nobel_entanglement,
            "Değişkenler ve kontrol": national_academies,
            "Kaynak taraması ve literatür": nobel_cosmology,
            "Etik, güvenlik ve dürüst veri": national_academies,
            "Proje planı ve ölçütler": national_academies,
            "Sonuçları yorumlama ve sınırlılıklar": national_academies,
            "Kara delik ölçekleri ve parametreler": (
                "NIST CODATA — temel sabitler",
                "https://physics.nist.gov/cuu/Constants/",
            ),
            "Schwarzschild ve Kerr çözümleri": nasa_black_holes,
            "Olay ufku ve kara delik gölgesi": eht,
            "Akresyon diski ve tayf": nasa_black_holes,
            "Kütleçekimsel merceklenme": nasa_black_holes,
            "Süper kütleli kara delikler: Sgr A* ve M87*": eht,
            "Jetler ve manyetik alanlar": nasa_black_holes,
            "Kara delik birleşmeleri ve dalgalar": ligo,
            "Hawking ışınımı ve kuramsal sınırlar": nasa_black_holes,
            "Kaynak ve yapay zekâ desteği": (
                "TÜBİTAK — resmî site (güncel yarışma kılavuzlarını kontrol et)",
                "https://www.tubitak.gov.tr/",
            ),
        }

    def konu_secildi(self, _olay):
        secim = self.konu_listesi.selection()
        if secim:
            self.konu_goster(secim[0])

    def metni_bolumlere_ayir(self, widget, metin, tek_bolum="AÇIKLAMA"):
        widget.delete("1.0", tk.END)
        widget.tag_configure(
            "bolum_basligi",
            foreground=MAVI,
            font=("Segoe UI", 9, "bold"),
            spacing1=12,
            spacing3=4,
            lmargin1=8,
        )
        widget.tag_configure(
            "bolum_metni",
            foreground=BEYAZ,
            font=("Segoe UI", 12),
            spacing1=3,
            spacing2=2,
            spacing3=15,
            lmargin1=8,
            lmargin2=8,
            rmargin=8,
        )
        paragraflar = [
            parca.strip()
            for parca in metin.replace("\r\n", "\n").split("\n\n")
            if parca.strip()
        ]
        adlar = ("TEMEL FİKİR", "DENEY / ÖRNEK", "BAĞLANTI / SINIR")
        for sira, paragraf in enumerate(paragraflar):
            etiket = (
                tek_bolum
                if len(paragraflar) == 1
                else adlar[min(sira, len(adlar) - 1)]
            )
            widget.insert(tk.END, etiket + "\n", "bolum_basligi")
            widget.insert(tk.END, paragraf + "\n\n", "bolum_metni")

    def konu_goster(self, secilen_id):
        baslik, aciklama, gorsel_turu = self.konu_icerikleri[secilen_id]
        self.konu_baslik.config(text=baslik)
        self.konu_metni.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(self.konu_metni, aciklama)
        self.konu_metni.config(state=tk.DISABLED)
        if baslik in self.konu_destek:
            _tur, benzetme, etkinlik = self.konu_destek[baslik]
        else:
            benzetme = "Bu başlık, altındaki bölümlerin genel tanıtımıdır."
            etkinlik = "Soldan bir bölüm seçerek görsel, benzetme ve etkinliği aç."
        self.benzetme.config(text=benzetme)
        self.etkinlik.config(text=etkinlik)
        kaynak = self.konu_kaynaklari.get(baslik)
        if kaynak:
            kaynak_adi, url = kaynak
            self.kaynak_linki.config(text=f"Kaynak: {kaynak_adi}")
            self.kaynak_linki.bind(
                "<Button-1>", lambda _olay, adres=url: webbrowser.open(adres)
            )
        else:
            self.kaynak_linki.config(text="")
            self.kaynak_linki.unbind("<Button-1>")
        self.konu_gorsel_ciz(gorsel_turu)

    def konu_gorsel_ciz(self, tur):
        c = self.konu_gorsel
        c.delete("all")
        rastgele = random.Random(41)
        for _ in range(28):
            x = rastgele.randint(8, 590)
            y = rastgele.randint(12, 160)
            c.create_oval(
                x, y, x + 2, y + 2,
                fill=rastgele.choice(("#475569", "#64748b", "#38bdf8")),
                outline="",
            )
        c.create_text(
            12, 12, text="Görsel örnek (şematik)", fill=SOLUK,
            anchor="nw", font=("Segoe UI", 9)
        )

        if tur == "particles":
            c.create_text(300, 30, text="Olasılık bulutu", fill=BEYAZ)
            for _ in range(150):
                x = random.gauss(300, 65)
                y = random.gauss(95, 35)
                if 170 < x < 430 and 42 < y < 150:
                    c.create_oval(x, y, x + 3, y + 3, fill=MAVI, outline="")
            c.create_oval(297, 92, 303, 98, fill=BEYAZ, outline="")
        elif tur == "probability":
            c.create_text(300, 30, text="Olası sonuçların örnek dağılımı", fill=BEYAZ)
            heights = (35, 65, 92, 118, 95, 68, 38)
            renkler = (MAVI, MOR, PEMBE, TURUNCU, PEMBE, MOR, MAVI)
            for i, height in enumerate(heights):
                x = 170 + i * 38
                c.create_rectangle(
                    x, 145 - height, x + 22, 145, fill=renkler[i], outline=""
                )
            c.create_line(150, 145, 460, 145, fill=SOLUK)
        elif tur == "axes":
            c.create_text(300, 30, text="Ölçüm ekseni değişince soru da değişir", fill=BEYAZ)
            for angle, color, x in ((25, MAVI, 250), (-35, TURUNCU, 350)):
                rad = math.radians(angle)
                dx, dy = math.cos(rad) * 55, math.sin(rad) * 55
                c.create_line(x - dx, 95 + dy, x + dx, 95 - dy, fill=color, width=4)
                c.create_oval(x - 5, 90, x + 5, 100, fill=BEYAZ, outline="")
            c.create_text(250, 155, text="A", fill=MAVI)
            c.create_text(350, 155, text="B", fill=TURUNCU)
        elif tur == "entanglement":
            c.create_text(300, 30, text="Ortak durum → ilişkili sonuçlar", fill=BEYAZ)
            c.create_oval(95, 70, 165, 140, outline=MAVI, width=4)
            c.create_oval(435, 70, 505, 140, outline=TURUNCU, width=4)
            c.create_text(130, 105, text="A", fill=MAVI, font=("Segoe UI", 16, "bold"))
            c.create_text(470, 105, text="B", fill=TURUNCU, font=("Segoe UI", 16, "bold"))
            c.create_line(170, 105, 430, 105, fill=MOR, dash=(5, 4), width=3)
            c.create_text(300, 130, text="Bu çizgi mesaj/sinyal değildir", fill=SOLUK)
        elif tur == "spectrum":
            c.create_text(300, 30, text="Işık tayfı: uzaktan gelen bir barkod gibi", fill=BEYAZ)
            renkler = ("#6b4cff", "#4169e1", "#00a5ff", "#35c878", "#ffd43b", "#ff8c32", "#ed4141")
            for i, renk in enumerate(renkler):
                x = 150 + i * 40
                c.create_rectangle(x, 75, x + 38, 125, fill=renk, outline="")
            for x in (205, 329, 393):
                c.create_line(x, 72, x, 128, fill="#ffffff", width=2)
            c.create_text(300, 150, text="Çizgiler, ışığı yayan madde hakkında ipucu verir", fill=SOLUK)
        elif tur == "black_hole":
            c.create_text(300, 30, text="Kara delik çevresi ve jetler (şematik)", fill=BEYAZ)
            c.create_oval(255, 65, 345, 155, fill="#000000", outline=MOR, width=3)
            c.create_oval(230, 86, 370, 134, outline=TURUNCU, width=5)
            c.create_line(300, 63, 300, 38, fill=MAVI, width=7)
            c.create_line(300, 157, 300, 165, fill=PEMBE, width=7)
            c.create_text(300, 175, text="Görsel ölçekli değildir; gerçek jetlerin modeli değildir", fill=SOLUK)
        elif tur == "orbit":
            c.create_text(300, 30, text="Görünmeyen kütle, hareketi etkileyebilir", fill=BEYAZ)
            c.create_oval(190, 53, 410, 157, outline=MOR, dash=(4, 3), width=2)
            c.create_oval(287, 85, 313, 111, fill=TURUNCU, outline="")
            c.create_oval(390, 98, 402, 110, fill=MAVI, outline="")
            c.create_text(300, 175, text="Şematik yörünge: doğrudan görüntü değil, hareket verisi", fill=SOLUK)
        elif tur == "spacetime":
            c.create_text(300, 30, text="Uzay-zamanda ışık konisi (şematik)", fill=BEYAZ)
            c.create_line(300, 50, 205, 155, fill=MAVI, width=3)
            c.create_line(300, 50, 395, 155, fill=MAVI, width=3)
            c.create_line(150, 105, 450, 105, fill=SOLUK, dash=(4, 3))
            c.create_oval(294, 44, 306, 56, fill=TURUNCU, outline="")
            c.create_text(300, 165, text="Nedensel etkiler ışık konisinin dışına taşınamaz", fill=SOLUK)
        elif tur == "scale":
            c.create_text(300, 30, text="Boyutları karşılaştır (eşit aralıklı çizim değil)", fill=BEYAZ)
            c.create_line(90, 100, 510, 100, fill=SOLUK, width=3)
            noktalar = (
                (110, "İnsan", MAVI),
                (240, "Hücre", YESIL),
                (360, "Atom", TURUNCU),
                (490, "Planck*", MOR),
            )
            for x, label, renk in noktalar:
                c.create_line(x, 86, x, 114, fill=renk, width=4)
                c.create_text(x, 130, text=label, fill=renk, font=("Segoe UI", 9, "bold"))
            c.create_text(300, 160, text="*Planck uzunluğu önemli kuramsal ölçektir; altını ölçtüğümüz anlamına gelmez.", fill=SOLUK)
        elif tur == "graph":
            c.create_text(300, 30, text="Örnek sayısı arttıkça ortalama dengelenir", fill=BEYAZ)
            c.create_line(145, 145, 470, 145, fill=SOLUK)
            c.create_line(145, 55, 145, 145, fill=SOLUK)
            points = ((155, 110), (200, 80), (245, 120), (290, 75), (335, 95), (380, 70), (425, 88), (465, 82))
            c.create_line(*[coord for point in points for coord in point], fill=TURUNCU, width=3)
            for x, y in points:
                c.create_oval(x - 4, y - 4, x + 4, y + 4, fill=MAVI, outline="")
        elif tur == "flow":
            c.create_text(300, 30, text="Bilimsel çalışma akışı", fill=BEYAZ)
            kutular = (
                (55, "Soru", MAVI),
                (190, "Hipotez", MOR),
                (325, "Test", TURUNCU),
                (460, "Sonuç", YESIL),
            )
            for x, label, renk in kutular:
                c.create_rectangle(x, 75, x + 85, 125, outline=renk, width=3)
                c.create_text(
                    x + 42, 100, text=label, fill=renk,
                    font=("Segoe UI", 10, "bold")
                )
            for x in (145, 280, 415):
                c.create_line(x, 100, x + 38, 100, fill=SOLUK, width=2, arrow=tk.LAST)
        else:
            c.create_text(300, 95, text="Bir bölüm seçerek görseli aç", fill=SOLUK)

    def deneyleri_hazirla(self):
        govde = ttk.Frame(self.deneyler_sekmesi, padding=22)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Deneyler ve gözlemler",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            govde,
            text="Bir başlık seç; düzeneği, gözlenen sonucu ve yorum sınırlarını oku.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(34, 14))

        deneyler = [
            (
                "Çift yarık",
                "Soru: Işık ve elektronlar hangi koşullarda girişim deseni oluşturur?",
                "Parçacıklar tek tek iki yarıklı bir düzeneğe gönderilir; ekrandaki "
                "konumları birikir. Hangi-yol bilgisini fiziksel olarak ölçen "
                "düzenek eklendiğinde girişim örüntüsü değişebilir.",
                "Tek tek noktaların zamanla girişim saçakları oluşturması, "
                "kuantum olasılıklarının dalga benzeri girişimle ilişkisini gösterir.",
                "Bu sonuç insan bilincinin parçacığı değiştirdiğini göstermez. "
                "Düzenek, kaynak ve dedektör koşulları önemlidir.",
            ),
            (
                "Stern–Gerlach",
                "Soru: Açısal momentum ölçümünde neden ayrık sonuçlar görülür?",
                "Gümüş atomlarından oluşan demet, uzayda değişen manyetik alan "
                "bölgesinden geçirilir ve ekrandaki konumları kaydedilir.",
                "1922 deneyinde demetin sürekli bir dağılım yerine ayrılmış izler "
                "vermesi, açısal momentumun kuantumlanmasına kanıt sağladı.",
                "Gerçek düzenek atom demeti ve dikkatli alan/kolimasyon kontrolü "
                "gerektirir; bu programda deneysel ölçüm yapılmaz.",
            ),
            (
                "Bell eşitsizliği deneyleri",
                "Soru: Yerel gizli değişken modelleri bütün kuantum korelasyonlarını "
                "açıklayabilir mi?",
                "Dolanık parçacık çiftleri hazırlanır; iki tarafta farklı ölçüm "
                "ayarları seçilir ve çok sayıda eşleşmiş sonuç karşılaştırılır.",
                "Bazı korelasyonlar Bell eşitsizliği sınırını aşar. Clauser, "
                "Aspect ve Zeilinger’in çalışmaları 2022 Nobel Fizik Ödülü’yle "
                "tanındı.",
                "Tek bir çift veya bu uygulamadaki ideal simülasyon, kapanmış "
                "açıklara sahip gerçek bir Bell testi değildir; mesajlaşma "
                "olduğu anlamına da gelmez.",
            ),
            (
                "Kara delik gölgesi — EHT",
                "Soru: Olay ufku yakınındaki ışınımın açısal yapısı nasıl ölçülür?",
                "Dünya çapındaki radyo teleskopları eş zamanlı gözlem yapıp "
                "çok uzun taban çizgili girişimölçümüyle sanal bir teleskop "
                "açıklığı oluşturur.",
                "M87* ve Samanyolu merkezindeki Sgr A* çevresinde parlak halka "
                "ve karanlık gölge ölçeği yeniden oluşturulmuş görüntülerde "
                "incelendi.",
                "Görüntü olay ufkunun fotoğrafı değildir. Kalibrasyon, veri "
                "işleme, plazma ve kütle/uzaklık belirsizlikleri yorumda önemlidir.",
            ),
            (
                "LIGO ve kütleçekim dalgaları",
                "Soru: Birleşen kara deliklerin uzay-zamanda oluşturduğu sinyal "
                "nasıl ölçülür?",
                "Lazer interferometresinin iki dik kolundaki çok küçük göreli "
                "uzunluk değişimleri izlenir; sinyal gürültüden ayrılıp dalga "
                "biçimiyle karşılaştırılır.",
                "2015’te LIGO ilk doğrudan kütleçekim dalgası algılamasını "
                "duyurdu. Bu gözlemler birleşen kompakt cisimlerin kütleleri "
                "ve hareketleri hakkında bilgi verir.",
                "Dalga biçiminden çıkarım kuramsal şablonlara ve kalibrasyona "
                "dayanır; bu uygulama gerçek LIGO verisini analiz etmiyor.",
            ),
            (
                "Yıldız yörüngeleri — galaktik merkez",
                "Soru: Görünmeyen bir merkezî kütlenin varlığı nasıl sınanır?",
                "Galaksi merkezine yakın yıldızların konumları uzun yıllar "
                "boyunca ölçülür ve yörüngeleri hesaplanır.",
                "Samanyolu merkezindeki yıldız yörüngeleri çok büyük, kompakt "
                "bir kütlenin varlığına güçlü kanıt verdi; bu çalışmalar "
                "2020 Nobel Fizik Ödülü’nde tanındı.",
                "Yörüngeden kütle çıkarımı gözlem süresi, mesafe, astrometri "
                "ve alternatif kütle dağılımlarının sınanmasını gerektirir.",
            ),
        ]
        self.deney_verileri = deneyler
        self.deney_listesi = ttk.Treeview(
            govde, show="tree", height=18, selectmode="browse"
        )
        self.deney_listesi.column("#0", width=265, stretch=False)
        self.deney_listesi.grid(row=1, column=0, sticky="nsw", padx=(0, 18))
        detay = ttk.Frame(govde, style="Card.TFrame", padding=20)
        detay.grid(row=1, column=1, sticky="nsew")
        detay.columnconfigure(0, weight=1)
        detay.rowconfigure(2, weight=1)
        self.deney_baslik = ttk.Label(
            detay, style="Card.TLabel", font=("Segoe UI", 17, "bold")
        )
        self.deney_baslik.grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.deney_gorseli = tk.Canvas(
            detay, height=165, bg="#060d1c",
            highlightthickness=1, highlightbackground="#243449",
        )
        self.deney_gorseli.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.deney_gorseli.bind("<Configure>", self.deney_gorsel_yenile)
        self.deney_metni = tk.Text(
            detay, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=PANEL, fg=BEYAZ, padx=22, pady=20, relief=tk.FLAT,
        )
        self.deney_metni.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=10,
            lmargin1=5, rmargin=5,
        )
        self.deney_metni.grid(row=2, column=0, sticky="nsew")
        for sira, deney in enumerate(deneyler):
            self.deney_listesi.insert("", tk.END, iid=str(sira), text=deney[0])
        self.deney_listesi.bind("<<TreeviewSelect>>", self.deney_secildi)
        self.deney_listesi.selection_set("0")
        self.deney_goster(0)

    def deney_secildi(self, _olay):
        secim = self.deney_listesi.selection()
        if secim:
            self.deney_goster(int(secim[0]))

    def deney_goster(self, sira):
        baslik, soru, duzenek, gozlem, sinir = self.deney_verileri[sira]
        self.deney_baslik.config(text=baslik)
        icerik = (
            f"{soru}\n\nDüzenek\n{duzenek}\n\nGözlem / bulgu\n{gozlem}"
            f"\n\nYorum sınırı\n{sinir}"
        )
        self.deney_metni.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.deney_metni, icerik, tek_bolum="DENEYİN ÖZETİ"
        )
        self.deney_metni.config(state=tk.DISABLED)
        self.deney_gorsel_ciz(sira)

    def deney_gorsel_yenile(self, _olay=None):
        if hasattr(self, "deney_listesi"):
            secim = self.deney_listesi.selection()
            if secim:
                self.deney_gorsel_ciz(int(secim[0]))

    def deney_gorsel_ciz(self, sira):
        c = self.deney_gorseli
        c.delete("all")
        width = max(c.winfo_width(), 520)
        height = max(c.winfo_height(), 150)
        middle = height * 0.53
        rnd = random.Random(190 + sira)
        for _ in range(24):
            x = rnd.randrange(width)
            y = rnd.randrange(height)
            c.create_oval(
                x, y, x + 1.5, y + 1.5,
                fill=rnd.choice(("#233047", "#334155", "#475569")),
                outline="",
            )
        c.create_text(
            width - 12, 12, text="ŞEMATİK GÖRSEL · ölçekli değildir",
            fill=SOLUK, anchor="ne", font=("Segoe UI", 8, "bold"),
        )

        if sira == 0:
            source_x, barrier_x, screen_x = 55, width * 0.47, width * 0.84
            c.create_oval(
                source_x - 8, middle - 8, source_x + 8, middle + 8,
                fill=TURUNCU, outline="",
            )
            for y1, y2 in (
                (18, middle - 42), (middle - 29, middle - 14),
                (middle + 14, middle + 29), (middle + 42, height - 12),
            ):
                c.create_line(barrier_x, y1, barrier_x, y2, fill=SOLUK, width=3)
            c.create_line(screen_x, 24, screen_x, height - 18, fill=MAVI, width=2)
            for slit_y in (middle - 22, middle + 22):
                c.create_line(
                    source_x + 8, middle, barrier_x, slit_y,
                    fill="#7dd3fc", dash=(4, 3),
                )
                c.create_line(
                    barrier_x, slit_y, screen_x, middle,
                    fill="#7dd3fc", dash=(4, 3),
                )
            for index in range(-5, 6):
                y = middle + index * 10
                color = TURUNCU if index % 2 == 0 else "#7c2d12"
                c.create_oval(
                    screen_x - 4, y - 3, screen_x + 4, y + 3,
                    fill=color, outline="",
                )
            c.create_text(source_x, height - 12, text="kaynak", fill=SOLUK)
            c.create_text(barrier_x, height - 12, text="iki yarık", fill=SOLUK)
            c.create_text(screen_x, height - 12, text="ekran", fill=SOLUK)
        elif sira == 1:
            c.create_text(55, middle, text="Ag", fill=BEYAZ, font=("Segoe UI", 10, "bold"))
            c.create_line(78, middle, width * 0.37, middle, fill=MAVI, width=3, arrow=tk.LAST)
            c.create_polygon(
                width * 0.39, middle - 28, width * 0.53, middle - 10,
                width * 0.39, middle - 4, fill="#7f1d1d", outline=PEMBE,
            )
            c.create_polygon(
                width * 0.39, middle + 28, width * 0.53, middle + 10,
                width * 0.39, middle + 4, fill="#1e3a8a", outline=MAVI,
            )
            c.create_text(width * 0.44, middle - 15, text="N", fill=BEYAZ)
            c.create_text(width * 0.44, middle + 15, text="S", fill=BEYAZ)
            c.create_line(
                width * 0.54, middle, width * 0.83, middle - 40,
                fill=TURUNCU, width=2, arrow=tk.LAST,
            )
            c.create_line(
                width * 0.54, middle, width * 0.83, middle + 40,
                fill=MAVI, width=2, arrow=tk.LAST,
            )
            c.create_line(width * 0.86, 20, width * 0.86, height - 18, fill=SOLUK)
            c.create_oval(width * 0.86 - 4, middle - 44, width * 0.86 + 4, middle - 36, fill=TURUNCU, outline="")
            c.create_oval(width * 0.86 - 4, middle + 36, width * 0.86 + 4, middle + 44, fill=MAVI, outline="")
            c.create_text(width * 0.68, height - 12, text="manyetik alan gradyanı", fill=SOLUK)
        elif sira == 2:
            source_x, source_y = width * 0.5, middle
            left_x, right_x = width * 0.15, width * 0.85
            c.create_oval(
                source_x - 9, source_y - 9, source_x + 9, source_y + 9,
                fill=MOR, outline="",
            )
            c.create_line(source_x - 9, source_y, left_x + 20, middle - 32, fill=MAVI, width=2, arrow=tk.LAST)
            c.create_line(source_x - 9, source_y, left_x + 20, middle + 32, fill=MAVI, width=2, arrow=tk.LAST)
            c.create_line(source_x + 9, source_y, right_x - 20, middle - 32, fill=TURUNCU, width=2, arrow=tk.LAST)
            c.create_line(source_x + 9, source_y, right_x - 20, middle + 32, fill=TURUNCU, width=2, arrow=tk.LAST)
            for x, label, color in (
                (left_x, "A: ölçüm", MAVI), (right_x, "B: ölçüm", TURUNCU)
            ):
                c.create_rectangle(x - 42, middle - 42, x + 42, middle + 42, outline=color, width=2)
                c.create_text(x, middle, text=label, fill=color, font=("Segoe UI", 9, "bold"))
            c.create_text(source_x, height - 12, text="dolaşık çift kaynağı", fill=SOLUK)
        elif sira == 3:
            earth_x, earth_y = width * 0.22, middle
            c.create_oval(
                earth_x - 52, earth_y - 44, earth_x + 52, earth_y + 44,
                outline="#2563eb", width=2,
            )
            for dx, dy in ((-32, -25), (22, -33), (40, 14), (-16, 35)):
                tx, ty = earth_x + dx, earth_y + dy
                c.create_line(tx, ty, width * 0.55, middle, fill="#334155", dash=(3, 3))
                c.create_oval(tx - 4, ty - 4, tx + 4, ty + 4, fill=MAVI, outline="")
            image_x = width * 0.76
            c.create_oval(
                image_x - 50, middle - 45, image_x + 50, middle + 45,
                fill="#030712", outline="#f59e0b", width=8,
            )
            c.create_oval(
                image_x - 22, middle - 22, image_x + 22, middle + 22,
                fill="#030712", outline="#111827", width=3,
            )
            c.create_text(earth_x, height - 12, text="teleskop ağı", fill=SOLUK)
            c.create_text(image_x, height - 12, text="yeniden oluşturulan halka", fill=SOLUK)
        elif sira == 4:
            center_x = width * 0.48
            c.create_line(55, middle, width - 55, middle, fill=MAVI, width=2)
            c.create_line(center_x, 24, center_x, height - 22, fill=MOR, width=2)
            c.create_rectangle(center_x - 7, middle - 7, center_x + 7, middle + 7, fill=BEYAZ, outline="")
            for x, y in (
                (width - 50, middle), (center_x, 22),
                (width - 50, height - 20), (55, middle),
            ):
                c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=TURUNCU, outline="")
            wave = []
            for index in range(121):
                x = 70 + (width - 140) * index / 120
                y = height - 30 - 12 * math.sin(index * 0.25) * math.exp(-((index - 82) / 22) ** 2)
                wave.extend((x, y))
            c.create_line(*wave, fill=PEMBE, width=2)
            c.create_text(width * 0.5, height - 8, text="şematik sinyal", fill=SOLUK)
        else:
            center_x, center_y = width * 0.52, middle
            c.create_oval(
                center_x - 125, center_y - 42,
                center_x + 125, center_y + 42,
                outline="#38bdf8", width=2, dash=(5, 3),
            )
            c.create_oval(
                center_x - 10, center_y - 10,
                center_x + 10, center_y + 10,
                fill="#f97316", outline="",
            )
            c.create_oval(
                center_x + 65, center_y - 27,
                center_x + 73, center_y - 19,
                fill=BEYAZ, outline="",
            )
            c.create_line(
                center_x + 69, center_y - 23,
                center_x + 125, center_y - 38,
                fill=SOLUK, dash=(3, 2),
            )
            c.create_text(center_x, height - 12, text="merkezî kütle ve yıldız yörüngesi", fill=SOLUK)

    def cift_yarik_lab_hazirla(self):
        govde = ttk.Frame(self.cift_yarik_sekmesi, padding=18)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Çift yarık girişim laboratuvarı",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        controls = ttk.Frame(govde, style="Card.TFrame", padding=14)
        controls.grid(row=1, column=0, sticky="nsw", padx=(0, 14), pady=(14, 0))
        ttk.Label(
            controls, text="Düzeneği ayarla", style="Card.TLabel",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))
        self.cift_yarik_dalga_boyu = tk.DoubleVar(value=550)
        self.cift_yarik_aralik = tk.DoubleVar(value=0.4)
        self.cift_yarik_uzaklik = tk.DoubleVar(value=2.0)
        self.cift_yarik_yol_bilgisi = tk.BooleanVar(value=False)
        ayarlar = (
            ("Dalga boyu (nm)", self.cift_yarik_dalga_boyu, 380, 700),
            ("Yarık aralığı (mm)", self.cift_yarik_aralik, 0.15, 1.0),
            ("Ekran uzaklığı (m)", self.cift_yarik_uzaklik, 0.5, 5.0),
        )
        for baslik, degisken, baslangic, bitis in ayarlar:
            ttk.Label(
                controls, text=baslik, style="Card.TLabel"
            ).pack(anchor="w", pady=(8, 2))
            ttk.Scale(
                controls, variable=degisken, from_=baslangic, to=bitis,
                command=self.cift_yarik_ciz,
            ).pack(fill=tk.X, pady=(0, 4))
        ttk.Checkbutton(
            controls, text="Hangi-yol bilgisi ölçülüyor",
            variable=self.cift_yarik_yol_bilgisi,
            command=self.cift_yarik_ciz,
        ).pack(anchor="w", pady=(12, 6))
        ttk.Label(
            controls,
            text=(
                "İdeal, eş fazlı iki yarığın şematik modeli. Çizim "
                "tek tek fotonları veya gerçek bir deney düzeneğini "
                "simüle etmez."
            ),
            style="Muted.TLabel", wraplength=220, justify=tk.LEFT,
        ).pack(anchor="w", pady=(8, 0))
        self.cift_yarik_kanvasi = tk.Canvas(
            govde, height=440, bg="#030712",
            highlightthickness=1, highlightbackground="#243449",
        )
        self.cift_yarik_kanvasi.grid(
            row=1, column=1, sticky="nsew", pady=(14, 0)
        )
        self.cift_yarik_kanvasi.bind(
            "<Configure>", self.cift_yarik_ciz
        )
        self.cift_yarik_ciz()

    def cift_yarik_ciz(self, _olay=None):
        if not hasattr(self, "cift_yarik_kanvasi"):
            return
        c = self.cift_yarik_kanvasi
        c.delete("all")
        width = max(c.winfo_width(), 520)
        height = max(c.winfo_height(), 360)
        left, right, top, bottom = 65, width - 25, 45, height - 55
        chart_h = bottom - top
        c.create_text(
            left, 16, text="Ekrandaki göreli yoğunluk",
            fill=BEYAZ, anchor="w", font=("Segoe UI", 11, "bold"),
        )
        for fraction in (0, 0.25, 0.5, 0.75, 1):
            y = bottom - fraction * chart_h
            c.create_line(left, y, right, y, fill="#233047")
            c.create_text(
                left - 10, y, text=f"{fraction:.2g}",
                fill=SOLUK, anchor="e", font=("Segoe UI", 9),
            )
        c.create_line(left, top, left, bottom, fill=SOLUK)
        c.create_line(left, bottom, right, bottom, fill=SOLUK)
        for index in range(5):
            x_mm = -10 + 20 * index / 4
            x = left + (right - left) * index / 4
            c.create_line(x, bottom, x, bottom + 5, fill=SOLUK)
            c.create_text(
                x, bottom + 20, text=f"{x_mm:.0f}",
                fill=SOLUK, font=("Segoe UI", 9),
            )
        c.create_text(
            (left + right) / 2, height - 12,
            text="Ekrandaki konum (mm)", fill=SOLUK,
            font=("Segoe UI", 9),
        )
        wavelength = self.cift_yarik_dalga_boyu.get() * 1e-9
        separation = self.cift_yarik_aralik.get() * 1e-3
        slit_width = 0.05e-3
        screen_distance = self.cift_yarik_uzaklik.get()
        path_known = self.cift_yarik_yol_bilgisi.get()
        points = []
        samples = 240
        for index in range(samples + 1):
            x_mm = -10 + 20 * index / samples
            angle = math.atan((x_mm * 1e-3) / screen_distance)
            alpha = math.pi * slit_width * math.sin(angle) / wavelength
            beta = math.pi * separation * math.sin(angle) / wavelength
            envelope = 1.0 if abs(alpha) < 1e-12 else (
                math.sin(alpha) / alpha
            ) ** 2
            intensity = envelope if path_known else (
                envelope * math.cos(beta) ** 2
            )
            x = left + (right - left) * index / samples
            y = bottom - max(0.0, min(1.0, intensity)) * chart_h
            points.extend((x, y))
        color = TURUNCU if path_known else MAVI
        c.create_line(*points, fill=color, width=2, smooth=True)
        c.create_text(
            right - 4, top + 8,
            text=(
                "Yol bilgisi açık: girişim terimi yok"
                if path_known else "Yol bilgisi yok: girişim saçakları"
            ),
            fill=color, anchor="ne", font=("Segoe UI", 10, "bold"),
        )

    def spin_lab_hazirla(self):
        govde = ttk.Frame(self.spin_lab_sekmesi, padding=18)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Spin ölçümü ve Born kuralı",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        controls = ttk.Frame(govde, style="Card.TFrame", padding=14)
        controls.grid(row=1, column=0, sticky="nsw", padx=(0, 14), pady=(14, 0))
        ttk.Label(
            controls, text="Hazırlık ve ölçüm", style="Card.TLabel",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))
        self.spin_hazirlama_acisi = tk.DoubleVar(value=0)
        self.spin_olcum_acisi = tk.DoubleVar(value=60)
        self.spin_ornek_sayisi = tk.StringVar(value="1000")
        self.spin_lab_olcum_sayisi = 0
        self.spin_lab_artilar = 0
        for baslik, degisken in (
            ("Hazırlama ekseni (°)", self.spin_hazirlama_acisi),
            ("Ölçüm ekseni (°)", self.spin_olcum_acisi),
        ):
            ttk.Label(
                controls, text=baslik, style="Card.TLabel"
            ).pack(anchor="w", pady=(8, 2))
            ttk.Scale(
                controls, variable=degisken, from_=0, to=180,
                command=self.spin_lab_parametre_degisti,
            ).pack(fill=tk.X, pady=(0, 4))
        ttk.Label(
            controls, text="Örnek ölçüm sayısı", style="Card.TLabel"
        ).pack(anchor="w", pady=(10, 2))
        ttk.Combobox(
            controls, textvariable=self.spin_ornek_sayisi,
            values=("100", "500", "1000", "5000"),
            state="readonly", width=16,
        ).pack(anchor="w")
        ttk.Button(
            controls, text="Örnekleri ölç",
            style="Accent.TButton", command=self.spin_lab_olc,
        ).pack(fill=tk.X, pady=(12, 5))
        ttk.Button(
            controls, text="Örneklemi sıfırla",
            command=self.spin_lab_sifirla,
        ).pack(fill=tk.X)
        ttk.Label(
            controls,
            text=(
                "Hazırlanan durum + spin özdurumudur. İdeal olasılık "
                "P(+) = cos²(Δθ/2); örnek sonuçları rastlantısal "
                "dalgalanma gösterir."
            ),
            style="Muted.TLabel", wraplength=220, justify=tk.LEFT,
        ).pack(anchor="w", pady=(14, 0))
        self.spin_lab_sonuc = ttk.Label(
            controls, style="Card.TLabel", justify=tk.LEFT,
            wraplength=230, foreground="#a5f3fc",
        )
        self.spin_lab_sonuc.pack(anchor="w", pady=(12, 0))
        self.spin_lab_kanvasi = tk.Canvas(
            govde, height=440, bg="#030712",
            highlightthickness=1, highlightbackground="#243449",
        )
        self.spin_lab_kanvasi.grid(
            row=1, column=1, sticky="nsew", pady=(14, 0)
        )
        self.spin_lab_kanvasi.bind("<Configure>", self.spin_lab_ciz)
        self.spin_lab_parametre_degisti()

    def spin_lab_olasilik(self):
        fark = math.radians(
            self.spin_hazirlama_acisi.get() - self.spin_olcum_acisi.get()
        )
        return math.cos(fark / 2) ** 2

    def spin_lab_parametre_degisti(self, _deger=None):
        self.spin_lab_olcum_sayisi = 0
        self.spin_lab_artilar = 0
        self.spin_lab_sonuc_guncelle()
        self.spin_lab_ciz()

    def spin_lab_olc(self):
        adet = int(self.spin_ornek_sayisi.get())
        olasilik = self.spin_lab_olasilik()
        self.spin_lab_artilar = sum(
            random.random() < olasilik for _ in range(adet)
        )
        self.spin_lab_olcum_sayisi = adet
        self.spin_lab_sonuc_guncelle()
        self.spin_lab_ciz()

    def spin_lab_sifirla(self):
        self.spin_lab_olcum_sayisi = 0
        self.spin_lab_artilar = 0
        self.spin_lab_sonuc_guncelle()
        self.spin_lab_ciz()

    def spin_lab_sonuc_guncelle(self):
        olasilik = self.spin_lab_olasilik()
        if self.spin_lab_olcum_sayisi:
            oran = self.spin_lab_artilar / self.spin_lab_olcum_sayisi
            hata = math.sqrt(
                olasilik * (1 - olasilik) / self.spin_lab_olcum_sayisi
            )
            metin = (
                f"Kuramsal P(+): {olasilik:.3f}\n"
                f"Örnek P(+): {oran:.3f} "
                f"({self.spin_lab_artilar}/{self.spin_lab_olcum_sayisi})\n"
                f"Beklenen 1σ örnekleme ölçeği: {hata:.3f}"
            )
        else:
            metin = f"Kuramsal P(+): {olasilik:.3f}\nHenüz örnek alınmadı."
        self.spin_lab_sonuc.config(text=metin)

    def spin_lab_ciz(self, _olay=None):
        if not hasattr(self, "spin_lab_kanvasi"):
            return
        c = self.spin_lab_kanvasi
        c.delete("all")
        width = max(c.winfo_width(), 520)
        height = max(c.winfo_height(), 360)
        left, right, top, bottom = 70, width - 24, 50, height - 65
        plot_h = bottom - top
        p_plus = self.spin_lab_olasilik()
        p_minus = 1 - p_plus
        if self.spin_lab_olcum_sayisi:
            p_plus_sample = self.spin_lab_artilar / self.spin_lab_olcum_sayisi
            p_minus_sample = 1 - p_plus_sample
        else:
            p_plus_sample = None
            p_minus_sample = None
        c.create_text(
            left, 20, text="Sonuç olasılığı / gözlenen oran",
            fill=BEYAZ, anchor="w", font=("Segoe UI", 11, "bold"),
        )
        for fraction in (0, 0.25, 0.5, 0.75, 1):
            y = bottom - fraction * plot_h
            c.create_line(left, y, right, y, fill="#233047")
            c.create_text(
                left - 10, y, text=f"{fraction:.2g}",
                fill=SOLUK, anchor="e", font=("Segoe UI", 9),
            )
        c.create_line(left, top, left, bottom, fill=SOLUK)
        c.create_line(left, bottom, right, bottom, fill=SOLUK)
        count = 4
        group_width = (right - left) / count
        values = (
            ("+ kuramsal", p_plus, MAVI),
            ("+ örnek", p_plus_sample, TURUNCU),
            ("− kuramsal", p_minus, MAVI),
            ("− örnek", p_minus_sample, TURUNCU),
        )
        for index, (label, value, color) in enumerate(values):
            center = left + group_width * (index + 0.5)
            if value is not None:
                bar_h = value * plot_h
                c.create_rectangle(
                    center - 30, bottom - bar_h,
                    center + 30, bottom, fill=color, outline="",
                )
                c.create_text(
                    center, bottom - bar_h - 12, text=f"{value:.2f}",
                    fill=BEYAZ, font=("Segoe UI", 9, "bold"),
                )
            c.create_text(
                center, bottom + 24, text=label,
                fill=SOLUK, font=("Segoe UI", 9),
            )

    def odulleri_hazirla(self):
        oduller = [
            (
                "2022 — Kuantum dolaşıklığı ve Bell deneyleri",
                "Alain Aspect, John F. Clauser ve Anton Zeilinger; dolaşık foton "
                "deneyleri, Bell eşitsizliklerinin ihlali ve kuantum bilgi "
                "biliminin önünü açan çalışmaları nedeniyle ödüllendirildi.",
                "https://www.nobelprize.org/prizes/physics/2022/summary/",
            ),
            (
                "2020 — Kara delikler",
                "Roger Penrose, kara delik oluşumunun genel göreliliğin sağlam "
                "bir öngörüsü olduğunu gösteren çalışmasıyla; Reinhard Genzel "
                "ve Andrea Ghez, Samanyolu merkezindeki süper kütleli kompakt "
                "cismi keşifleriyle ödül aldı.",
                "https://www.nobelprize.org/prizes/physics/2020/summary/",
            ),
            (
                "2019 — Kozmoloji ve ötegezegen",
                "James Peebles, fiziksel kozmolojiye katkılarıyla; Michel Mayor "
                "ve Didier Queloz, Güneş benzeri bir yıldız çevresindeki ilk "
                "ötegezegen keşfiyle ödüllendirildi.",
                "https://www.nobelprize.org/prizes/physics/2019/summary/",
            ),
            (
                "2017 — Kütleçekim dalgaları",
                "Rainer Weiss, Barry C. Barish ve Kip S. Thorne, LIGO "
                "dedektörüne ve kütleçekim dalgalarının gözlenmesine belirleyici "
                "katkıları nedeniyle ödüllendirildi.",
                "https://www.nobelprize.org/prizes/physics/2017/summary/",
            ),
            (
                "2011 — Evrenin hızlanan genişlemesi",
                "Saul Perlmutter, Brian P. Schmidt ve Adam G. Riess, uzak "
                "süpernovaların gözlemleriyle evrenin genişlemesinin hızlandığını "
                "keşfetmeleri nedeniyle ödüllendirildi.",
                "https://www.nobelprize.org/prizes/physics/2011/summary/",
            ),
        ]
        self.odul_verileri = oduller
        govde = ttk.Frame(self.oduller_sekmesi, padding=22)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Nobel Fizik Ödülleri ve büyük keşifler",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            govde,
            text="Ödül, belirli bilimsel katkıları tanır; tek başına yeni bir iddianın kanıtı değildir.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(34, 14))
        self.odul_listesi = ttk.Treeview(
            govde, show="tree", height=12, selectmode="browse"
        )
        self.odul_listesi.column("#0", width=330, stretch=False)
        self.odul_listesi.grid(row=1, column=0, sticky="nsw", padx=(0, 18))
        panel = ttk.Frame(govde, style="Card.TFrame", padding=22)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.odul_baslik = ttk.Label(
            panel, style="Card.TLabel", font=("Segoe UI", 16, "bold")
        )
        self.odul_baslik.grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.odul_aciklama = tk.Text(
            panel, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=PANEL, fg=BEYAZ, padx=22, pady=20, relief=tk.FLAT,
        )
        self.odul_aciklama.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=10,
            lmargin1=5, rmargin=5,
        )
        self.odul_aciklama.grid(row=1, column=0, sticky="nsew")
        self.odul_kaynak = ttk.Button(
            panel, text="Resmî Nobel kaynağını aç",
            command=self.odul_kaynagini_ac,
        )
        self.odul_kaynak.grid(row=2, column=0, sticky="w", pady=(12, 0))
        for sira, odul in enumerate(oduller):
            self.odul_listesi.insert("", tk.END, iid=str(sira), text=odul[0])
        self.odul_listesi.bind("<<TreeviewSelect>>", self.odul_secildi)
        self.odul_listesi.selection_set("0")
        self.odul_goster(0)

    def odul_secildi(self, _olay):
        secim = self.odul_listesi.selection()
        if secim:
            self.odul_goster(int(secim[0]))

    def odul_goster(self, sira):
        baslik, aciklama, self.secili_odul_url = self.odul_verileri[sira]
        self.odul_baslik.config(text=baslik)
        self.odul_aciklama.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.odul_aciklama, aciklama, tek_bolum="ÖDÜLÜN KATKISI"
        )
        self.odul_aciklama.config(state=tk.DISABLED)

    def odul_kaynagini_ac(self):
        webbrowser.open(self.secili_odul_url)

    def kaynaklari_hazirla(self):
        kaynaklar = [
            (
                "NASA — Kara delikler",
                "NASA'nın kara deliklerin oluşumu, gözlenmesi ve temel özellikleri hakkındaki tanıtımı.",
                "https://science.nasa.gov/universe/black-holes/",
            ),
            (
                "Event Horizon Telescope",
                "EHT işbirliğinin teleskop ağı, gözlemleri ve kara delik görüntüleri hakkında birincil kaynak.",
                "https://eventhorizontelescope.org/",
            ),
            (
                "LIGO — Kütleçekim dalgaları",
                "LIGO Caltech'in kütleçekim dalgaları ve interferometre gözlemleri için açıklamaları.",
                "https://www.ligo.caltech.edu/page/what-are-gw",
            ),
            (
                "Nobel Prize — Fizik ödülleri",
                "Nobel Fizik Ödülleri'nin yıllara göre resmî açıklamaları ve ödül gerekçeleri.",
                "https://www.nobelprize.org/prizes/lists/all-nobel-prizes-in-physics/",
            ),
            (
                "NIST — CODATA temel sabitleri",
                "Fizikte kullanılan temel sabitlerin güncel ve izlenebilir değerleri.",
                "https://physics.nist.gov/cuu/Constants/",
            ),
            (
                "National Academies — Bilim eğitimi",
                "Bilimsel kanıtı değerlendirme, araştırma ve fen eğitimi için kaynaklar.",
                "https://www.nationalacademies.org/",
            ),
        ]
        govde = ttk.Frame(self.kaynaklar_sekmesi, padding=22)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(1, weight=1)
        ttk.Label(
            govde, text="Kaynak kütüphanesi",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            govde,
            text="Önce birincil ve kurumsal kaynaklara bak; popüler anlatımı özgün kaynağıyla karşılaştır.",
            style="Muted.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(34, 14))
        self.kaynak_listesi = ttk.Treeview(
            govde, show="tree", height=12, selectmode="browse"
        )
        self.kaynak_listesi.column("#0", width=310, stretch=False)
        self.kaynak_listesi.grid(row=1, column=0, sticky="nsw", padx=(0, 18))
        panel = ttk.Frame(govde, style="Card.TFrame", padding=22)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.kaynak_baslik = ttk.Label(
            panel, style="Card.TLabel", font=("Segoe UI", 16, "bold")
        )
        self.kaynak_baslik.grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.kaynak_aciklama = tk.Text(
            panel, wrap=tk.WORD, font=("Segoe UI", 12),
            bg=PANEL, fg=BEYAZ, padx=22, pady=20, relief=tk.FLAT,
        )
        self.kaynak_aciklama.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=10,
            lmargin1=5, rmargin=5,
        )
        self.kaynak_aciklama.grid(row=1, column=0, sticky="nsew")
        ttk.Button(
            panel, text="Kaynağı tarayıcıda aç",
            command=self.kaynagi_ac,
        ).grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.kaynak_verileri = kaynaklar
        for sira, kaynak in enumerate(kaynaklar):
            self.kaynak_listesi.insert("", tk.END, iid=str(sira), text=kaynak[0])
        self.kaynak_listesi.bind(
            "<<TreeviewSelect>>", self.kaynak_secildi
        )
        self.kaynak_listesi.selection_set("0")
        self.kaynak_goster(0)

    def kaynak_secildi(self, _olay):
        secim = self.kaynak_listesi.selection()
        if secim:
            self.kaynak_goster(int(secim[0]))

    def kaynak_goster(self, sira):
        baslik, aciklama, self.secili_kaynak_url = self.kaynak_verileri[sira]
        self.kaynak_baslik.config(text=baslik)
        self.kaynak_aciklama.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.kaynak_aciklama, aciklama, tek_bolum="KAYNAK HAKKINDA"
        )
        self.kaynak_aciklama.config(state=tk.DISABLED)

    def kaynagi_ac(self):
        webbrowser.open(self.secili_kaynak_url)

    def terimleri_hazirla(self):
        self.terimler_ic_sekmeler = ttk.Notebook(self.terimler_sekmesi)
        self.terimler_ic_sekmeler.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.terim_sozlugu_sekmesi = ttk.Frame(self.terimler_ic_sekmeler)
        self.anlatim_sekmesi = ttk.Frame(self.terimler_ic_sekmeler)
        self.terimler_ic_sekmeler.add(
            self.terim_sozlugu_sekmesi, text="Terim sözlüğü"
        )
        self.terimler_ic_sekmeler.add(
            self.anlatim_sekmesi, text="5 dk anlatım"
        )

        govde = ttk.Frame(self.terim_sozlugu_sekmesi, padding=20)
        govde.pack(fill=tk.BOTH, expand=True)
        govde.columnconfigure(1, weight=1)
        govde.rowconfigure(0, weight=1)

        terimler = [
            (
                "Kuantum dolanıklık (ortak durum)",
                "İki parçacığın kuantum durumu ayrı ayrı değil, birlikte tanımlanır. "
                "Ölçümler arasında klasik sezgiyi aşan korelasyonlar görülebilir.",
            ),
            (
                "Spin (içsel açısal momentum)",
                "Parçacığın kuantum özelliğidir. Küçük bir topun gerçekten dönmesi "
                "gibi düşünülmemelidir.",
            ),
            (
                "Singlet durumu (toplam spin sıfır olan çift)",
                "Bu örnekteki iki spin-1/2 parçacığın ortak kuantum durumudur. "
                "Aynı eksende ölçülürlerse sonuçları zıt olur.",
            ),
            (
                "Ölçüm ekseni (sonucun ölçüldüğü yön)",
                "Açı düğmeleri A ve B taraflarındaki ölçüm eksenini değiştirir. "
                "Eksenler arasındaki açı korelasyon modelini etkiler.",
            ),
            (
                "Korelasyon (sonuçlar arasındaki istatistiksel ilişki)",
                "Tek bir ölçüm çiftinden değil, çok sayıda tekrardan anlaşılır. "
                "Simülasyon ölçülen değeri kuramsal beklentiyle karşılaştırır.",
            ),
            (
                "Rastgele sonuç (önceden kestirilemeyen tek ölçüm)",
                "Dolanıklık olsa bile A veya B tarafındaki tekil sonuçlar "
                "kontrol edilebilir bir mesaj oluşturmaz.",
            ),
            (
                "Marjinal dağılım (tek tarafın sonuç oranları)",
                "A ya da B sonuçlarına ayrı ayrı bakıldığında görülen oranlardır. "
                "Uzak tarafın ayarını değiştirerek bu oranlarla mesaj kodlanamaz.",
            ),
            (
                "Işıktan hızlı iletişim (bu modelde mümkün değil)",
                "Korelasyonlar, kayıtlar daha sonra normal iletişimle "
                "karşılaştırıldığında görülür. Dolaşıklık tek başına mesaj taşımaz.",
            ),
            (
                "Kuramsal korelasyon (E = -cos Δ)",
                "İdeal spin-1/2 singlet modeli için sonuçların çarpımının "
                "beklenen değeridir. Δ, iki ölçüm ekseni arasındaki açıdır.",
            ),
            (
                "Olay ufku (geri dönüş sınırı)",
                "Kara deliğin içinden dışarıya ışığın bile kaçamadığı sınırdır. "
                "Laboratuvardaki yarıçap Kerr çözümünün kuramsal değeridir; "
                "ufkun kendisi doğrudan ışık saçan bir yüzey değildir.",
            ),
            (
                "Kerr kara deliği (dönen kara delik modeli)",
                "Dönen, yüksüz bir kara deliğin ideal çözümüdür. Kütle ve spin "
                "ufuk geometrisini belirler; gerçek gök cisimlerinin çevresinde "
                "madde ve manyetik alanlar da bulunabilir.",
            ),
            (
                "Spin parametresi (a*, dönme ölçüsü)",
                "Boyutsuz dönme parametresi; bu laboratuvarda 0 ile 1 arasında "
                "ayarlanır. Spin arttıkça Kerr olay ufkunun yarıçapı azalır. "
                "Gözlemsel spin çıkarımı kullanılan modele bağlıdır.",
            ),
            (
                "Schwarzschild yarıçapı (dönmeyen modelin ufku)",
                "Dönmeyen, yüksüz ideal kara delikte olay ufkunun yarıçapıdır: "
                "rₛ = 2GM/c². Dönen kara deliklerde ufuk için Kerr çözümü "
                "kullanılır; bu iki yarıçapı karıştırmamak gerekir.",
            ),
            (
                "Kara delik gölgesi (ışığın bükülmesiyle oluşan karanlık alan)",
                "Gözlenen karanlık bölge, olay ufkunun fotoğrafı değildir. "
                "Yakınından geçen ışığın bükülmesi ve yakalanması gölgeyi "
                "oluşturur; çevresindeki parlak halka da ışınım yapan gazdır.",
            ),
            (
                "Akresyon diski (kara deliğe düşen sıcak madde)",
                "Gaz ve toz içeri doğru dönerken sürtünme ve manyetik süreçlerle "
                "ısınabilir ve ışık yayabilir. Diskin görünümü bakış açısına, "
                "madde akışına ve gözlem dalga boyuna bağlıdır.",
            ),
            (
                "Astrofiziksel jet (dar madde ve enerji akışı)",
                "Bazı kara delik çevrelerinde kutuplardan çıkan güçlü plazma "
                "akışları görülür. Jetin oluşumunda manyetik alanlar ve dönme "
                "rol oynayabilir; her kara delikte belirgin jet bulunmaz.",
            ),
            (
                "Eğim (sisteme baktığımız görüş açısı)",
                "Diskin veya dönme ekseninin görüş doğrultusuna göre açısıdır. "
                "Aynı sistem farklı açılardan farklı görünür; ölçülen ışık ve "
                "tayfın yorumunu etkileyebilir.",
            ),
            (
                "Doppler kayması (hareketin ışık rengini değiştirmesi)",
                "Işık kaynağı yaklaşırken tayf daha maviye, uzaklaşırken daha "
                "kırmızıya kayabilir. Hızlı dönen diskin iki tarafı bu nedenle "
                "farklı parlaklık ve renkte görünebilir.",
            ),
            (
                "Kütleçekimsel merceklenme (ışığın kütleçekimle bükülmesi)",
                "Kütleçekim ışığın izlediği yolu büker. Kara delik çevresindeki "
                "ışık halkaları ve görüntünün şekli bu etkinin izlerini taşır.",
            ),
            (
                "Tayf (ışığın dalga boylarına göre dağılımı)",
                "Bir cismin farklı dalga boylarındaki ışık miktarını gösterir. "
                "Diskin sıcaklığı, kimyasal içeriği ve hareketi hakkında ipuçları "
                "verir; tek başına modele bağlı yorum gerektirir.",
            ),
            (
                "Açısal çözünürlük (ayrıntı seçebilme gücü)",
                "Teleskobun gökyüzündeki birbirine yakın ayrıntıları ayırma "
                "yeteneğidir. Kara delik gölgesini incelemek için çok yüksek "
                "çözünürlük ve farklı istasyonların ortak ölçümleri gerekir.",
            ),
            (
                "EHT (Event Horizon Telescope ağı)",
                "Dünya çapındaki radyo teleskoplarını birlikte kullanarak çok "
                "yüksek açısal çözünürlük elde eden gözlem ağıdır. EHT görüntüleri "
                "ufkun fotoğrafı değil, çevresindeki ışınımın yeniden kurulmuş "
                "görüntüleridir.",
            ),
            (
                "Kütleçekim dalgaları (uzay-zamanın titreşimleri)",
                "Hızlanan büyük kütlelerin oluşturduğu uzay-zaman dalgalarıdır. "
                "Kompakt cisim birleşmelerinden gelen dalga biçimleri, kaynak "
                "kütleleri ve spinleri hakkında bilgi taşıyabilir.",
            ),
            (
                "Olay ufku açısal boyutu (uzaklığa bağlı görünür ölçek)",
                "Bir uzunluğun gökyüzünde kapladığı açıdır. Aynı kütle daha "
                "uzakta daha küçük görünür. Laboratuvarın gölge çapı tahmini "
                "ufuk çapıyla aynı değildir ve gerçek veri çözümlemesi yapmaz.",
            ),
        ]
        self.terim_aciklamalari = terimler

        sol = ttk.Frame(govde)
        sol.grid(row=0, column=0, sticky="nsw", padx=(0, 14))
        kaydirma = ttk.Scrollbar(sol, orient=tk.VERTICAL)
        self.terim_listesi = tk.Listbox(
            sol,
            width=38,
            height=25,
            font=("Segoe UI", 10),
            bg=PANEL,
            fg=BEYAZ,
            selectbackground=MAVI,
            borderwidth=0,
            yscrollcommand=kaydirma.set,
        )
        kaydirma.config(command=self.terim_listesi.yview)
        self.terim_listesi.pack(side=tk.LEFT, fill=tk.Y)
        kaydirma.pack(side=tk.RIGHT, fill=tk.Y)

        sag = ttk.Frame(govde)
        sag.grid(row=0, column=1, sticky="nsew")
        sag.columnconfigure(0, weight=1)
        sag.rowconfigure(1, weight=1)
        self.terim_baslik = ttk.Label(
            sag, text="Bir terim seç", font=("Segoe UI", 16, "bold")
        )
        self.terim_baslik.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.terim_metni = tk.Text(
            sag,
            wrap=tk.WORD,
            font=("Segoe UI", 13),
            bg=PANEL,
            fg=BEYAZ,
            padx=22,
            pady=20,
            relief=tk.FLAT,
            height=15,
        )
        self.terim_metni.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=9,
            lmargin1=4, rmargin=4,
        )
        self.terim_metni.grid(row=1, column=0, sticky="nsew")

        for baslik, _aciklama in terimler:
            self.terim_listesi.insert(tk.END, baslik)
        self.terim_listesi.bind("<<ListboxSelect>>", self.terim_secildi)
        self.terim_listesi.selection_set(0)
        self.terimi_goster(0)

    def terim_secildi(self, _olay):
        secim = self.terim_listesi.curselection()
        if secim:
            self.terimi_goster(secim[0])

    def terimi_goster(self, sira):
        baslik, aciklama = self.terim_aciklamalari[sira]
        self.terim_baslik.config(text=baslik)
        self.terim_metni.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.terim_metni, aciklama, tek_bolum="TERİMİN ANLAMI"
        )
        self.terim_metni.config(state=tk.DISABLED)

    def anlatimi_hazirla(self):
        self.ders_bolumleri = [
            (
                "1/5 — Soru: Parçacıklar nasıl ilişki kuruyor?",
                "Bu sunumda iki kuantum parçacığının ölçüm sonuçları arasındaki "
                "ilişkiyi inceleyeceğiz. Bazen sonuçlar, parçacıklar çok uzakta olsa "
                "bile birbiriyle bağlantılı görünür.\n\n"
                "Bu durum kulağa bir parçacık "
                "ötekine anında haber veriyormuş gibi gelebilir. Fakat deneylerin "
                "gösterdiği şey kontrol edilebilir bir mesajın ışık hızından hızlı "
                "gittiği değildir.\n\n"
                "Her ölçümün tekil sonucu rastgeledir. Dolaşıklığın "
                "şaşırtıcı yanı, çok sayıda ölçümün birlikte incelendiğinde ortaya "
                "çıkan istatistiksel örüntüdür. Önce bu ayrımı akılda tutalım: "
                "korelasyon, mesaj göndermekle aynı şey değildir.",
            ),
            (
                "2/5 — Spin ve ölçüm ekseni",
                "Simülasyon, spin-1/2 parçacıklar için hazırlanmış ideal bir "
                "dolanık çift modelini kullanır. Spin, parçacığın içsel bir kuantum "
                "özelliğidir; parçacığın minik bir top gibi gerçekten döndüğü "
                "anlamına gelmez.\n\n"
                "Ölçüm yapan kişi bir eksen seçer ve sonuç +1 ya "
                "da -1 olur. A ve B düğmeleri bu eksenlerin açılarını değiştirir. "
                "Eksenler aynı olduğunda bu modelde iki sonuç zıttır. Eksenler "
                "arasındaki açı değiştikçe zıt ya da aynı sonuçların olasılıkları "
                "değişir. Düğmelere basıp önce birkaç ölçüm, sonra çok sayıda "
                "ölçüm çalıştırarak bu değişimi gözleyebilirsin.",
            ),
            (
                "3/5 — Korelasyon ne demek?",
                "Tek ölçüm çifti bize genel kuralı göstermez; şans eseri farklı "
                "sonuçlar çıkabilir. Bunun yerine yüzlerce ya da binlerce çift "
                "ölçülür ve A ile B sonuçlarının çarpımının ortalaması alınır. "
                "\n\n"
                "İdeal singlet modeli için bu beklenti E = -cos(Δ) olur; Δ iki "
                "ölçüm ekseni arasındaki açıdır. E değeri -1 ise sonuçlar tamamen "
                "zıttır, 0 civarındaysa bu ölçüm ayarlarında ortalama korelasyon "
                "yoktur.\n\n"
                "Uygulamadaki “ölçülen” değer sonlu sayıda rastgele "
                "örnekten gelir; “kuramsal” değer ise modelin beklediği değerdir. "
                "Örnek sayısını artırınca ölçülen değer genellikle kuramsal değere "
                "yaklaşır.",
            ),
            (
                "4/5 — Neden hızlı mesaj gönderemiyoruz?",
                "A veya B tarafında tek başına görülen sonuçlar rastgeledir. A "
                "tarafındaki kişi ölçüm ayarını değiştirse bile B tarafındaki kişi "
                "yalnız kendi sonuçlarına bakarak bu değişikliği ayırt edemez.\n\n"
                "İlişkiyi görmek için iki taraftaki kayıtlar karşılaştırılmalıdır. "
                "Bu karşılaştırma telefon, internet ya da başka bir klasik iletişim "
                "yolu gerektirir; bu yollar ışık hızını aşmaz. Fizikte bu özellik "
                "“no-signaling” (dolaşıklıkla kontrol edilebilir mesaj "
                "gönderilememesi) diye anılır. Yani korelasyon çok güçlü ve "
                "şaşırtıcı olabilir; ama tek başına anlık haberleşme sağlamaz.",
            ),
            (
                "5/5 — Simülasyonun sınırları",
                "Bu program gerçek parçacık üretmez ve laboratuvar deneyi değildir. "
                "Kuantum olasılıklarını bilgisayarda örnekleyerek ideal bir modelin "
                "sonuçlarını gösterir.\n\n"
                "Dolayısıyla kara delik, ak delik ya da "
                "ışıktan hızlı bir sinyal hakkında deneysel kanıt sunmaz. Bilimsel "
                "bir projede bilinen sonucu, kendi sorunu ve varsayımını ayrı "
                "tutmak gerekir. Bir sonraki adım, farklı ölçüm açıları için çok "
                "sayıda veri toplamak, ölçülen korelasyonun kuramsal değerle ne "
                "kadar uyuştuğunu incelemek ve kullanılan kaynakları belirtmektir. "
                "Bu şekilde simülasyon, yeni bir keşif iddiası değil, kuantum "
                "korelasyonlarını anlamaya yarayan şeffaf bir öğrenme aracı olur.",
            ),
        ]
        self.ders_sirasi = 0
        self.ders_zamani = None

        govde = ttk.Frame(self.anlatim_sekmesi, padding=24)
        govde.pack(fill=tk.BOTH, expand=True)
        self.ders_baslik = ttk.Label(
            govde, font=("Segoe UI", 18, "bold"), wraplength=850
        )
        self.ders_baslik.pack(anchor="w", pady=(0, 16))
        ttk.Label(
            govde,
            text="Beş kısa bölümde dolaşıklık deneyini, sonuçlarını ve sınırlarını öğren.",
            style="Muted.TLabel",
            wraplength=850,
        ).pack(anchor="w", pady=(0, 14))
        self.ders_metni = tk.Text(
            govde,
            wrap=tk.WORD,
            font=("Segoe UI", 13),
            bg=PANEL,
            fg=BEYAZ,
            padx=26,
            pady=24,
            relief=tk.FLAT,
            height=18,
        )
        self.ders_metni.tag_configure(
            "okunabilir", spacing1=3, spacing2=2, spacing3=10,
            lmargin1=6, rmargin=6,
        )
        self.ders_metni.pack(fill=tk.BOTH, expand=True)

        dugmeler = ttk.Frame(govde)
        dugmeler.pack(fill=tk.X, pady=(12, 4))
        ttk.Button(dugmeler, text="Önceki", command=self.ders_onceki).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(dugmeler, text="Sonraki", command=self.ders_sonraki).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(
            dugmeler, text="5 dk anlatımı başlat", command=self.ders_baslat
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(dugmeler, text="Durdur", command=self.ders_durdur).pack(
            side=tk.LEFT, padx=6
        )
        self.ders_durum = ttk.Label(dugmeler, text="")
        self.ders_durum.pack(side=tk.RIGHT)
        self.ders_goster()

    def ders_goster(self):
        baslik, metin = self.ders_bolumleri[self.ders_sirasi]
        self.ders_baslik.config(text=baslik)
        self.ders_metni.config(state=tk.NORMAL)
        self.metni_bolumlere_ayir(
            self.ders_metni, metin, tek_bolum="ANLATIM"
        )
        self.ders_metni.config(state=tk.DISABLED)
        if self.ders_zamani is None:
            self.ders_durum.config(
                text=f"Bölüm {self.ders_sirasi + 1}/{len(self.ders_bolumleri)}"
            )

    def ders_onceki(self):
        self.ders_durdur()
        self.ders_sirasi = max(0, self.ders_sirasi - 1)
        self.ders_goster()

    def ders_sonraki(self):
        self.ders_durdur()
        self.ders_sirasi = min(len(self.ders_bolumleri) - 1, self.ders_sirasi + 1)
        self.ders_goster()

    def ders_baslat(self):
        self.ders_durdur()
        self.ders_sirasi = 0
        self.ders_goster()
        self.ders_durum.config(text="Otomatik anlatım başladı")
        self.ders_zamani = self.pencere.after(60000, self.ders_otomatik_ilerle)

    def ders_otomatik_ilerle(self):
        self.ders_zamani = None
        if self.ders_sirasi < len(self.ders_bolumleri) - 1:
            self.ders_sirasi += 1
            self.ders_goster()
            self.ders_durum.config(text="Otomatik anlatım sürüyor")
            self.ders_zamani = self.pencere.after(
                60000, self.ders_otomatik_ilerle
            )
        else:
            self.ders_durum.config(text="Anlatım tamamlandı")

    def ders_durdur(self):
        if self.ders_zamani is not None:
            self.pencere.after_cancel(self.ders_zamani)
            self.ders_zamani = None
            self.ders_durum.config(text="Anlatım durduruldu")

    def aci_degistir(self, taraf, miktar):
        if taraf == "a":
            self.aci_a = (self.aci_a + miktar) % 360
        else:
            self.aci_b = (self.aci_b + miktar) % 360
        self.ciz()

    def bir_cift_olc(self):
        sonuc_a, sonuc_b = dolasik_cift_olc(self.aci_a, self.aci_b)
        self.toplam += 1
        self.toplam_carpim += sonuc_a * sonuc_b
        self.sayilar_a[sonuc_a] += 1
        self.sayilar_b[sonuc_b] += 1
        self.son_cift = (sonuc_a, sonuc_b)
        self.ciz()

    def bin_cift_olc(self):
        for _ in range(1000):
            sonuc_a, sonuc_b = dolasik_cift_olc(self.aci_a, self.aci_b)
            self.toplam += 1
            self.toplam_carpim += sonuc_a * sonuc_b
            self.sayilar_a[sonuc_a] += 1
            self.sayilar_b[sonuc_b] += 1
            self.son_cift = (sonuc_a, sonuc_b)
        self.ciz()

    def sifirla(self):
        self.toplam = 0
        self.toplam_carpim = 0
        self.sayilar_a = {-1: 0, 1: 0}
        self.sayilar_b = {-1: 0, 1: 0}
        self.son_cift = None
        self.ciz()

    def tus_ciz(self, merkez, aci, renk):
        x, y = merkez
        yari_uzunluk = 52
        radyan = math.radians(aci)
        dx = math.cos(radyan) * yari_uzunluk
        dy = math.sin(radyan) * yari_uzunluk
        self.kanvas.create_line(
            x - dx, y + dy, x + dx, y - dy, fill=renk, width=4
        )
        self.kanvas.create_oval(
            x - 7, y - 7, x + 7, y + 7, fill=renk, outline=""
        )

    def yuzde(self, adet):
        if not self.toplam:
            return 0.0
        return 100 * adet / self.toplam

    def ciz(self):
        c = self.kanvas
        c.delete("all")
        rastgele = random.Random(17)
        for _ in range(55):
            x = rastgele.randint(4, GENISLIK - 4)
            y = rastgele.randint(4, YUKSEKLIK - 4)
            c.create_oval(
                x, y, x + 2, y + 2,
                fill=rastgele.choice(("#334155", "#475569", "#164e63")),
                outline="",
            )
        c.create_rectangle(25, 15, 435, 220, fill=PANEL, outline="#1b2a3e", width=1)
        c.create_rectangle(465, 15, 875, 220, fill=PANEL, outline="#1b2a3e", width=1)
        c.create_text(
            55, 42, text="Olcum A", fill=MAVI, anchor="w",
            font=("Segoe UI", 15, "bold")
        )
        c.create_text(
            495, 42, text="Olcum B", fill=TURUNCU, anchor="w",
            font=("Segoe UI", 15, "bold")
        )
        c.create_text(
            55, 72, text=f"Olcum ekseni: {self.aci_a} derece",
            fill=SOLUK, anchor="w", font=("Segoe UI", 10)
        )
        c.create_text(
            495, 72, text=f"Olcum ekseni: {self.aci_b} derece",
            fill=SOLUK, anchor="w", font=("Segoe UI", 10)
        )
        self.tus_ciz((230, 135), self.aci_a, MAVI)
        self.tus_ciz((670, 135), self.aci_b, TURUNCU)

        if self.son_cift is None:
            sonuc_a = "Son sonuc: henuz olcum yok"
            sonuc_b = "Son sonuc: henuz olcum yok"
        else:
            sonuc_a = f"Son sonuc: {self.son_cift[0]:+d}"
            sonuc_b = f"Son sonuc: {self.son_cift[1]:+d}"
        c.create_text(
            55, 190, text=sonuc_a, fill=MAVI, anchor="w",
            font=("Segoe UI", 11, "bold")
        )
        c.create_text(
            495, 190, text=sonuc_b, fill=TURUNCU, anchor="w",
            font=("Segoe UI", 11, "bold")
        )

        c.create_rectangle(25, 240, 875, 395, fill=PANEL, outline="#1b2a3e", width=1)
        c.create_text(
            55, 266, text=f"Olculen cift sayisi: {self.toplam}",
            fill=BEYAZ, anchor="w", font=("Segoe UI", 11)
        )
        c.create_text(
            55, 300,
            text=(
                f"A tek-basina: +1 %{self.yuzde(self.sayilar_a[1]):.1f}  "
                f"-1 %{self.yuzde(self.sayilar_a[-1]):.1f}"
            ),
            fill=MAVI, anchor="w", font=("Segoe UI", 10)
        )
        c.create_text(
            455, 300,
            text=(
                f"B tek-basina: +1 %{self.yuzde(self.sayilar_b[1]):.1f}  "
                f"-1 %{self.yuzde(self.sayilar_b[-1]):.1f}"
            ),
            fill=TURUNCU, anchor="w", font=("Segoe UI", 10)
        )

        aci_farki = math.radians(self.aci_a - self.aci_b)
        beklenen = -math.cos(aci_farki)
        olculen = self.toplam_carpim / self.toplam if self.toplam else 0.0
        c.create_text(
            55, 342,
            text=f"Korelasyon A x B: olculen {olculen:+.3f} | kuramsal {beklenen:+.3f}",
            fill=YESIL, anchor="w", font=("Segoe UI", 10)
        )

        c.create_rectangle(25, 415, 875, 555, fill=PANEL, outline="#1b2a3e", width=1)
        c.create_text(
            50, 440,
            text="Bu model neyi gosteriyor?",
            fill=BEYAZ, anchor="w", font=("Segoe UI", 11, "bold")
        )
        c.create_text(
            50, 470,
            text="Ayni olcum ekseninde sonuclar zit; eksenler farkliysa korelasyon degisir.",
            fill=SOLUK, anchor="w", font=("Segoe UI", 10)
        )
        c.create_text(
            50, 500,
            text="Her tarafin tek-basina sonuclari rastgele kalir; diger tarafin ayariyla mesaj kodlanamaz.",
            fill=SOLUK, anchor="w", font=("Segoe UI", 10)
        )
        c.create_text(
            50, 530,
            text="Bu, ideal spin-1/2 dolasik cift icin matematiksel egitim modelidir; gercek deney degildir.",
            fill=SOLUK, anchor="w", font=("Segoe UI", 10)
        )


def main():
    windows_dpi_ayarla()
    pencere = tk.Tk()
    DolasiklikSunumu(pencere)
    pencere.mainloop()


if __name__ == "__main__":
    main()
