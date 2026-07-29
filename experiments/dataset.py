"""52 moderately complex, refactor-worthy Java snippets for the HUMAN-AI trust study.

Design goals:
- Diverse problem families (not only sort/search)
- Valid Java that still benefits from refactoring
- Messy naming, nested logic, mild duplication on purpose
"""

SELECTED_DATASET = [
    {
        "id": "code_01",
        "source_reference": "study://human-ai/search/OrderLookup",
        "description": "Siparis listesinde musteri kimligine gore kayit arama",
        "original_code": """package study.search;

public class OrderLookup {
    public static int find(String[][] rows, String cid) {
        if (rows == null) return -1;
        int i = 0;
        while (i < rows.length) {
            String[] r = rows[i];
            if (r != null && r.length > 1) {
                String a = r[0];
                String b = r[1];
                if (a != null && b != null) {
                    if (a.trim().equalsIgnoreCase(cid == null ? "" : cid.trim())) {
                        return i;
                    }
                }
            }
            i = i + 1;
        }
        return -1;
    }
}""",
    },
    {
        "id": "code_02",
        "source_reference": "study://human-ai/sort/ScoreBoard",
        "description": "Ogrenci notlarini bubble sort ile siralama",
        "original_code": """package study.sort;

public class ScoreBoard {
    public static void arrange(int[] s) {
        if (s == null) return;
        int n = s.length;
        for (int x = 0; x < n; x++) {
            boolean f = false;
            for (int y = 0; y < n - 1; y++) {
                int p = s[y];
                int q = s[y + 1];
                if (p < q) {
                    s[y] = q;
                    s[y + 1] = p;
                    f = true;
                }
            }
            if (!f) {
                break;
            }
        }
    }
}""",
    },
    {
        "id": "code_03",
        "source_reference": "study://human-ai/string/TicketCode",
        "description": "Bilet kodunu normalize edip dogrulama",
        "original_code": """package study.stringutil;

public class TicketCode {
    public static boolean ok(String raw) {
        if (raw == null) return false;
        String t = raw.trim().toUpperCase();
        if (t.length() < 6) return false;
        if (t.length() > 12) return false;
        int i = 0;
        int letters = 0;
        int digits = 0;
        while (i < t.length()) {
            char c = t.charAt(i);
            if (c >= 'A' && c <= 'Z') letters++;
            else if (c >= '0' && c <= '9') digits++;
            else return false;
            i++;
        }
        if (letters < 2) return false;
        if (digits < 2) return false;
        return true;
    }
}""",
    },
    {
        "id": "code_04",
        "source_reference": "study://human-ai/ds/SimpleCache",
        "description": "Basit anahtar-deger onbellek (sabit kapasite)",
        "original_code": """package study.ds;

public class SimpleCache {
    private String[] k;
    private String[] v;
    private int n;

    public SimpleCache(int cap) {
        if (cap < 1) cap = 1;
        k = new String[cap];
        v = new String[cap];
        n = 0;
    }

    public void put(String key, String val) {
        if (key == null) return;
        for (int i = 0; i < n; i++) {
            if (k[i].equals(key)) {
                v[i] = val;
                return;
            }
        }
        if (n >= k.length) {
            for (int i = 1; i < n; i++) {
                k[i - 1] = k[i];
                v[i - 1] = v[i];
            }
            n = n - 1;
        }
        k[n] = key;
        v[n] = val;
        n = n + 1;
    }

    public String get(String key) {
        if (key == null) return null;
        for (int i = 0; i < n; i++) {
            if (k[i].equals(key)) return v[i];
        }
        return null;
    }
}""",
    },
    {
        "id": "code_05",
        "source_reference": "study://human-ai/math/InvoiceMath",
        "description": "Fatura satirlari icin KDV dahil toplam",
        "original_code": """package study.math;

public class InvoiceMath {
    public static double total(double[] prices, double[] qty, double tax) {
        if (prices == null || qty == null) return 0;
        int m = prices.length;
        if (qty.length < m) m = qty.length;
        double s = 0;
        for (int i = 0; i < m; i++) {
            double p = prices[i];
            double q = qty[i];
            if (p < 0) p = 0;
            if (q < 0) q = 0;
            double line = p * q;
            if (tax > 0) {
                line = line + (line * tax);
            }
            s = s + line;
        }
        return Math.round(s * 100.0) / 100.0;
    }
}""",
    },
    {
        "id": "code_06",
        "source_reference": "study://human-ai/parse/CsvRow",
        "description": "CSV satirini alanlara ayirma (tirnak destekli basit)",
        "original_code": """package study.parse;

import java.util.ArrayList;
import java.util.List;

public class CsvRow {
    public static List<String> split(String line) {
        List<String> out = new ArrayList<String>();
        if (line == null) return out;
        String cur = "";
        boolean q = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '"') {
                q = !q;
            } else if (c == ',' && !q) {
                out.add(cur);
                cur = "";
            } else {
                cur = cur + c;
            }
        }
        out.add(cur);
        return out;
    }
}""",
    },
    {
        "id": "code_07",
        "source_reference": "study://human-ai/tree/OrgNode",
        "description": "Organizasyon agacinda derinlik hesaplama",
        "original_code": """package study.tree;

import java.util.List;

public class OrgNode {
    public String name;
    public List<OrgNode> kids;

    public OrgNode(String name, List<OrgNode> kids) {
        this.name = name;
        this.kids = kids;
    }

    public static int depth(OrgNode n) {
        if (n == null) return 0;
        if (n.kids == null || n.kids.size() == 0) return 1;
        int best = 0;
        for (int i = 0; i < n.kids.size(); i++) {
            OrgNode c = n.kids.get(i);
            int d = depth(c);
            if (d > best) best = d;
        }
        return best + 1;
    }
}""",
    },
    {
        "id": "code_08",
        "source_reference": "study://human-ai/validate/PasswordGate",
        "description": "Sifre guvenlik kurallarini kontrol etme",
        "original_code": """package study.validate;

public class PasswordGate {
    public static boolean accept(String p) {
        if (p == null) return false;
        if (p.length() < 8) return false;
        boolean up = false;
        boolean low = false;
        boolean dig = false;
        boolean sp = false;
        for (int i = 0; i < p.length(); i++) {
            char c = p.charAt(i);
            if (c >= 'A' && c <= 'Z') up = true;
            else if (c >= 'a' && c <= 'z') low = true;
            else if (c >= '0' && c <= '9') dig = true;
            else sp = true;
        }
        if (!up) return false;
        if (!low) return false;
        if (!dig) return false;
        if (!sp) return false;
        return true;
    }
}""",
    },
    {
        "id": "code_09",
        "source_reference": "study://human-ai/schedule/MeetingOverlap",
        "description": "Iki toplantinin cakisip cakismadigini kontrol",
        "original_code": """package study.schedule;

public class MeetingOverlap {
    public static boolean clash(int s1, int e1, int s2, int e2) {
        if (e1 < s1) {
            int t = s1;
            s1 = e1;
            e1 = t;
        }
        if (e2 < s2) {
            int t = s2;
            s2 = e2;
            e2 = t;
        }
        if (e1 <= s2) return false;
        if (e2 <= s1) return false;
        return true;
    }
}""",
    },
    {
        "id": "code_10",
        "source_reference": "study://human-ai/text/KeywordScore",
        "description": "Metinde anahtar kelime skorlama",
        "original_code": """package study.text;

public class KeywordScore {
    public static int score(String text, String[] keys) {
        if (text == null || keys == null) return 0;
        String t = text.toLowerCase();
        int s = 0;
        for (int i = 0; i < keys.length; i++) {
            String k = keys[i];
            if (k == null || k.trim().isEmpty()) continue;
            String kk = k.toLowerCase().trim();
            int from = 0;
            while (true) {
                int p = t.indexOf(kk, from);
                if (p < 0) break;
                s = s + 1;
                from = p + kk.length();
            }
        }
        return s;
    }
}""",
    },
    {
        "id": "code_11",
        "source_reference": "study://human-ai/inventory/StockMove",
        "description": "Stok artirma/azaltma ve negatif engelleme",
        "original_code": """package study.inventory;

public class StockMove {
    private int q;

    public StockMove(int start) {
        if (start < 0) start = 0;
        q = start;
    }

    public boolean apply(String type, int amount) {
        if (amount < 0) return false;
        if (type == null) return false;
        String t = type.trim().toLowerCase();
        if (t.equals("in") || t.equals("add")) {
            q = q + amount;
            return true;
        }
        if (t.equals("out") || t.equals("remove")) {
            if (q < amount) return false;
            q = q - amount;
            return true;
        }
        return false;
    }

    public int qty() {
        return q;
    }
}""",
    },
    {
        "id": "code_12",
        "source_reference": "study://human-ai/graph/FriendReach",
        "description": "Arkadaslik matrisinde 1 adim ulasilabilirlik",
        "original_code": """package study.graph;

import java.util.ArrayList;
import java.util.List;

public class FriendReach {
    public static List<Integer> near(boolean[][] g, int me) {
        List<Integer> out = new ArrayList<Integer>();
        if (g == null) return out;
        if (me < 0 || me >= g.length) return out;
        boolean[] row = g[me];
        if (row == null) return out;
        for (int j = 0; j < row.length; j++) {
            if (j == me) continue;
            if (row[j]) out.add(j);
        }
        return out;
    }
}""",
    },
    {
        "id": "code_13",
        "source_reference": "study://human-ai/finance/Installment",
        "description": "Taksit tutarini faiz ile hesaplama",
        "original_code": """package study.finance;

public class Installment {
    public static double[] plan(double amount, int months, double rate) {
        if (months < 1) months = 1;
        if (amount < 0) amount = 0;
        if (rate < 0) rate = 0;
        double[] out = new double[months];
        double left = amount;
        for (int i = 0; i < months; i++) {
            double interest = left * rate;
            double base = amount / months;
            double pay = base + interest;
            out[i] = Math.round(pay * 100.0) / 100.0;
            left = left - base;
            if (left < 0) left = 0;
        }
        return out;
    }
}""",
    },
    {
        "id": "code_14",
        "source_reference": "study://human-ai/string/SlugMaker",
        "description": "Basliktan URL slug uretme",
        "original_code": """package study.stringutil;

public class SlugMaker {
    public static String make(String title) {
        if (title == null) return "";
        String s = title.trim().toLowerCase();
        StringBuilder b = new StringBuilder();
        boolean dash = false;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) {
                b.append(c);
                dash = false;
            } else if (c == ' ' || c == '_' || c == '-') {
                if (!dash && b.length() > 0) {
                    b.append('-');
                    dash = true;
                }
            }
        }
        String r = b.toString();
        if (r.endsWith("-")) r = r.substring(0, r.length() - 1);
        return r;
    }
}""",
    },
    {
        "id": "code_15",
        "source_reference": "study://human-ai/ds/RingBuffer",
        "description": "Sabit boyutlu dairesel tampon",
        "original_code": """package study.ds;

public class RingBuffer {
    private int[] d;
    private int h;
    private int t;
    private int c;

    public RingBuffer(int size) {
        if (size < 1) size = 1;
        d = new int[size];
        h = 0;
        t = 0;
        c = 0;
    }

    public boolean push(int x) {
        if (c == d.length) return false;
        d[t] = x;
        t = (t + 1) % d.length;
        c = c + 1;
        return true;
    }

    public int pop() {
        if (c == 0) return Integer.MIN_VALUE;
        int v = d[h];
        h = (h + 1) % d.length;
        c = c - 1;
        return v;
    }

    public int size() {
        return c;
    }
}""",
    },
    {
        "id": "code_16",
        "source_reference": "study://human-ai/time/WorkHours",
        "description": "Calisma dakikalarini saat:dakika formatina cevirme",
        "original_code": """package study.time;

public class WorkHours {
    public static String fmt(int minutes) {
        if (minutes < 0) minutes = 0;
        int h = minutes / 60;
        int m = minutes % 60;
        String hs = String.valueOf(h);
        String ms = String.valueOf(m);
        if (hs.length() < 2) hs = "0" + hs;
        if (ms.length() < 2) ms = "0" + ms;
        return hs + ":" + ms;
    }

    public static int parse(String hhmm) {
        if (hhmm == null) return 0;
        String[] p = hhmm.split(":");
        if (p.length != 2) return 0;
        try {
            int h = Integer.parseInt(p[0].trim());
            int m = Integer.parseInt(p[1].trim());
            if (h < 0) h = 0;
            if (m < 0) m = 0;
            if (m > 59) m = 59;
            return h * 60 + m;
        } catch (Exception e) {
            return 0;
        }
    }
}""",
    },
    {
        "id": "code_17",
        "source_reference": "study://human-ai/stats/MovingAvg",
        "description": "Basit hareketli ortalama hesabi",
        "original_code": """package study.stats;

public class MovingAvg {
    public static double[] calc(double[] data, int w) {
        if (data == null) return new double[0];
        if (w < 1) w = 1;
        if (w > data.length) w = data.length;
        double[] out = new double[data.length - w + 1];
        for (int i = 0; i < out.length; i++) {
            double s = 0;
            for (int j = 0; j < w; j++) {
                s = s + data[i + j];
            }
            out[i] = s / w;
        }
        return out;
    }
}""",
    },
    {
        "id": "code_18",
        "source_reference": "study://human-ai/path/RelPath",
        "description": "Iki yol parcasini guvenli birlestirme",
        "original_code": """package study.path;

public class RelPath {
    public static String join(String a, String b) {
        if (a == null) a = "";
        if (b == null) b = "";
        a = a.replace('\\\\', '/').trim();
        b = b.replace('\\\\', '/').trim();
        while (a.endsWith("/")) a = a.substring(0, a.length() - 1);
        while (b.startsWith("/")) b = b.substring(1);
        if (a.isEmpty()) return b;
        if (b.isEmpty()) return a;
        return a + "/" + b;
    }
}""",
    },
    {
        "id": "code_19",
        "source_reference": "study://human-ai/list/DedupKeepOrder",
        "description": "Listeden tekrarlari silip sirayi koruma",
        "original_code": """package study.listutil;

import java.util.ArrayList;
import java.util.List;

public class DedupKeepOrder {
    public static List<String> clean(List<String> in) {
        List<String> out = new ArrayList<String>();
        if (in == null) return out;
        for (int i = 0; i < in.size(); i++) {
            String x = in.get(i);
            if (x == null) continue;
            boolean seen = false;
            for (int j = 0; j < out.size(); j++) {
                if (out.get(j).equals(x)) {
                    seen = true;
                    break;
                }
            }
            if (!seen) out.add(x);
        }
        return out;
    }
}""",
    },
    {
        "id": "code_20",
        "source_reference": "study://human-ai/net/RetryDelay",
        "description": "Ussel geri deneme bekleme suresi",
        "original_code": """package study.net;

public class RetryDelay {
    public static long waitMs(int attempt, long base, long max) {
        if (attempt < 0) attempt = 0;
        if (base < 1) base = 1;
        if (max < base) max = base;
        long v = base;
        for (int i = 0; i < attempt; i++) {
            if (v > max / 2) {
                v = max;
                break;
            }
            v = v * 2;
        }
        if (v > max) v = max;
        return v;
    }
}""",
    },
    {
        "id": "code_21",
        "source_reference": "study://human-ai/matrix/SparseSum",
        "description": "Seyrek matriste satir toplamlari",
        "original_code": """package study.matrix;

public class SparseSum {
    public static int[] rowSums(int[][] m) {
        if (m == null) return new int[0];
        int[] out = new int[m.length];
        for (int i = 0; i < m.length; i++) {
            int s = 0;
            int[] row = m[i];
            if (row != null) {
                for (int j = 0; j < row.length; j++) {
                    int v = row[j];
                    if (v != 0) s = s + v;
                }
            }
            out[i] = s;
        }
        return out;
    }
}""",
    },
    {
        "id": "code_22",
        "source_reference": "study://human-ai/auth/SessionToken",
        "description": "Oturum jetonu format kontrolu",
        "original_code": """package study.auth;

public class SessionToken {
    public static boolean valid(String token) {
        if (token == null) return false;
        String t = token.trim();
        String[] p = t.split("\\\\.");
        if (p.length != 3) return false;
        for (int i = 0; i < p.length; i++) {
            String part = p[i];
            if (part.length() < 4) return false;
            for (int j = 0; j < part.length(); j++) {
                char c = part.charAt(j);
                boolean ok = (c >= 'a' && c <= 'z')
                        || (c >= 'A' && c <= 'Z')
                        || (c >= '0' && c <= '9')
                        || c == '-' || c == '_';
                if (!ok) return false;
            }
        }
        return true;
    }
}""",
    },
    {
        "id": "code_23",
        "source_reference": "study://human-ai/shop/DiscountStack",
        "description": "Kupon ve yuzde indirimini sirayla uygulama",
        "original_code": """package study.shop;

public class DiscountStack {
    public static double apply(double price, double pct, double coupon) {
        if (price < 0) price = 0;
        if (pct < 0) pct = 0;
        if (pct > 100) pct = 100;
        if (coupon < 0) coupon = 0;
        double afterPct = price - (price * pct / 100.0);
        double after = afterPct - coupon;
        if (after < 0) after = 0;
        return Math.round(after * 100.0) / 100.0;
    }
}""",
    },
    {
        "id": "code_24",
        "source_reference": "study://human-ai/text/DiffLines",
        "description": "Iki metin satiri listesinde farkli indeksler",
        "original_code": """package study.text;

import java.util.ArrayList;
import java.util.List;

public class DiffLines {
    public static List<Integer> diff(String[] a, String[] b) {
        List<Integer> out = new ArrayList<Integer>();
        if (a == null) a = new String[0];
        if (b == null) b = new String[0];
        int n = a.length;
        if (b.length > n) n = b.length;
        for (int i = 0; i < n; i++) {
            String x = i < a.length ? a[i] : null;
            String y = i < b.length ? b[i] : null;
            if (x == null && y == null) continue;
            if (x == null || y == null || !x.equals(y)) out.add(i);
        }
        return out;
    }
}""",
    },
    {
        "id": "code_25",
        "source_reference": "study://human-ai/queue/PriorityJob",
        "description": "Oncelikli is ekleme (kucuk sayi once)",
        "original_code": """package study.queue;

import java.util.ArrayList;
import java.util.List;

public class PriorityJob {
    private List<String> names = new ArrayList<String>();
    private List<Integer> prios = new ArrayList<Integer>();

    public void add(String name, int prio) {
        if (name == null) return;
        int i = 0;
        while (i < prios.size() && prios.get(i) <= prio) {
            i++;
        }
        names.add(i, name);
        prios.add(i, prio);
    }

    public String next() {
        if (names.isEmpty()) return null;
        prios.remove(0);
        return names.remove(0);
    }
}""",
    },
    {
        "id": "code_26",
        "source_reference": "study://human-ai/geo/BoundingBox",
        "description": "Noktanin dikdortgen alan icinde olup olmadigi",
        "original_code": """package study.geo;

public class BoundingBox {
    public static boolean inside(double x, double y, double minX, double minY, double maxX, double maxY) {
        if (minX > maxX) {
            double t = minX;
            minX = maxX;
            maxX = t;
        }
        if (minY > maxY) {
            double t = minY;
            minY = maxY;
            maxY = t;
        }
        if (x < minX) return false;
        if (x > maxX) return false;
        if (y < minY) return false;
        if (y > maxY) return false;
        return true;
    }
}""",
    },
    {
        "id": "code_27",
        "source_reference": "study://human-ai/log/LevelFilter",
        "description": "Log seviyesine gore satir filtreleme",
        "original_code": """package study.log;

import java.util.ArrayList;
import java.util.List;

public class LevelFilter {
    public static List<String> keep(String[] lines, String level) {
        List<String> out = new ArrayList<String>();
        if (lines == null || level == null) return out;
        String L = level.trim().toUpperCase();
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i];
            if (line == null) continue;
            String u = line.toUpperCase();
            if (u.contains("[" + L + "]") || u.startsWith(L + ":")) {
                out.add(line);
            }
        }
        return out;
    }
}""",
    },
    {
        "id": "code_28",
        "source_reference": "study://human-ai/bits/FlagPack",
        "description": "Boolean bayraklari tek int icinde paketleme",
        "original_code": """package study.bits;

public class FlagPack {
    public static int pack(boolean a, boolean b, boolean c, boolean d) {
        int v = 0;
        if (a) v = v + 1;
        if (b) v = v + 2;
        if (c) v = v + 4;
        if (d) v = v + 8;
        return v;
    }

    public static boolean[] unpack(int v) {
        boolean[] out = new boolean[4];
        out[0] = (v & 1) != 0;
        out[1] = (v & 2) != 0;
        out[2] = (v & 4) != 0;
        out[3] = (v & 8) != 0;
        return out;
    }
}""",
    },
    {
        "id": "code_29",
        "source_reference": "study://human-ai/school/GradeCurve",
        "description": "Ham notu harf notuna cevirme",
        "original_code": """package study.school;

public class GradeCurve {
    public static String letter(int score) {
        if (score < 0) score = 0;
        if (score > 100) score = 100;
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }

    public static int bump(int score, int curve) {
        int s = score + curve;
        if (s < 0) s = 0;
        if (s > 100) s = 100;
        return s;
    }
}""",
    },
    {
        "id": "code_30",
        "source_reference": "study://human-ai/stream/WindowCount",
        "description": "Pencere icinde esik asan deger sayisi",
        "original_code": """package study.stream;

public class WindowCount {
    public static int count(int[] data, int start, int end, int thr) {
        if (data == null) return 0;
        if (start < 0) start = 0;
        if (end > data.length) end = data.length;
        if (end < start) {
            int t = start;
            start = end;
            end = t;
        }
        int c = 0;
        for (int i = start; i < end; i++) {
            if (data[i] > thr) c = c + 1;
        }
        return c;
    }
}""",
    },
    {
        "id": "code_31",
        "source_reference": "study://human-ai/xmlish/TagStrip",
        "description": "Basit etiketleri metinden temizleme",
        "original_code": """package study.xmlish;

public class TagStrip {
    public static String strip(String html) {
        if (html == null) return "";
        StringBuilder b = new StringBuilder();
        boolean in = false;
        for (int i = 0; i < html.length(); i++) {
            char c = html.charAt(i);
            if (c == '<') {
                in = true;
            } else if (c == '>') {
                in = false;
            } else if (!in) {
                b.append(c);
            }
        }
        return b.toString().trim();
    }
}""",
    },
    {
        "id": "code_32",
        "source_reference": "study://human-ai/hr/ShiftSwap",
        "description": "Iki calisanin vardiya kayitlarini degistirme",
        "original_code": """package study.hr;

public class ShiftSwap {
    public static boolean swap(String[] shifts, int i, int j) {
        if (shifts == null) return false;
        if (i < 0 || j < 0) return false;
        if (i >= shifts.length || j >= shifts.length) return false;
        String a = shifts[i];
        String b = shifts[j];
        shifts[i] = b;
        shifts[j] = a;
        return true;
    }
}""",
    },
    {
        "id": "code_33",
        "source_reference": "study://human-ai/cryptoish/Checksum",
        "description": "Basit kayan toplam checksum",
        "original_code": """package study.cryptoish;

public class Checksum {
    public static int rolling(String data, int mod) {
        if (data == null) return 0;
        if (mod < 2) mod = 256;
        int s = 0;
        for (int i = 0; i < data.length(); i++) {
            s = (s + data.charAt(i)) % mod;
            s = (s * 31) % mod;
        }
        return s;
    }
}""",
    },
    {
        "id": "code_34",
        "source_reference": "study://human-ai/array/RotateRight",
        "description": "Diziyi saga k adim dondurme",
        "original_code": """package study.arrayutil;

public class RotateRight {
    public static void rotate(int[] a, int k) {
        if (a == null || a.length == 0) return;
        int n = a.length;
        if (k < 0) k = n - ((-k) % n);
        k = k % n;
        if (k == 0) return;
        int[] tmp = new int[n];
        for (int i = 0; i < n; i++) {
            int ni = (i + k) % n;
            tmp[ni] = a[i];
        }
        for (int i = 0; i < n; i++) a[i] = tmp[i];
    }
}""",
    },
    {
        "id": "code_35",
        "source_reference": "study://human-ai/booking/SeatMap",
        "description": "Koltuk haritasinda bos yer bulma",
        "original_code": """package study.booking;

public class SeatMap {
    public static int[] findFree(boolean[][] seats) {
        if (seats == null) return null;
        for (int r = 0; r < seats.length; r++) {
            boolean[] row = seats[r];
            if (row == null) continue;
            for (int c = 0; c < row.length; c++) {
                if (!row[c]) {
                    return new int[] {r, c};
                }
            }
        }
        return null;
    }
}""",
    },
    {
        "id": "code_36",
        "source_reference": "study://human-ai/text/CamelToSnake",
        "description": "camelCase ifadeyi snake_case yapmak",
        "original_code": """package study.text;

public class CamelToSnake {
    public static String conv(String s) {
        if (s == null || s.isEmpty()) return "";
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= 'A' && c <= 'Z') {
                if (b.length() > 0) b.append('_');
                b.append((char) (c + 32));
            } else {
                b.append(c);
            }
        }
        return b.toString();
    }
}""",
    },
    {
        "id": "code_37",
        "source_reference": "study://human-ai/metrics/ErrorRate",
        "description": "Basari/hata sayisindan hata orani",
        "original_code": """package study.metrics;

public class ErrorRate {
    public static double rate(int ok, int fail) {
        if (ok < 0) ok = 0;
        if (fail < 0) fail = 0;
        int t = ok + fail;
        if (t == 0) return 0.0;
        double r = (fail * 1.0) / t;
        return Math.round(r * 10000.0) / 10000.0;
    }
}""",
    },
    {
        "id": "code_38",
        "source_reference": "study://human-ai/tree/PathJoinNodes",
        "description": "Agac dugum yolunu birlestirme",
        "original_code": """package study.tree;

public class PathJoinNodes {
    public static String path(String[] parts) {
        if (parts == null) return "";
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            String p = parts[i];
            if (p == null) continue;
            p = p.trim();
            if (p.isEmpty()) continue;
            if (b.length() > 0) b.append('/');
            b.append(p);
        }
        return b.toString();
    }
}""",
    },
    {
        "id": "code_39",
        "source_reference": "study://human-ai/security/IpAllow",
        "description": "IP adresinin izin listesinde olup olmadigi",
        "original_code": """package study.security;

public class IpAllow {
    public static boolean allowed(String ip, String[] allow) {
        if (ip == null || allow == null) return false;
        String x = ip.trim();
        for (int i = 0; i < allow.length; i++) {
            String a = allow[i];
            if (a == null) continue;
            a = a.trim();
            if (a.equals("*")) return true;
            if (a.endsWith(".*")) {
                String prefix = a.substring(0, a.length() - 1);
                if (x.startsWith(prefix)) return true;
            } else if (a.equals(x)) {
                return true;
            }
        }
        return false;
    }
}""",
    },
    {
        "id": "code_40",
        "source_reference": "study://human-ai/compress/RleEncode",
        "description": "Basit run-length encode",
        "original_code": """package study.compress;

public class RleEncode {
    public static String encode(String s) {
        if (s == null || s.isEmpty()) return "";
        StringBuilder b = new StringBuilder();
        char cur = s.charAt(0);
        int cnt = 1;
        for (int i = 1; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == cur) {
                cnt++;
            } else {
                b.append(cur);
                b.append(cnt);
                cur = c;
                cnt = 1;
            }
        }
        b.append(cur);
        b.append(cnt);
        return b.toString();
    }
}""",
    },
    {
        "id": "code_41",
        "source_reference": "study://human-ai/bank/IbanMask",
        "description": "IBAN numarasini maskeleme",
        "original_code": """package study.bank;

public class IbanMask {
    public static String mask(String iban) {
        if (iban == null) return "";
        String t = iban.replace(" ", "").toUpperCase();
        if (t.length() <= 8) return t;
        String start = t.substring(0, 4);
        String end = t.substring(t.length() - 4);
        StringBuilder mid = new StringBuilder();
        for (int i = 0; i < t.length() - 8; i++) mid.append('*');
        return start + mid.toString() + end;
    }
}""",
    },
    {
        "id": "code_42",
        "source_reference": "study://human-ai/game/ScoreCombo",
        "description": "Ardisik isabet kombo skoru",
        "original_code": """package study.game;

public class ScoreCombo {
    public static int combo(boolean[] hits) {
        if (hits == null) return 0;
        int best = 0;
        int cur = 0;
        for (int i = 0; i < hits.length; i++) {
            if (hits[i]) {
                cur = cur + 1;
                if (cur > best) best = cur;
            } else {
                cur = 0;
            }
        }
        return best;
    }
}""",
    },
    {
        "id": "code_43",
        "source_reference": "study://human-ai/mail/AddressBook",
        "description": "E-posta listesinde domain’e gore filtre",
        "original_code": """package study.mail;

import java.util.ArrayList;
import java.util.List;

public class AddressBook {
    public static List<String> byDomain(String[] mails, String domain) {
        List<String> out = new ArrayList<String>();
        if (mails == null || domain == null) return out;
        String d = domain.trim().toLowerCase();
        for (int i = 0; i < mails.length; i++) {
            String m = mails[i];
            if (m == null) continue;
            m = m.trim();
            int at = m.indexOf('@');
            if (at < 1) continue;
            String dom = m.substring(at + 1).toLowerCase();
            if (dom.equals(d)) out.add(m);
        }
        return out;
    }
}""",
    },
    {
        "id": "code_44",
        "source_reference": "study://human-ai/units/TempConvert",
        "description": "Sicaklik birimi donusumu",
        "original_code": """package study.units;

public class TempConvert {
    public static double conv(double v, String from, String to) {
        if (from == null || to == null) return v;
        String f = from.trim().toUpperCase();
        String t = to.trim().toUpperCase();
        double c = v;
        if (f.equals("F")) c = (v - 32.0) * 5.0 / 9.0;
        else if (f.equals("K")) c = v - 273.15;
        else if (!f.equals("C")) return v;
        if (t.equals("C")) return Math.round(c * 100.0) / 100.0;
        if (t.equals("F")) return Math.round(((c * 9.0 / 5.0) + 32.0) * 100.0) / 100.0;
        if (t.equals("K")) return Math.round((c + 273.15) * 100.0) / 100.0;
        return v;
    }
}""",
    },
    {
        "id": "code_45",
        "source_reference": "study://human-ai/workflow/StepGate",
        "description": "Is akisi adimlarinin sirayla tamamlanmasi",
        "original_code": """package study.workflow;

public class StepGate {
    public static boolean canRun(boolean[] done, int step) {
        if (done == null) return false;
        if (step < 0 || step >= done.length) return false;
        for (int i = 0; i < step; i++) {
            if (!done[i]) return false;
        }
        return !done[step];
    }

    public static void mark(boolean[] done, int step) {
        if (done == null) return;
        if (step < 0 || step >= done.length) return;
        done[step] = true;
    }
}""",
    },
    {
        "id": "code_46",
        "source_reference": "study://human-ai/search/MultiKeyFilter",
        "description": "Kayitlarda birden fazla alana gore filtre",
        "original_code": """package study.search;

import java.util.ArrayList;
import java.util.List;

public class MultiKeyFilter {
    public static List<Integer> filter(String[][] rows, String city, String status) {
        List<Integer> out = new ArrayList<Integer>();
        if (rows == null) return out;
        for (int i = 0; i < rows.length; i++) {
            String[] r = rows[i];
            if (r == null || r.length < 3) continue;
            boolean ok = true;
            if (city != null && city.trim().length() > 0) {
                if (r[1] == null || !r[1].equalsIgnoreCase(city.trim())) ok = false;
            }
            if (ok && status != null && status.trim().length() > 0) {
                if (r[2] == null || !r[2].equalsIgnoreCase(status.trim())) ok = false;
            }
            if (ok) out.add(i);
        }
        return out;
    }
}""",
    },
    {
        "id": "code_47",
        "source_reference": "study://human-ai/memory/LruTouch",
        "description": "LRU listesinde anahtari one alma",
        "original_code": """package study.memory;

import java.util.ArrayList;
import java.util.List;

public class LruTouch {
    public static void touch(List<String> order, String key, int cap) {
        if (order == null || key == null) return;
        if (cap < 1) cap = 1;
        int idx = -1;
        for (int i = 0; i < order.size(); i++) {
            if (key.equals(order.get(i))) {
                idx = i;
                break;
            }
        }
        if (idx >= 0) order.remove(idx);
        order.add(0, key);
        while (order.size() > cap) {
            order.remove(order.size() - 1);
        }
    }
}""",
    },
    {
        "id": "code_48",
        "source_reference": "study://human-ai/report/WeeklyBuckets",
        "description": "Gunluk degerleri haftalik kovlara toplama",
        "original_code": """package study.report;

public class WeeklyBuckets {
    public static int[] weekly(int[] daily) {
        if (daily == null) return new int[0];
        int weeks = (daily.length + 6) / 7;
        int[] out = new int[weeks];
        for (int i = 0; i < daily.length; i++) {
            int w = i / 7;
            out[w] = out[w] + daily[i];
        }
        return out;
    }
}""",
    },
    {
        "id": "code_49",
        "source_reference": "study://human-ai/ui/Pagination",
        "description": "Sayfalama icin baslangic/bitis indeksi",
        "original_code": """package study.ui;

public class Pagination {
    public static int[] range(int total, int page, int size) {
        if (total < 0) total = 0;
        if (page < 1) page = 1;
        if (size < 1) size = 1;
        int start = (page - 1) * size;
        if (start > total) start = total;
        int end = start + size;
        if (end > total) end = total;
        return new int[] {start, end};
    }
}""",
    },
    {
        "id": "code_50",
        "source_reference": "study://human-ai/notify/Throttle",
        "description": "Bildirim sikligini sinirlama (throttle)",
        "original_code": """package study.notify;

public class Throttle {
    private long last;
    private long gap;

    public Throttle(long gapMs) {
        if (gapMs < 0) gapMs = 0;
        gap = gapMs;
        last = 0;
    }

    public boolean allow(long now) {
        if (now < 0) now = 0;
        if (last == 0 || now - last >= gap) {
            last = now;
            return true;
        }
        return false;
    }
}""",
    },
    {
        "id": "code_51",
        "source_reference": "study://human-ai/sort/InsertionRanks",
        "description": "Sinav puanlarini insertion sort ile artan siralama",
        "original_code": """package study.sort;

public class InsertionRanks {
    public static void sort(int[] arr) {
        if (arr == null) return;
        int n = arr.length;
        for (int i = 1; i < n; i++) {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0) {
                if (arr[j] <= key) {
                    break;
                }
                arr[j + 1] = arr[j];
                j = j - 1;
            }
            arr[j + 1] = key;
        }
    }

    public static boolean isSorted(int[] arr) {
        if (arr == null || arr.length < 2) return true;
        for (int k = 1; k < arr.length; k++) {
            if (arr[k - 1] > arr[k]) return false;
        }
        return true;
    }
}""",
    },
    {
        "id": "code_52",
        "source_reference": "study://human-ai/tree/LeafCounter",
        "description": "Ikili agacta yaprak dugum sayisini sayma",
        "original_code": """package study.tree;

public class LeafCounter {
    public static class Node {
        public int val;
        public Node left;
        public Node right;

        public Node(int val, Node left, Node right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }

    public static int count(Node root) {
        if (root == null) return 0;
        if (root.left == null && root.right == null) {
            return 1;
        }
        int c = 0;
        if (root.left != null) {
            c = c + count(root.left);
        }
        if (root.right != null) {
            c = c + count(root.right);
        }
        return c;
    }
}""",
    },
]
