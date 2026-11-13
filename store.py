import os
import sqlite3
from flask import Flask, flash, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.secret_key = "dz_platform_secret_key"
DB_NAME = "store_platform_v2.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT UNIQUE,
            owner_name TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            title TEXT,
            price REAL,
            stock INTEGER,
            image_url TEXT,
            FOREIGN KEY(vendor_id) REFERENCES vendors(id)
        )
    """)
  conn.commit()
  conn.close()


init_db()

# --- واجهة المنصة المطورة (V2) ---
MAIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DZ.PLATFORM PRO | منصة المتاجر الذكية</title>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #090d16; --card: rgba(30, 41, 59, 0.8); --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
    body { background: var(--bg); color: var(--text); min-height: 100vh; padding: 2rem 5%; }
    
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .logo { font-size: 1.8rem; font-weight: 800; background: linear-gradient(45deg, #818cf8, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    /* بطاقات الإحصائيات السريعة */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
    .stat-card { background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9)); border: 1px solid rgba(99,102,241,0.3); padding: 1.5rem; border-radius: 16px; text-align: center; }
    .stat-card h4 { color: var(--muted); font-size: 0.9rem; margin-bottom: 0.5rem; }
    .stat-card .num { font-size: 1.8rem; font-weight: 800; color: #38bdf8; }

    .grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 2rem; }
    @media(max-width: 850px) { .grid { grid-template-columns: 1fr; } }
    
    .box { background: var(--card); border: 1px solid rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(12px); }
    h2 { margin-bottom: 1.2rem; color: #818cf8; font-size: 1.3rem; }
    
    .form-group { margin-bottom: 1rem; }
    label { display: block; color: var(--muted); margin-bottom: 0.3rem; font-size: 0.85rem; }
    input, select { width: 100%; padding: 0.75rem; background: #0f172a; border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; color: #fff; font-size: 0.95rem; outline: none; }
    input:focus, select:focus { border-color: var(--accent); }
    
    .btn { background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; padding: 0.85rem; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; transition: 0.2s; font-size: 1rem; }
    .btn:hover { opacity: 0.9; transform: translateY(-2px); }

    table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: #0f172a; border-radius: 12px; overflow: hidden; }
    th, td { padding: 0.9rem; text-align: right; border-bottom: 1px solid #1e293b; font-size: 0.9rem; vertical-align: middle; }
    th { background: #1e293b; color: #38bdf8; }
    
    .prod-img { width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); }
    .action-btn { padding: 0.4rem 0.8rem; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-left: 0.3rem; }
    .edit-btn { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }
    .del-btn { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #f87171; }
    
    .alert { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #6ee7b7; padding: 0.9rem; border-radius: 10px; margin-bottom: 1.5rem; font-weight: 600; }
  </style>
</head>
<body>

  <header>
    <div class="logo">DZ.PLATFORM PRO 💎</div>
    <div style="color: var(--muted); font-size: 0.9rem;">نظام إدارة المتاجر والسلع المتكامل</div>
  </header>

  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <div class="alert">{{ messages[0] }}</div>
    {% endif %}
  {% endwith %}

  <!-- بطاقات الإحصائيات العامة -->
  <div class="stats-grid">
    <div class="stat-card">
      <h4>إجمالي المتاجر المسجلة</h4>
      <div class="num">{{ vendors|length }}</div>
    </div>
    <div class="stat-card">
      <h4>عدد المنتجات المعروضة</h4>
      <div class="num">{{ products|length }}</div>
    </div>
    <div class="stat-card">
      <h4>القيمة الإجمالية للمخزون</h4>
      <div class="num">{{ "{:,.0f}".format(total_inventory_value) }} د.ج</div>
    </div>
  </div>

  <div class="grid">
    <!-- تسجيل متجر -->
    <div class="box">
      <h2>1. إنشاء متجر جديد</h2>
      <form method="POST" action="/add_vendor">
        <div class="form-group">
          <label>اسم المتجر</label>
          <input type="text" name="store_name" placeholder="مثال: متجر الأناقة" required>
        </div>
        <div class="form-group">
          <label>اسم التاجر</label>
          <input type="text" name="owner_name" placeholder="مثال: كريم" required>
        </div>
        <button type="submit" class="btn">تسجيل المتجر +</button>
      </form>
    </div>

    <!-- إضافة منتج -->
    <div class="box">
      <h2>2. إضافة سلعة جديدة مع صورتها</h2>
      <form method="POST" action="/add_product">
        <div class="form-group">
          <label>المتجر التابع له</label>
          <select name="vendor_id" required>
            {% for v in vendors %}
              <option value="{{ v[0] }}">{{ v[1] }} ({{ v[2] }})</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label>اسم المنتج</label>
          <input type="text" name="title" placeholder="مثال: سماعات لاسلكية Pro" required>
        </div>
        <div class="form-group">
          <label>رابط صورة المنتج (اختياري)</label>
          <input type="url" name="image_url" placeholder="https://example.com/image.jpg">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label>السعر (د.ج)</label>
            <input type="number" name="price" placeholder="3200" required>
          </div>
          <div class="form-group">
            <label>الكمية في المخزن</label>
            <input type="number" name="stock" placeholder="15" required>
          </div>
        </div>
        <button type="submit" class="btn">حفظ ونشر المنتج 🚀</button>
      </form>
    </div>
  </div>

  <!-- جدول المنتجات وإدارتها -->
  <div class="box" style="margin-top: 2rem; overflow-x: auto;">
    <h2>📦 إدارة المخزون والسلع المعروضة</h2>
    <table>
      <thead>
        <tr>
          <th>الصورة</th>
          <th>المتجر</th>
          <th>المنتج</th>
          <th>السعر</th>
          <th>المخزون</th>
          <th>القيمة الإجمالية</th>
          <th>التحكم</th>
        </tr>
      </thead>
      <tbody>
        {% for p in products %}
        <tr>
          <td>
            <img src="{{ p[6] if p[6] else 'https://via.placeholder.com/50/1e293b/818cf8?text=Box' }}" class="prod-img" alt="صورة">
          </td>
          <td><b>{{ p[1] }}</b><br><small style="color:var(--muted)">{{ p[2] }}</small></td>
          <td>{{ p[3] }}</td>
          <td>{{ "{:,.0f}".format(p[4]) }} د.ج</td>
          <td>{{ p[5] }} قطعة</td>
          <td style="color: #38bdf8; font-weight: bold;">{{ "{:,.0f}".format(p[4] * p[5]) }} د.ج</td>
          <td>
            <a href="/edit/{{ p[0] }}" class="action-btn edit-btn">تعديل ✏️</a>
            <a href="/delete/{{ p[0] }}" class="action-btn del-btn" onclick="return confirm('هل أنت متأكد من حذف هذا المنتج؟')">حذف 🗑️</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

</body>
</html>
"""

# --- صفحة تعديل المنتج ---
EDIT_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>تعديل المنتج</title>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body { background: #090d16; color: #f8fafc; font-family: 'Cairo', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .box { background: #1e293b; padding: 2.5rem; border-radius: 20px; width: 100%; max-width: 450px; border: 1px solid rgba(255,255,255,0.1); }
    h2 { margin-bottom: 1.5rem; color: #38bdf8; }
    label { display: block; margin-bottom: 0.4rem; color: #94a3b8; font-size: 0.9rem; }
    input { width: 100%; padding: 0.8rem; margin-bottom: 1.2rem; background: #0f172a; border: 1px solid #334155; border-radius: 10px; color: #fff; }
    button { width: 100%; padding: 0.9rem; background: #6366f1; color: #fff; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
    a { display: block; text-align: center; margin-top: 1rem; color: #94a3b8; text-decoration: none; }
  </style>
</head>
<body>
  <div class="box">
    <h2>✏️ تعديل بيانات المنتج</h2>
    <form method="POST">
      <label>اسم المنتج</label>
      <input type="text" name="title" value="{{ product[2] }}" required>
      <label>رابط الصورة</label>
      <input type="url" name="image_url" value="{{ product[5] or '' }}">
      <label>السعر (د.ج)</label>
      <input type="number" name="price" value="{{ product[3] }}" required>
      <label>الكمية المتوفرة</label>
      <input type="number" name="stock" value="{{ product[4] }}" required>
      <button type="submit">حفظ التعديلات ✅</button>
    </form>
    <a href="/">إلغاء والعودة</a>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM vendors")
  vendors = cursor.fetchall()

  cursor.execute("""
        SELECT products.id, vendors.store_name, vendors.owner_name, products.title, products.price, products.stock, products.image_url
        FROM products
        JOIN vendors ON products.vendor_id = vendors.id
        ORDER BY products.id DESC
    """)
  products = cursor.fetchall()
  conn.close()

  total_inventory_value = sum(p[4] * p[5] for p in products)
  return render_template_string(
      MAIN_HTML,
      vendors=vendors,
      products=products,
      total_inventory_value=total_inventory_value,
  )


@app.route("/add_vendor", methods=["POST"])
def add_vendor():
  store_name = request.form.get("store_name")
  owner_name = request.form.get("owner_name")
  try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vendors (store_name, owner_name) VALUES (?, ?)",
        (store_name, owner_name),
    )
    conn.commit()
    conn.close()
    flash(f"تم إنشاء المتجر '{store_name}' بنجاح!")
  except sqlite3.IntegrityError:
    flash("⚠️ اسم المتجر مسجل مسبقاً، يرجى اختيار اسم آخر.")
  return redirect(url_for("index"))


@app.route("/add_product", methods=["POST"])
def add_product():
  vendor_id = request.form.get("vendor_id")
  title = request.form.get("title")
  image_url = request.form.get("image_url")
  price = float(request.form.get("price", 0))
  stock = int(request.form.get("stock", 0))

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO products (vendor_id, title, price, stock, image_url) VALUES"
      " (?, ?, ?, ?, ?)",
      (vendor_id, title, price, stock, image_url),
  )
  conn.commit()
  conn.close()
  flash("✅ تمت إضافة المنتج وتحديث حسابات المخزون!")
  return redirect(url_for("index"))


@app.route("/edit/<int:prod_id>", methods=["GET", "POST"])
def edit_product(prod_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  if request.method == "POST":
    title = request.form.get("title")
    image_url = request.form.get("image_url")
    price = float(request.form.get("price", 0))
    stock = int(request.form.get("stock", 0))
    cursor.execute(
        "UPDATE products SET title=?, price=?, stock=?, image_url=? WHERE id=?",
        (title, price, stock, image_url, prod_id),
    )
    conn.commit()
    conn.close()
    flash("✏️ تم تحديث بيانات المنتج بنجاح!")
    return redirect(url_for("index"))

  cursor.execute("SELECT * FROM products WHERE id=?", (prod_id,))
  product = cursor.fetchone()
  conn.close()
  return render_template_string(EDIT_HTML, product=product)


@app.route("/delete/<int:prod_id>")
def delete_product(prod_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
  conn.commit()
  conn.close()
  flash("🗑️ تم حذف المنتج من المخزون.")
  return redirect(url_for("index"))

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
