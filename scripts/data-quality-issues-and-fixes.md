# 🧪 RetailHub — Zaszyte błędy danych i jak je naprawić

Dataset **celowo** zawiera 6 kontrolowanych problemów z jakością danych. Każdy jest seedowany regułą modulo, więc **reprodukuje się tak samo za każdym razem** — i każdy ma swoje zapytanie wykrywające w Dniu 1.

**Cel:** pokazać, że prawdziwe dane nie są czyste — i że zadaniem warstwy **Gold** jest sprawić, by raport Power BI tego nie „zobaczył".

| | |
|---|---|
| 📋 **Inwentarz błędów (6)** | [`08_source_risk_register.sql`](../sql/exploration/08_source_risk_register.sql) |
| 📋 **Rekoncyliacja nagłówek vs linie (#6)** | [`09_header_vs_lines_recon.sql`](../sql/exploration/09_header_vs_lines_recon.sql) |
| 🏭 **Definicje błędów** | `data/generate_training_dataset.ipynb` → sekcja *„2. Orders and controlled quality issues"* |

---

## ⭐ Złota zasada

> **Najpierw discovery (sprawdź ziarno i ryzyka), potem buduj Gold.**
>
> `08_risk_register` → świadoma decyzja (odfiltruj / oznacz / Unknown member) → zapisz w kontrakcie BI → zwaliduj (KPI smoke test, `duplicate keys = 0`).

---

## 📊 Przegląd: 6 błędów na jednej tabeli

| # | Błąd | Lokalizacja | Reguła | Wzorzec naprawczy |
|:-:|---|---|---|---|
| 1 | Data z przyszłości | `sales_orders.order_date` | `order_id % 997` | flaga `is_future_dated` |
| 2 | Status spoza słownika | `sales_orders.status` | `order_id % 101` → `'Unknown'` | `CASE WHEN status='Completed'` |
| 3 | Brak ceny | `order_lines.unit_price` | `line_id % 1543` → `NULL` | `coalesce` miar do 0 |
| 4 | Sierocy klient | `order_lines.customer_id` | `line_id % 4001` | Unknown member w `dim_customer` |
| 5 | Sierocy produkt | `order_lines.product_id` | `line_id % 3001` | Unknown member w `dim_product` |
| 6 | Rozjazd nagłówek/linie | `sales_orders.order_total_amount` | `order_id % 401` | Revenue liczony z linii |

> ⚠️ Osobno: **znany quirk źródła** — potrojone/zduplikowane linie (`order_lines`). Nie jest liczony jako błąd, bo ziarno `fact_sales` to `line_id` (unikalne) i nie da się go zdeduplikować po kluczu biznesowym. Szczegóły na końcu.

---

## 🧹 Kto sprząta co — macierz czyszczenia per tabela Gold

**Zasada:** błędy żyją w `silver`. Każda tabela Gold, budując się z warstwy Silver, **musi usunąć/obsłużyć błędy, które jej dotyczą** — zanim trafi do Power BI.

| Tabela Gold | Czyta z | Błędy do obsłużenia | Co konkretnie zrobić |
|---|---|---|---|
| `dim_date` | `sequence()` | *(brak — generowana)* | tylko zapewnij unikalny `date_key` |
| `dim_customer` | `silver.customers` (+ sieroty) | **#4** sierocy klient | Unknown member (`LEFT ANTI JOIN`); unikalny `customer_id` |
| `dim_product` | `silver.products` (+ sieroty) | **#5** sierocy produkt | Unknown member; unikalny `product_id` |
| `fact_sales` | `silver.order_lines` | **#1 #2 #3 #6** | flagi statusu (`is_completed`…); `coalesce` NULL price/miar; flaga `is_future_dated`; revenue tylko z `line_revenue` |
| `fact_sales_dashboard` | `fact_sales` + wymiary | **#4 #5 #2** | `COALESCE(..., 'Unknown')` po JOIN; flagi statusu |
| `kpi_daily` / `revenue_monthly` | `fact_sales` | **#2 #1** | filtr `status='Completed'`; pomiń `is_future_dated` |

> 💡 **Najwięcej pracy jest w `fact_sales`** — to jedyna tabela czytająca brudne `order_lines`, więc ląduje tam 4 z 6 błędów. Wymiary obsługują tylko swoje sieroty, a agregaty dziedziczą już czysty fakt.

---

# 🔧 Szczegóły — błąd po błędzie

---

## 1️⃣ Data z przyszłości

**Gdzie:** `silver.sales_orders.order_date` &nbsp;·&nbsp; **Reguła:** `order_id % 997 = 0` (data = `current_date() + 30`)
**Co psuje:** oś czasu i trendy — pojawia się „sprzedaż w przyszłości".

🔍 **Wykryj**
```sql
SELECT COUNT(*) FROM silver.sales_orders WHERE order_date > current_date();
```

🔧 **Napraw** — oznacz flagą (zostaw wiersz):
```sql
CASE WHEN order_date > current_date() THEN true ELSE false END AS is_future_dated
```
> 📝 W kontrakcie BI: *„KPI mogą wykluczać `is_future_dated`"*.

---

## 2️⃣ Status spoza słownika

**Gdzie:** `silver.sales_orders.status` &nbsp;·&nbsp; **Reguła:** `order_id % 101 = 0 → 'Unknown'`
**Słownik docelowy:** `Completed` · `Returned` · `Cancelled`
**Co psuje:** liczniki Completed/Returned, sumy revenue.

🔍 **Wykryj**
```sql
SELECT status, COUNT(*) FROM silver.sales_orders
WHERE status NOT IN ('Completed','Returned','Cancelled')
GROUP BY status;
```

🔧 **Napraw** — flagi statusu + licz miary jawnie po fladze:
```sql
SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue
```
> ⚠️ **Nigdy** nie licz `SUM(line_revenue)` bez filtra statusu — `'Unknown'` wpadnie do wyniku.

---

## 3️⃣ Brak ceny jednostkowej

**Gdzie:** `silver.order_lines.unit_price` &nbsp;·&nbsp; **Reguła:** `line_id % 1543 = 0 → NULL` (przez co `line_revenue`/`line_margin` też NULL)
**Co psuje:** sumy revenue zaniżone lub `NULL`.

🔍 **Wykryj**
```sql
SELECT COUNT(*) FROM silver.order_lines WHERE unit_price IS NULL;
```

🔧 **Napraw** — `coalesce` miar do 0 (zostaw wiersz):
```sql
coalesce(unit_price, 0), coalesce(line_revenue, 0), coalesce(line_margin, 0)
```
> ⚠️ Nie zostawiaj `NULL` „w locie". Gold ma mieć komplet niezerowych miar.

---

## 4️⃣ Sierocy `customer_id` (brak w `customers`)

**Gdzie:** `silver.order_lines.customer_id` &nbsp;·&nbsp; **Reguła:** `line_id % 4001 = 0`
**Co psuje:** zerwana relacja do `dim_customer` — przy `INNER JOIN` wiersze znikają.

🔍 **Wykryj** (`LEFT ANTI JOIN`)
```sql
SELECT COUNT(*) FROM silver.order_lines l
LEFT ANTI JOIN silver.customers c ON l.customer_id = c.customer_id;
```

🔧 **Napraw** — wzorzec **„Unknown member"** (Kimball): dorzuć zastępcze wiersze do wymiaru (tak robi `gold.dim_customer`):
```sql
SELECT DISTINCT
  ol.customer_id,
  'Unknown' AS customer_name, 'Unknown' AS city,
  'Unknown' AS customer_region, 'Unknown' AS country,
  'Unknown' AS segment, NULL AS created_date
FROM silver.order_lines ol
LEFT ANTI JOIN silver.customers c ON ol.customer_id = c.customer_id
WHERE ol.customer_id IS NOT NULL
```
> ✅ Efekt: relacja `fact → dim_customer` jest **pełna**, a osierocone transakcje grupują się pod „Unknown" zamiast znikać.

---

## 5️⃣ Sierocy `product_id` (brak w `products`)

**Gdzie:** `silver.order_lines.product_id` &nbsp;·&nbsp; **Reguła:** `line_id % 3001 = 0`
**Co psuje:** zerwana relacja do `dim_product`.

🔍 **Wykryj**
```sql
SELECT COUNT(*) FROM silver.order_lines l
LEFT ANTI JOIN silver.products p ON l.product_id = p.product_id;
```

🔧 **Napraw** — ten sam wzorzec **„Unknown member"** co przy kliencie (👆 pkt 4), tylko dla `dim_product`.

---

## 6️⃣ Rozjazd: suma nagłówka vs suma linii

**Gdzie:** `silver.sales_orders.order_total_amount` vs `SUM(order_lines.line_revenue)` &nbsp;·&nbsp; **Reguła:** `order_id % 401 = 0`
**Co psuje:** dwie różne „prawdy" o wartości zamówienia.

🔍 **Wykryj** (rekoncyliacja)
```sql
WITH line_totals AS (
  SELECT order_id, ROUND(SUM(line_revenue),2) AS line_revenue_total
  FROM silver.order_lines GROUP BY order_id
)
SELECT o.order_id, o.order_total_amount, l.line_revenue_total,
       ROUND(o.order_total_amount - l.line_revenue_total, 2) AS amount_diff
FROM silver.sales_orders o JOIN line_totals l ON o.order_id = l.order_id
WHERE ABS(ROUND(o.order_total_amount - l.line_revenue_total, 2)) > 0.01
ORDER BY ABS(amount_diff) DESC;
```

🔧 **Napraw** — wybierz **jedno** źródło prawdy:
> 💡 **Revenue zawsze z linii** (`line_revenue`), nigdy z nagłówka. `order_total_amount` traktuj jako kontrolę rekoncyliacyjną, nie jako miarę raportową.

---

## ⚙️ Quirk źródła (NIE błąd) — potrojone / zduplikowane linie

**Gdzie:** `silver.order_lines` &nbsp;·&nbsp; **Reguła:** `line_id % 10007 = 0` (re-insert z `line_id + 10000000`)

🔎 **Dlaczego to NIE jest jeden z 6 błędów:**
- Generator z założenia tworzy **3 identyczne linie na każde zamówienie** (ten sam `product_id`, ta sama `quantity`). Czyli `(order_id, product_id)` występuje **3× naturalnie** — **nie jest kluczem**.
- `COUNT(*) - COUNT(DISTINCT (order_id, product_id))` = ~240 000 (naturalne), a zaszyty re-insert to ~36 dodatkowych wierszy — nieodróżnialnych od potrojenia.
- Brak zapytania wykrywającego w Dniu 1 (`08`/`09` go nie liczą).

🔧 **Decyzja modelowa:** ziarno `fact_sales` to **`line_id`** i jest **unikalne** (też dla re-insertu), więc to formalnie poprawna linia. **Nie deduplikujemy** — dedup po `(order_id, product_id)` obciąłby revenue do ~1/3 i usunął legalne dane.
> 📝 W kontrakcie BI: *„fact_sales ma ziarno `line_id`; źródłowe potrojenie linii i zaszyty re-insert są znane i pozostają w danych"*.
