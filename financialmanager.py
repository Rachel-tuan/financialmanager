import tkinter as tk
from tkinter import messagebox, ttk, font,filedialog, simpledialog
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from decimal import Decimal, ROUND_HALF_UP
import uuid

matplotlib.use('TkAgg')  # 确保使用正确的后端

CATEGORY_FILE = 'categories.json'
RULES_FILE = 'rules.json'
DATA_FILE = 'records.json'
GOAL_FILE = 'goals.json'
CATEGORY_FILE = 'categories.json'

def _safe_read_json(file_path, default):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, type(default)) else default
    except Exception:
        return default
    return default

def _safe_write_json(file_path, data):
    tmp_path = file_path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, file_path)

def load_data():
    data = _safe_read_json(DATA_FILE, [])
    changed = False
    normalized = []
    for r in data:
        if isinstance(r, dict):
            if not str(r.get('id', '')).strip():
                r['id'] = uuid.uuid4().hex
                changed = True
            normalized.append(r)
    if changed:
        _safe_write_json(DATA_FILE, normalized)
    return normalized

def save_data(data):
    _safe_write_json(DATA_FILE, data)

def load_goals():
    return _safe_read_json(GOAL_FILE, {})

def save_goals(goals):
    _safe_write_json(GOAL_FILE, goals)

def load_categories():
    cats = _safe_read_json(CATEGORY_FILE, [])
    if not isinstance(cats, list):
        cats = []
    cats = [str(c).strip() for c in cats if isinstance(c, str)]
    if '未分类' not in cats:
        cats.append('未分类')
    return sorted(set(cats))

def save_categories(categories):
    cats = [str(c).strip() for c in categories if str(c).strip()]
    _safe_write_json(CATEGORY_FILE, sorted(set(cats)))

def load_rules():
    rules = _safe_read_json(RULES_FILE, [])
    if not isinstance(rules, list):
        rules = []
    cleaned = []
    for r in rules:
        if isinstance(r, dict):
            kw = str(r.get('keyword', '')).strip()
            cat = str(r.get('category', '')).strip()
            if kw and cat:
                cleaned.append({'keyword': kw, 'category': cat})
    return cleaned

def save_rules(rules):
    _safe_write_json(RULES_FILE, rules)

def suggest_tag(note):
    note = (note or '').strip()
    if not note:
        return '未分类'
    for r in load_rules():
        if r['keyword'] and r['keyword'] in note:
            return r['category']
    data = load_data()
    freq = {}
    for r in data:
        n = (r.get('note') or '').strip()
        t = (r.get('tag') or '').strip()
        if n == note and t:
            freq[t] = freq.get(t, 0) + 1
    if freq:
        return max(freq.items(), key=lambda x: x[1])[0]
    return '未分类'

def _is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except Exception:
        return False

def _is_valid_month(month_str):
    try:
        datetime.strptime(month_str, '%Y-%m')
        return True
    except Exception:
        return False

def open_add_record_window():
    # 创建新窗口
    add_window = tk.Toplevel(root)
    add_window.title('添加账单')
    add_window.geometry('400x300')
    add_window.configure(bg='#f5f6fa')
    add_window.resizable(False, False)
    add_window.transient(root)  # 设置为主窗口的子窗口
    add_window.grab_set()  # 模态窗口
    
    # 设置窗口样式
    title_label = tk.Label(add_window, text='添加新账单', font=('微软雅黑', 16, 'bold'), bg='#f5f6fa', fg='#273c75')
    title_label.pack(pady=10)
    
    # 创建表单框架
    form_frame = tk.Frame(add_window, bg='#f5f6fa')
    form_frame.pack(pady=5, fill='both', expand=True)
    
    # 日期输入
    date_frame = tk.Frame(form_frame, bg='#f5f6fa')
    date_frame.pack(fill='x', pady=5)
    date_label = tk.Label(date_frame, text='日期:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    date_label.pack(side='left', padx=5)
    date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    date_entry = tk.Entry(date_frame, textvariable=date_var, font=('微软雅黑', 12), width=20)
    date_entry.pack(side='left', padx=5)
    
    # 类型选择
    type_frame = tk.Frame(form_frame, bg='#f5f6fa')
    type_frame.pack(fill='x', pady=5)
    type_label = tk.Label(type_frame, text='类型:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    type_label.pack(side='left', padx=5)
    type_var = tk.StringVar(value='支出')
    type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=('支出', '收入'), font=('微软雅黑', 12), width=18, state='readonly')
    type_combo.pack(side='left', padx=5)
    
    # 金额输入
    amount_frame = tk.Frame(form_frame, bg='#f5f6fa')
    amount_frame.pack(fill='x', pady=5)
    amount_label = tk.Label(amount_frame, text='金额:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    amount_label.pack(side='left', padx=5)
    amount_var = tk.StringVar()
    amount_entry = tk.Entry(amount_frame, textvariable=amount_var, font=('微软雅黑', 12), width=20)
    amount_entry.pack(side='left', padx=5)
    
    # 用途/备注输入
    note_frame = tk.Frame(form_frame, bg='#f5f6fa')
    note_frame.pack(fill='x', pady=5)
    note_label = tk.Label(note_frame, text='用途/备注:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    note_label.pack(side='left', padx=5)
    note_var = tk.StringVar()
    note_entry = tk.Entry(note_frame, textvariable=note_var, font=('微软雅黑', 12), width=20)
    note_entry.pack(side='left', padx=5)

    tag_frame = tk.Frame(form_frame, bg='#f5f6fa')
    tag_frame.pack(fill='x', pady=5)
    tag_label = tk.Label(tag_frame, text='类别:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    tag_label.pack(side='left', padx=5)
    tag_var = tk.StringVar()
    tag_combo = ttk.Combobox(tag_frame, textvariable=tag_var, values=load_categories(), font=('微软雅黑', 12), width=18, state='normal')
    tag_combo.pack(side='left', padx=5)

    def _update_tag_suggestion():
        if not (tag_var.get() or '').strip():
            tag_var.set(suggest_tag(note_var.get()))
    note_var.trace_add('write', lambda *a: _update_tag_suggestion())
    
    # 按钮框架
    btn_frame = tk.Frame(add_window, bg='#f5f6fa')
    btn_frame.pack(pady=10)
    
    # 保存按钮
    def save_record():
        try:
            date = date_var.get()
            category = type_var.get()
            amount_str = amount_var.get().strip()
            note = note_var.get().strip()

            if not amount_str or not category:
                messagebox.showwarning('提示', '类型和金额不能为空！', parent=add_window)
                return
            if not _is_valid_date(date):
                messagebox.showwarning('提示', '日期格式需为 YYYY-MM-DD！', parent=add_window)
                return
                
            try:
                amount_dec = Decimal(amount_str)
            except ValueError:
                messagebox.showwarning('提示', '金额必须是数字！', parent=add_window)
                return
            
            if amount_dec <= 0:
                messagebox.showwarning('提示', '金额必须为正数！', parent=add_window)
                return
            
            amount_dec = abs(amount_dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            amount = float(amount_dec)
            
            tag = (tag_var.get() or '').strip()
            if not tag:
                tag = suggest_tag(note)
            record = {'date': date, 'category': category, 'tag': tag, 'amount': amount, 'note': note}
            data = load_data()
            data.append(record)
            save_data(data)
            cats = load_categories()
            if tag and tag != '未分类' and tag not in cats:
                cats.append(tag)
                save_categories(cats)
            
            messagebox.showinfo('成功', '账单已添加！', parent=add_window)
            update_summary()
            update_table()
            update_chart()
            add_window.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {str(e)}', parent=add_window)
    
    save_btn = tk.Button(btn_frame, text='保存', width=10, font=('微软雅黑', 12), bg='#00b894', fg='white', command=save_record, relief='flat')
    save_btn.pack(side='left', padx=10)
    
    # 取消按钮
    cancel_btn = tk.Button(btn_frame, text='取消', width=10, font=('微软雅黑', 12), bg='#d63031', fg='white', command=add_window.destroy, relief='flat')
    cancel_btn.pack(side='left', padx=10)
    
    # 设置初始焦点
    date_entry.focus_set()

def open_set_goal_window():
    # 创建新窗口
    goal_window = tk.Toplevel(root)
    goal_window.title('设置月度目标')
    goal_window.geometry('400x200')
    goal_window.configure(bg='#f5f6fa')
    goal_window.resizable(False, False)
    goal_window.transient(root)  # 设置为主窗口的子窗口
    goal_window.grab_set()  # 模态窗口
    
    # 设置窗口样式
    title_label = tk.Label(goal_window, text='设置月度支出目标', font=('微软雅黑', 16, 'bold'), bg='#f5f6fa', fg='#273c75')
    title_label.pack(pady=10)
    
    # 创建表单框架
    form_frame = tk.Frame(goal_window, bg='#f5f6fa')
    form_frame.pack(pady=5, fill='both', expand=True)
    
    # 月份输入
    month_frame = tk.Frame(form_frame, bg='#f5f6fa')
    month_frame.pack(fill='x', pady=5)
    month_label = tk.Label(month_frame, text='月份:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    month_label.pack(side='left', padx=5)
    month_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
    month_entry = tk.Entry(month_frame, textvariable=month_var, font=('微软雅黑', 12), width=20)
    month_entry.pack(side='left', padx=5)
    
    # 目标金额输入
    amount_frame = tk.Frame(form_frame, bg='#f5f6fa')
    amount_frame.pack(fill='x', pady=5)
    amount_label = tk.Label(amount_frame, text='目标金额:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    amount_label.pack(side='left', padx=5)
    amount_var = tk.StringVar()
    amount_entry = tk.Entry(amount_frame, textvariable=amount_var, font=('微软雅黑', 12), width=20)
    amount_entry.pack(side='left', padx=5)
    
    # 按钮框架
    btn_frame = tk.Frame(goal_window, bg='#f5f6fa')
    btn_frame.pack(pady=10)
    
    # 保存按钮
    def save_goal():
        try:
            month = month_var.get().strip()
            amount_str = amount_var.get().strip()
            
            if not month or not amount_str:
                messagebox.showwarning('提示', '月份和目标金额不能为空！', parent=goal_window)
                return
                
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showwarning('提示', '目标金额必须是数字！', parent=goal_window)
                return
            
            if amount <= 0:
                messagebox.showwarning('提示', '目标金额必须为正数！', parent=goal_window)
                return
            
            goals = load_goals()
            goals[month] = amount
            save_goals(goals)
            
            messagebox.showinfo('成功', f'{month} 月支出目标已设置为 {amount:.2f}！', parent=goal_window)
            update_summary()
            update_table()
            update_chart()
            goal_window.destroy()
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {str(e)}', parent=goal_window)
    
    save_btn = tk.Button(btn_frame, text='保存', width=10, font=('微软雅黑', 12), bg='#00b894', fg='white', command=save_goal, relief='flat')
    save_btn.pack(side='left', padx=10)
    
    # 取消按钮
    cancel_btn = tk.Button(btn_frame, text='取消', width=10, font=('微软雅黑', 12), bg='#d63031', fg='white', command=goal_window.destroy, relief='flat')
    cancel_btn.pack(side='left', padx=10)
    
    # 设置初始焦点
    month_entry.focus_set()

def update_summary():
    month = selected_month.get().strip()
    if not month:
        month = datetime.now().strftime('%Y-%m')
        selected_month.set(month)
    elif not _is_valid_month(month):
        messagebox.showwarning('提示', '月份格式需为 YYYY-MM！')
        return
    
    data = load_data()
    income = sum((Decimal(str(r['amount'])) for r in data if r['category'] == '收入' and r['date'].startswith(month)), Decimal('0'))
    expense = sum((Decimal(str(r['amount'])) for r in data if r['category'] == '支出' and r['date'].startswith(month)), Decimal('0'))
    balance = income - expense
    goals = load_goals()
    goal = goals.get(month, None)
    
    # 格式化摘要信息
    summary = f"当前月份: {month}\n\n"
    summary += f"本月收入: {income.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n"
    summary += f"本月支出: {expense.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n"
    summary += f"当前结余: {balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n\n"
    
    if goal is not None:
        goal_dec = Decimal(str(goal))
        remaining = goal_dec - expense
        status = "达标" if remaining >= 0 else "超支"
        summary += f"本月目标: {goal_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n"
        summary += f"剩余额度: {remaining.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n"
        summary += f"状态: {status}"
    else:
        summary += "本月未设置支出目标\n"
        summary += "请点击'设置月目标'按钮"
    
    summary_var.set(summary)

def show_month_summary_ui():
    # 创建新窗口
    summary_window = tk.Toplevel(root)
    summary_window.title('月度统计')
    summary_window.geometry('400x300')
    summary_window.configure(bg='#f5f6fa')
    summary_window.resizable(False, False)
    summary_window.transient(root)  # 设置为主窗口的子窗口
    summary_window.grab_set()  # 模态窗口
    
    # 设置窗口样式
    title_label = tk.Label(summary_window, text='月度收支统计', font=('微软雅黑', 16, 'bold'), bg='#f5f6fa', fg='#273c75')
    title_label.pack(pady=10)
    
    # 创建表单框架
    form_frame = tk.Frame(summary_window, bg='#f5f6fa')
    form_frame.pack(pady=5, fill='x')
    
    # 月份输入
    month_frame = tk.Frame(form_frame, bg='#f5f6fa')
    month_frame.pack(fill='x', pady=5)
    month_label = tk.Label(month_frame, text='月份:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa')
    month_label.pack(side='left', padx=5)
    month_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
    month_entry = tk.Entry(month_frame, textvariable=month_var, font=('微软雅黑', 12), width=15)
    month_entry.pack(side='left', padx=5)
    
    # 结果显示框架
    result_frame = tk.Frame(summary_window, bg='#f5f6fa')
    result_frame.pack(pady=10, fill='both', expand=True)
    
    # 结果文本框
    result_text = tk.Text(result_frame, font=('微软雅黑', 12), width=35, height=8, bg='white', relief='flat')
    result_text.pack(padx=20, pady=5, fill='both', expand=True)
    
    # 查询按钮
    def query_summary():
        month = month_var.get().strip()
        if not month:
            month = datetime.now().strftime('%Y-%m')
        elif not _is_valid_month(month):
            messagebox.showwarning('提示', '月份格式需为 YYYY-MM！', parent=summary_window)
            return
            
        data = load_data()
        income = sum((Decimal(str(r['amount'])) for r in data if r['category'] == '收入' and r['date'].startswith(month)), Decimal('0'))
        expense = sum((Decimal(str(r['amount'])) for r in data if r['category'] == '支出' and r['date'].startswith(month)), Decimal('0'))
        goals = load_goals()
        goal = goals.get(month, None)
        
        result_text.delete(1.0, tk.END)
        
        result_text.insert(tk.END, f"月份: {month}\n\n")
        result_text.insert(tk.END, f"总收入: {income.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n")
        result_text.insert(tk.END, f"总支出: {expense.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n")
        result_text.insert(tk.END, f"结余: {(income - expense).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n\n")
        
        if goal is not None:
            goal_dec = Decimal(str(goal))
            remaining = goal_dec - expense
            status = "达标" if remaining >= 0 else "超支"
            result_text.insert(tk.END, f"本月目标: {goal_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元\n")
            result_text.insert(tk.END, f"剩余额度: {remaining.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} 元 ({status})")
        else:
            result_text.insert(tk.END, "本月未设置支出目标")
            
        result_text.config(state='disabled')
    
    # 按钮框架
    btn_frame = tk.Frame(summary_window, bg='#f5f6fa')
    btn_frame.pack(pady=10)
    
    query_btn = tk.Button(btn_frame, text='查询', width=10, font=('微软雅黑', 12), bg='#00b894', fg='white', command=query_summary, relief='flat')
    query_btn.pack(side='left', padx=10)
    
    close_btn = tk.Button(btn_frame, text='关闭', width=10, font=('微软雅黑', 12), bg='#d63031', fg='white', command=summary_window.destroy, relief='flat')
    close_btn.pack(side='left', padx=10)
    
    # 初始查询
    query_summary()
    
    # 设置初始焦点
    month_entry.focus_set()

def open_category_manager_window():
    win = tk.Toplevel(root)
    win.title('类别与规则管理')
    win.geometry('700x420')
    win.configure(bg='#f5f6fa')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    left = tk.LabelFrame(win, text='类别', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
    left.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    right = tk.LabelFrame(win, text='关键词规则', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
    right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

    cat_list = tk.Listbox(left, font=normal_font, height=10)
    cat_list.pack(fill='both', expand=True)

    def refresh_cats():
        cat_list.delete(0, tk.END)
        for c in load_categories():
            cat_list.insert(tk.END, c)

    add_cat_frame = tk.Frame(left, bg='#f5f6fa')
    add_cat_frame.pack(fill='x', pady=5)
    new_cat_var = tk.StringVar()
    new_cat_entry = tk.Entry(add_cat_frame, textvariable=new_cat_var, font=normal_font)
    new_cat_entry.pack(side='left', padx=5)
    def add_cat():
        name = new_cat_var.get().strip()
        if not name:
            return
        cats = load_categories()
        if name not in cats:
            cats.append(name)
            save_categories(cats)
            refresh_cats()
            new_cat_var.set('')
    tk.Button(add_cat_frame, text='新增', font=normal_font, bg='#00b894', fg='white', relief='flat', command=add_cat).pack(side='left', padx=5)

    def rename_cat():
        sel = cat_list.curselection()
        if not sel:
            return
        old = cat_list.get(sel[0])
        if old == '未分类':
            return
        new = simpledialog.askstring('重命名类别', '新的类别名称：', parent=win)
        if not new:
            return
        new = new.strip()
        if not new:
            return
        cats = load_categories()
        if new in cats:
            return
        cats = [new if c == old else c for c in cats]
        save_categories(cats)
        data = load_data()
        for r in data:
            if (r.get('tag') or '') == old:
                r['tag'] = new
        save_data(data)
        rules = load_rules()
        for rr in rules:
            if rr['category'] == old:
                rr['category'] = new
        save_rules(rules)
        refresh_cats()

    def delete_cat():
        sel = cat_list.curselection()
        if not sel:
            return
        name = cat_list.get(sel[0])
        if name == '未分类':
            return
        if not messagebox.askyesno('确认', f'删除类别 {name} 并将相关记录设为未分类？', parent=win):
            return
        data = load_data()
        for r in data:
            if (r.get('tag') or '') == name:
                r['tag'] = '未分类'
        save_data(data)
        rules = [rr for rr in load_rules() if rr['category'] != name]
        save_rules(rules)
        cats = [c for c in load_categories() if c != name]
        save_categories(cats)
        refresh_cats()

    op_frame = tk.Frame(left, bg='#f5f6fa')
    op_frame.pack(fill='x', pady=5)
    tk.Button(op_frame, text='重命名', font=normal_font, bg='#fdcb6e', fg='#2d3436', relief='flat', command=rename_cat).pack(side='left', padx=5)
    tk.Button(op_frame, text='删除', font=normal_font, bg='#d63031', fg='white', relief='flat', command=delete_cat).pack(side='left', padx=5)

    rules_cols = ('关键词', '类别')
    rules_tree = ttk.Treeview(right, columns=rules_cols, show='headings', height=10)
    rules_tree.heading('关键词', text='关键词')
    rules_tree.heading('类别', text='类别')
    rules_tree.column('关键词', width=180)
    rules_tree.column('类别', width=120)
    rules_tree.pack(fill='both', expand=True)

    def refresh_rules():
        for i in rules_tree.get_children():
            rules_tree.delete(i)
        for rr in load_rules():
            rules_tree.insert('', 'end', values=(rr['keyword'], rr['category']))

    add_rule_frame = tk.Frame(right, bg='#f5f6fa')
    add_rule_frame.pack(fill='x', pady=5)
    kw_var = tk.StringVar()
    kw_entry = tk.Entry(add_rule_frame, textvariable=kw_var, font=normal_font, width=20)
    kw_entry.pack(side='left', padx=5)
    cat_var2 = tk.StringVar()
    cat_combo2 = ttk.Combobox(add_rule_frame, textvariable=cat_var2, values=load_categories(), font=normal_font, width=18, state='normal')
    cat_combo2.pack(side='left', padx=5)
    def add_rule():
        kw = kw_var.get().strip()
        cat = cat_var2.get().strip() or '未分类'
        if not kw:
            return
        rules = load_rules()
        rules.append({'keyword': kw, 'category': cat})
        save_rules(rules)
        if cat not in load_categories():
            cats = load_categories()
            cats.append(cat)
            save_categories(cats)
        kw_var.set('')
        refresh_rules()
        cat_combo2.config(values=load_categories())
    tk.Button(add_rule_frame, text='新增规则', font=normal_font, bg='#00b894', fg='white', relief='flat', command=add_rule).pack(side='left', padx=5)

    def delete_rule():
        sel = rules_tree.selection()
        if not sel:
            return
        vals = rules_tree.item(sel[0], 'values')
        kw = vals[0]
        cat = vals[1]
        rules = [rr for rr in load_rules() if not (rr['keyword'] == kw and rr['category'] == cat)]
        save_rules(rules)
        refresh_rules()
    tk.Button(add_rule_frame, text='删除规则', font=normal_font, bg='#d63031', fg='white', relief='flat', command=delete_rule).pack(side='left', padx=5)

    refresh_cats()
    refresh_rules()
    def _apply_rules():
        changed = apply_rules_to_all_records()
        if changed:
            update_table()
            update_chart()
            messagebox.showinfo('完成', '已应用规则到历史记录')
        else:
            messagebox.showinfo('提示', '当前无可应用的规则或记录')
    tk.Button(right, text='应用规则到历史记录', font=normal_font, bg='#fdcb6e', fg='#2d3436', relief='flat', command=_apply_rules).pack(fill='x', pady=5)

def update_table():
    # 清空表格
    for row in table.get_children():
        table.delete(row)
        
    # 获取选择的月份
    month = selected_month.get().strip()
    if not month:
        month = datetime.now().strftime('%Y-%m')
        selected_month.set(month)
    elif not _is_valid_month(month):
        messagebox.showwarning('提示', '月份格式需为 YYYY-MM！')
        return
    
    # 加载数据
    data = load_data()
    
    # 过滤当前月份的数据并按日期降序排序
    filtered_data = [r for r in data if r['date'].startswith(month)]
    sorted_data = sorted(filtered_data, key=lambda x: x['date'], reverse=True)
    
    # 填充表格
    for r in sorted_data:
        amount = r['amount']
        if r['category'] == '支出':
            amount_str = f"-{amount:.2f}"
            amount_color = '#d63031'
        else:
            amount_str = f"+{amount:.2f}"
            amount_color = '#00b894'
        tag_val = (r.get('tag') or '').strip() or '未分类'
        item_id = table.insert('', 'end', iid=str(r.get('id')), values=(r['date'], r['category'], tag_val, amount_str, r['note']))
        
        # 设置金额列的颜色
        table.tag_configure(f'amount_{item_id}', foreground=amount_color)
        table.item(item_id, tags=(f'amount_{item_id}',))

def export_chart_png():
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG 文件", "*.png"), ("所有文件", "*.*")],
                                             title="保存图表为 PNG")
    if file_path:
        fig.savefig(file_path, dpi=300, bbox_inches='tight')
        messagebox.showinfo("导出成功", f"图表已成功保存为 PNG 文件：\n{file_path}")

def export_chart_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")],
                                             title="保存图表为 PDF")
    if file_path:
        fig.savefig(file_path, dpi=300, format='pdf', bbox_inches='tight')
        messagebox.showinfo("导出成功", f"图表已成功保存为 PDF 文件：\n{file_path}")


def get_selected_record_id():
    sel = table.selection()
    if not sel:
        return None
    return sel[0]

def open_edit_record_window():
    rec_id = get_selected_record_id()
    if not rec_id:
        messagebox.showwarning('提示', '请先在表格中选择一条记录')
        return
    data = load_data()
    target = None
    for r in data:
        if str(r.get('id')) == rec_id:
            target = r
            break
    if not target:
        messagebox.showerror('错误', '未找到选中记录')
        return
    win = tk.Toplevel(root)
    win.title('编辑记录')
    win.geometry('420x320')
    win.configure(bg='#f5f6fa')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    form = tk.Frame(win, bg='#f5f6fa')
    form.pack(pady=10, fill='both', expand=True)

    date_var = tk.StringVar(value=target.get('date'))
    type_var = tk.StringVar(value=target.get('category'))
    amount_var = tk.StringVar(value=f"{float(target.get('amount', 0)):.2f}")
    note_var = tk.StringVar(value=target.get('note', ''))
    tag_var = tk.StringVar(value=target.get('tag', ''))

    tk.Label(form, text='日期:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa').grid(row=0, column=0, padx=5, pady=5)
    tk.Entry(form, textvariable=date_var, font=('微软雅黑', 12), width=20).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(form, text='类型:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa').grid(row=1, column=0, padx=5, pady=5)
    ttk.Combobox(form, textvariable=type_var, values=('支出','收入'), font=('微软雅黑', 12), width=18, state='readonly').grid(row=1, column=1, padx=5, pady=5)
    tk.Label(form, text='金额:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa').grid(row=2, column=0, padx=5, pady=5)
    tk.Entry(form, textvariable=amount_var, font=('微软雅黑', 12), width=20).grid(row=2, column=1, padx=5, pady=5)
    tk.Label(form, text='用途/备注:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa').grid(row=3, column=0, padx=5, pady=5)
    tk.Entry(form, textvariable=note_var, font=('微软雅黑', 12), width=20).grid(row=3, column=1, padx=5, pady=5)
    tk.Label(form, text='类别:', width=10, anchor='e', font=('微软雅黑', 12), bg='#f5f6fa').grid(row=4, column=0, padx=5, pady=5)
    ttk.Combobox(form, textvariable=tag_var, values=load_categories(), font=('微软雅黑', 12), width=18, state='normal').grid(row=4, column=1, padx=5, pady=5)

    def save_edit():
        date = date_var.get().strip()
        if not _is_valid_date(date):
            messagebox.showwarning('提示', '日期格式需为 YYYY-MM-DD！', parent=win)
            return
        t = type_var.get().strip()
        amt_str = amount_var.get().strip()
        try:
            amt_dec = Decimal(amt_str)
        except Exception:
            messagebox.showwarning('提示', '金额必须是数字！', parent=win)
            return
        if amt_dec <= 0:
            messagebox.showwarning('提示', '金额必须为正数！', parent=win)
            return
        amt_dec = abs(amt_dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tag = (tag_var.get() or '').strip() or '未分类'
        note = (note_var.get() or '').strip()
        for r in data:
            if str(r.get('id')) == rec_id:
                r['date'] = date
                r['category'] = t
                r['amount'] = float(amt_dec)
                r['note'] = note
                r['tag'] = tag
                break
        save_data(data)
        cats = load_categories()
        if tag and tag not in cats:
            cats.append(tag)
            save_categories(cats)
        update_summary()
        update_table()
        update_chart()
        win.destroy()

    btns = tk.Frame(win, bg='#f5f6fa')
    btns.pack(pady=10)
    tk.Button(btns, text='保存', width=10, font=('微软雅黑', 12), bg='#00b894', fg='white', relief='flat', command=save_edit).pack(side='left', padx=10)
    tk.Button(btns, text='取消', width=10, font=('微软雅黑', 12), bg='#d63031', fg='white', relief='flat', command=win.destroy).pack(side='left', padx=10)

def delete_selected_record():
    rec_id = get_selected_record_id()
    if not rec_id:
        messagebox.showwarning('提示', '请先在表格中选择一条记录')
        return
    if not messagebox.askyesno('确认', '确定删除选中记录？'):
        return
    data = load_data()
    data = [r for r in data if str(r.get('id')) != rec_id]
    save_data(data)
    update_summary()
    update_table()
    update_chart()
root = tk.Tk()
root.title('个人记账管理系统')
root.geometry('1000x700')  # 更大窗口
root.configure(bg='#f5f6fa')  # 柔和背景色
root.resizable(True, True)  # 允许调整窗口大小

# 创建自定义字体
title_font = ('微软雅黑', 18, 'bold')
header_font = ('微软雅黑', 14, 'bold')
normal_font = ('微软雅黑', 12)

# 创建主标题
title_frame = tk.Frame(root, bg='#273c75', height=60)
title_frame.pack(fill='x')
title_label = tk.Label(title_frame, text='个人记账管理系统', font=title_font, bg='#273c75', fg='white')
title_label.pack(pady=10)

# 创建主布局框架
main_frame = tk.Frame(root, bg='#f5f6fa')
main_frame.pack(fill='both', expand=True, padx=20, pady=10)

# 左侧面板 - 包含摘要和按钮
left_panel = tk.Frame(main_frame, bg='#f5f6fa', width=300)
left_panel.pack(side='left', fill='y', padx=(0, 10))
left_panel.pack_propagate(False)  # 防止框架缩小

# 摘要信息
summary_frame = tk.LabelFrame(left_panel, text='本月摘要', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
summary_frame.pack(fill='x', pady=10)

summary_var = tk.StringVar()
summary_label = tk.Label(summary_frame, textvariable=summary_var, justify='left', font=normal_font, bg='#f5f6fa', fg='#273c75')
summary_label.pack(pady=10, anchor='w')

# 按钮区域
btn_frame = tk.LabelFrame(left_panel, text='操作', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
btn_frame.pack(fill='x', pady=10)

# 设置按钮样式
add_btn = tk.Button(btn_frame, text='添加账单', width=14, height=2, font=normal_font, bg='#00b894', fg='white', command=open_add_record_window, relief='flat')
add_btn.pack(fill='x', pady=5)

goal_btn = tk.Button(btn_frame, text='设置月目标', width=14, height=2, font=normal_font, bg='#0984e3', fg='white', command=open_set_goal_window, relief='flat')
goal_btn.pack(fill='x', pady=5)

stat_btn = tk.Button(btn_frame, text='月度统计', width=14, height=2, font=normal_font, bg='#fdcb6e', fg='#2d3436', command=show_month_summary_ui, relief='flat')
stat_btn.pack(fill='x', pady=5)

category_btn = tk.Button(btn_frame, text='类别管理', width=14, height=2, font=normal_font, bg='#a29bfe', fg='white', command=lambda: open_category_manager_window(), relief='flat')
category_btn.pack(fill='x', pady=5)

# 右侧面板 - 
right_panel = tk.Frame(main_frame, bg='#f5f6fa')
right_panel.pack(side='right', fill='both', expand=True)

# 月份选择框架
month_select_frame = tk.Frame(right_panel, bg='#f5f6fa')
month_select_frame.pack(fill='x', padx=10, pady=5)

# 月份选择标签和输入框
month_label = tk.Label(month_select_frame, text='选择月份:', font=('微软雅黑', 12), bg='#f5f6fa', fg='#273c75')
month_label.pack(side='left', padx=5)

# 创建全局月份变量
selected_month = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
month_entry = tk.Entry(month_select_frame, textvariable=selected_month, font=('微软雅黑', 12), width=10)
month_entry.pack(side='left', padx=5)

# 查询按钮
query_btn = tk.Button(month_select_frame, text='查询', font=('微软雅黑', 10), bg='#0984e3', fg='white', 
                      command=lambda: [update_summary(), update_table(), update_chart()], relief='flat')
query_btn.pack(side='left', padx=5)

edit_btn = tk.Button(month_select_frame, text='编辑选中', font=('微软雅黑', 10), bg='#6c5ce7', fg='white', 
                     command=lambda: open_edit_record_window(), relief='flat')
edit_btn.pack(side='left', padx=5)

del_btn = tk.Button(month_select_frame, text='删除选中', font=('微软雅黑', 10), bg='#d63031', fg='white', 
                    command=lambda: delete_selected_record(), relief='flat')
del_btn.pack(side='left', padx=5)

# 表格区域
table_frame = tk.LabelFrame(right_panel, text='账单记录', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
table_frame.pack(fill='both', expand=True, pady=10)

# 设置表格样式
style = ttk.Style()
style.theme_use('default')
style.configure('Treeview', font=normal_font, rowheight=32, background='#ffffff', fieldbackground='#ffffff')
style.configure('Treeview.Heading', font=('微软雅黑', 13, 'bold'), background='#dff9fb', foreground='#273c75')
style.map('Treeview', background=[('selected', '#0984e3')])

# 创建表格和滚动条
columns = ('日期', '类型', '类别', '金额', '用途')
table = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

# 设置表头
table.heading('日期', text='日期')
table.heading('类型', text='类型')
table.heading('类别', text='类别')
table.heading('金额', text='金额')
table.heading('用途', text='用途/备注')

# 设置列宽
table.column('日期', width=100, anchor='center')
table.column('类型', width=80, anchor='center')
table.column('类别', width=100, anchor='center')
table.column('金额', width=100, anchor='e')
table.column('用途', width=200)

table.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')

# 消费分析区域
chart_frame = tk.LabelFrame(right_panel, text='消费分析', font=header_font, bg='#f5f6fa', fg='#273c75', padx=10, pady=10)
chart_frame.pack(fill='both', expand=True, pady=10)

# 添加导出按钮区域
export_btn_frame = tk.Frame(chart_frame, bg='#f5f6fa')
export_btn_frame.pack(pady=5)

png_btn = tk.Button(export_btn_frame, text="导出为 PNG", command=export_chart_png,
                    bg="#0984e3", fg="white", font=("微软雅黑", 10), padx=10, pady=5)
png_btn.pack(side='left', padx=10)

pdf_btn = tk.Button(export_btn_frame, text="导出为 PDF", command=export_chart_pdf,
                    bg="#6c5ce7", fg="white", font=("微软雅黑", 10), padx=10, pady=5)
pdf_btn.pack(side='left', padx=10)


# 创建一个带滚动条的框架来容纳图表
chart_canvas_frame = tk.Frame(chart_frame, bg='#f5f6fa')
chart_canvas_frame.pack(fill='both', expand=True)

# 创建画布和滚动条
chart_canvas = tk.Canvas(chart_canvas_frame, bg='#f5f6fa', highlightthickness=0)
chart_scrollbar = ttk.Scrollbar(chart_canvas_frame, orient='vertical', command=chart_canvas.yview)
chart_canvas.configure(yscrollcommand=chart_scrollbar.set)

# 添加水平滚动条
chart_h_scrollbar = ttk.Scrollbar(chart_canvas_frame, orient='horizontal', command=chart_canvas.xview)
chart_canvas.configure(yscrollcommand=chart_scrollbar.set, xscrollcommand=chart_h_scrollbar.set)

# 放置画布和滚动条
chart_scrollbar.pack(side='right', fill='y')
chart_canvas.pack(side='left', fill='both', expand=True)
chart_h_scrollbar.pack(side='bottom', fill='x')

# 创建一个框架放在画布上
chart_inner_frame = tk.Frame(chart_canvas, bg='#f5f6fa')
chart_canvas.create_window((0, 0), window=chart_inner_frame, anchor='nw')

# 创建图表
fig = plt.Figure(figsize=(12, 16), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=chart_inner_frame)
canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)


# 鼠标横向滚动（Shift+滚轮）
def _on_shift_mousewheel(event):
    chart_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
chart_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

# 更新图表函数
def update_chart():
    month = selected_month.get().strip()
    if not month:
        month = datetime.now().strftime('%Y-%m')
        selected_month.set(month)
    elif not _is_valid_month(month):
        messagebox.showwarning('提示', '月份格式需为 YYYY-MM！')
        return

    data = load_data()
    usage = {}
    for r in data:
        if r['category'] == '支出' and r['date'].startswith(month):
            key = (r.get('tag') or '').strip() or '未分类'
            usage[key] = usage.get(key, 0) + r['amount']

    ax.clear()
    if usage:
        # 设置中文字体，解决方框显示问题
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False

        # 按金额从大到小排序
        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_usage]
        sizes = [item[1] for item in sorted_usage]

        # 计算总支出
        total = sum(sizes)

        # 使用更好看的颜色方案
        colors = ['#00b894', '#00cec9', '#0984e3', '#6c5ce7', '#fdcb6e', '#e84393', '#d63031', '#e17055', '#74b9ff']
        # 如果颜色不够，循环使用
        if len(labels) > len(colors):
            colors = colors * (len(labels) // len(colors) + 1)

        # 创建水平条形图
        bars = ax.barh(labels, sizes, color=colors[:len(labels)], height=1)

        # 在条形上添加数值和百分比标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = width / total * 100
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.2f}元 ({percentage:.1f}%)',
                   va='center', fontsize=11, fontfamily='SimHei')

        # 设置图表标题和标签
        ax.set_title(f'{month} 类别消费分布', fontsize=16, fontweight='bold', pad=20, fontfamily='SimHei')
        ax.set_xlabel('支出金额 (元)', fontsize=12, fontfamily='SimHei')

        # 设置Y轴标签字体大小和字体
        ax.tick_params(axis='y', labelsize=10)
        for label in ax.get_yticklabels():
            label.set_fontfamily('SimHei')

        # 根据条目数量调整图表高度
        fig.set_figheight(max(5, len(labels) * 0.6))
        fig.set_figwidth(12)  # 加宽
    else:
        ax.text(0.5, 0.5, '本月暂无支出', ha='center', va='center', fontsize=14, fontweight='bold', fontfamily='SimHei')

    # 自动调整布局
    fig.tight_layout()
    canvas.draw()

    # 更新滚动区域
    chart_inner_frame.update_idletasks()
    chart_canvas.config(scrollregion=chart_canvas.bbox('all'))
    chart_canvas.configure(yscrollcommand=chart_scrollbar.set, xscrollcommand=chart_h_scrollbar.set)

    # 绑定鼠标滚轮事件
    def _on_mousewheel(event):
        chart_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    chart_canvas.bind_all("<MouseWheel>", _on_mousewheel)



update_summary()
update_table()
update_chart()

root.mainloop()
