import sqlite3
import os.path
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
import datetime as dt
import pyautogui 
from PIL import ImageTk, Image
from khayyam import *


# plays intro when open app
def intro():
    pass
# makes a table in database
def make_table():
    conn = sqlite3.connect('karmand.db')
    c = conn.cursor()
    # c.execute("DROP TABLE karmand")
    c.execute("""CREATE TABLE IF NOT EXISTS karmand(
        fname TEXT,
        lname TEXT,
        dob TEXT,
        personaln TEXT,
        degree TEXT,
        bank TEXT,
        id_number TEXT,
        phonen TEXT,
        w_w_hours INT,
        in_hour INT,
        additional_wh INT,
        pph INT,
        net_income INT,
        reversed_name TEXT,
        person_in INT,
        total_work INT
    )
            """)

    conn.commit()
    conn.close()
    
# returns all the payment infos 
def payment(w_w_hours, pph, additional_wh):
    time = JalaliDatetime.now()
    income = ((w_w_hours * pph)/7 )* time.daysinmonth
    extra_pay = pph * additional_wh
    total_pay = income + extra_pay
    if total_pay <= 5600000:
        tax = 0
    elif total_pay > 5600000 and total_pay <= 15000000:
        tax = 0.10
    elif total_pay > 15000000 and total_pay <= 25000000:
        tax = 0.15
    elif total_pay > 25000000 and total_pay <= 35000000:
        tax = 0.20
    else:
        tax = 0.30
    
    taxes = tax * total_pay
    insurance = 0.07 * total_pay
    total_loss = taxes + insurance
    net_income = total_pay - total_loss
    
    pay_check = {"income":round(income), "extra_pay":round(extra_pay), "total_pay":round(total_pay),
                 "tax":tax, "taxes":round(taxes), "insurance":round(insurance),
                 "total_loss":round(total_loss), "net_income":round(net_income) }
    
    return pay_check

# adds a persons info to the db
def add_karmand(fname, lname, dob, personaln, degree, bank, id_number,
                phonen, w_w_hours=44, additional_wh=0, pph=32000):
    conn = sqlite3.connect('karmand.db')
    c = conn.cursor()
    c.execute("SELECT personaln, id_number FROM karmand WHERE personaln =? OR id_number=?", (personaln, id_number))
    check = c.fetchone()
    if check:
        error_win = Toplevel(bg='white')
        error_win.title("خطا")
        error_win.lift(root)
        icon = PhotoImage(file=os.path.join(os.path.dirname(__file__), "error.png"))
        error_win.iconphoto(False, icon)
        lbl = Label(error_win, text=".کارمند با شماره پرسنلی یا شناسنامه یکسان قبلا ثبت شده", fg="black", bg="white")
        lbl.pack(side="top", padx=1, pady=2)
        btn = Button(error_win, text="باشه", font= "bold", command= lambda: error_win.destroy())
        btn.pack(side="bottom", padx=1, pady=1)
        error_win.mainloop()
    else:
        rev_fname = fname
        rev_lname = lname
        rev_name = rev_lname + rev_fname
        c.execute("INSERT INTO karmand VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(fname.lower(), lname.lower(), dob, personaln,
                                                                             degree, bank, id_number,phonen,
                                                                             w_w_hours, 0, additional_wh,pph,
                                                                             payment(w_w_hours,pph,additional_wh)["net_income"],
                                                                             rev_name, 0, 0))
    
    conn.commit()
    conn.close()
    
    
# makes "add_karmand" usable for tk.button
def add_btn_func():
    # gets arguments from entry boxes
    add_karmand(fname=fn_entry.get(),
                lname=ln_entry.get(),
                dob=dob_entry.get(),
                personaln=pn_entry.get(),
                degree=dgr_entry.get(),
                bank=bank_entry.get(),
                id_number=id_entry.get(),
                phonen=phn_entry.get(),
                w_w_hours=int(wwh_entry.get()),
                pph=int(pph_entry.get()))
    # updates the treeview
    query_db()
    
       
# gets data from db and inserts them to tree view
def query_db():
    conn = sqlite3.connect("karmand.db")
    c= conn.cursor()
    
    c.execute("""SELECT net_income,phonen,personaln,lname,fname FROM karmand 
              WHERE person_in=? ORDER BY reversed_name ASC""", (1,))
    records = c.fetchall()
    
    count = 0
    # sep by even and odd rows to make them different color
    remove_all()
    for record in records:
        if count%2 == 0:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="evenin")
        else:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="oddin")
        
        count += 1
    
    c.execute("""SELECT net_income,phonen,personaln,lname,fname FROM karmand 
              WHERE person_in=? ORDER BY reversed_name ASC""", (0,))
    records = c.fetchall()
    
    # sep by even and odd rows to make them different color
    for record in records:
        if count%2 == 0:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="evenout")
        else:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="oddout")
        
        count += 1
    
    conn.commit()
    conn.close()
    
# removes the selected person from tree and db
def remove_one():
    try:
        # deletes from db
        def full_delete(event=""):
            selected = my_tree.focus()
            up_info = my_tree.item(selected, 'values')[2]
            conn = sqlite3.connect("karmand.db")
            c = conn.cursor()
            c.execute("DELETE FROM karmand WHERE personaln = ?", (up_info,))
            conn.commit()
            c.close()
            conn.close()
            warn_win.destroy()
    
            x = my_tree.selection()[0]
            my_tree.delete(x)
            query_db() 
            
        # asks if you want to del the person     
        selected = my_tree.focus()
        fn = my_tree.item(selected, 'values')[4] 
        ln = my_tree.item(selected, 'values')[3]    
        warn_txt1 = "ایا میخواهید کارمند"
        warn_txt2 = "را حذف کنید؟"
        warn_win = Toplevel(bg='white')
        warn_win.title("خطا")
        warn_win.lift(root)
        warn_win.focus()
        center_x = int(root.winfo_screenwidth()/2 - warn_win.winfo_width()/ 2)
        center_y = int(root.winfo_screenheight()/2 - warn_win.winfo_height()/ 2)
        warn_win.geometry(f'+{center_x}+{center_y}')
        icon = PhotoImage(file=os.path.join(os.path.dirname(__file__), "error.png"))
        warn_win.iconphoto(False, icon)
        lbl = Label(warn_win, text= f'{warn_txt1} \"{fn} {ln}\" {warn_txt2}', fg="black", bg="white")
        lbl.pack(side="top", padx=10, pady=2)
        
        btn_frm = Frame(warn_win, bg="white")
        btn_frm.pack(side="bottom", padx=10, pady=5)
        no_btn = Button(btn_frm, text="خیر", font= "bold", command= lambda: warn_win.destroy(),)
        no_btn.pack(side="right", padx=1, pady=1)
        yes_btn = Button(btn_frm, text="بله", font= "bold",command= full_delete)
        yes_btn.pack(side="left", padx=10, pady=1)
        
        warn_win.bind("<Return>", func=full_delete)
        warn_win.mainloop()
    except:
        pass

# clears the treeview
def remove_all():
    for record in my_tree.get_children():
        my_tree.delete(record)


# Clears entry boxes
def refresh(event=""):
    query_db()
    fn_entry.delete(0,END)
    ln_entry.delete(0,END)
    id_entry.delete(0,END)
    pay_entry.delete(0,END)
    pph_entry.delete(0,END)
    wwh_entry.delete(0,END)
    bank_entry.delete(0,END)
    dgr_entry.delete(0,END)
    aw_entry.delete(0,END)
    pn_entry.delete(0,END)
    phn_entry.delete(0,END)
    dob_entry.delete(0,END)
    
    
# adds the selected persons info to entry boxes    
def select_record(event):
    try:
        fn_entry.delete(0,END)
        ln_entry.delete(0,END)
        id_entry.delete(0,END)
        pay_entry.delete(0,END)
        pph_entry.delete(0,END)
        wwh_entry.delete(0,END)
        bank_entry.delete(0,END)
        dgr_entry.delete(0,END)
        aw_entry.delete(0,END)
        pn_entry.delete(0,END)
        phn_entry.delete(0,END)
        dob_entry.delete(0,END)
        
        
        selected = my_tree.focus()
        up_info = my_tree.item(selected, 'values')[2]
        
        conn = sqlite3.connect('karmand.db')
        c= conn.cursor()
        c.execute("""SELECT
                fname,
                lname,
                id_number,
                pph,
                w_w_hours,
                bank,
                degree,
                additional_wh,
                personaln,
                phonen,
                dob,
                net_income
                FROM karmand
                WHERE personaln =?
                """, (up_info,))
        
        values = c.fetchall()
        
        # output to entry boxes
        fn_entry.insert(0, values[0][0])
        ln_entry.insert(0, values[0][1])
        id_entry.insert(0, values[0][2])
        pay_entry.insert(0, values[0][11])
        pph_entry.insert(0, values[0][3])
        wwh_entry.insert(0, values[0][4])
        bank_entry.insert(0, values[0][5])
        dgr_entry.insert(0, values[0][6])
        aw_entry.insert(0, values[0][7])
        pn_entry.insert(0, values[0][8])
        phn_entry.insert(0, values[0][9])
        dob_entry.insert(0, values[0][10])
    except IndexError:
        pass
        
# updates db and treeview
def update_db():
    selected = my_tree.focus()
    up_info = my_tree.item(selected, 'values')[2]
    
    conn = sqlite3.connect('karmand.db')
    c= conn.cursor()
    # gets the data from entries and updates the db
    c.execute('''UPDATE karmand SET 
              fname = ?,
              lname = ?,
              id_number = ?,
              pph = ?,
              w_w_hours = ?,
              bank = ?,
              degree = ?,
              additional_wh = ?,
              personaln = ?,
              phonen = ?,
              dob = ?,
              net_income = ?
              WHERE personaln = ?''', (fn_entry.get(),ln_entry.get(),id_entry.get(),
                                                    int(pph_entry.get()),int(wwh_entry.get()),bank_entry.get(),
                                                    dgr_entry.get(),int(aw_entry.get()),pn_entry.get(),
                                                    phn_entry.get(),dob_entry.get(),
                                                    payment(int(wwh_entry.get()),int(pph_entry.get())
                                                            ,int(aw_entry.get()))["net_income"],
                                                    up_info,))
    
    
    conn.commit()
    conn.close()
       
    #update treeview   
    query_db()
      
    fn_entry.delete(0,END)
    ln_entry.delete(0,END)
    id_entry.delete(0,END)
    pay_entry.delete(0,END)
    pph_entry.delete(0,END)
    wwh_entry.delete(0,END)
    bank_entry.delete(0,END)
    dgr_entry.delete(0,END)
    aw_entry.delete(0,END)
    pn_entry.delete(0,END)
    phn_entry.delete(0,END)
    dob_entry.delete(0,END)

# filters the treeview
def search(event=""):
    conn = sqlite3.connect("karmand.db")
    c = conn.cursor()
    c.execute("""SELECT net_income, phonen, personaln, lname, fname FROM karmand WHERE
              fname LIKE ? AND lname LIKE ? AND id_number LIKE ? AND net_income LIKE ? AND
              pph LIKE ? AND w_w_hours LIKE ? AND bank LIKE ? AND degree LIKE ? AND
              additional_wh LIKE ? AND personaln LIKE ? AND phonen LIKE ? AND dob LIKE ? AND
              person_in = ? ORDER BY reversed_name ASC""",
              ("%"+fn_entry.get()+"%", "%"+ln_entry.get()+"%", "%"+id_entry.get()+"%",
               "%"+pay_entry.get()+"%","%"+pph_entry.get()+"%", "%"+wwh_entry.get()+"%",
            "%"+bank_entry.get()+"%", "%"+dgr_entry.get()+"%", "%"+aw_entry.get()+"%",
            "%"+pn_entry.get()+"%", "%"+phn_entry.get()+"%", "%"+dob_entry.get()+"%", 1))
    
    records = c.fetchall()
    
    count = 0
    # sep by even and odd rows to make them different color
    remove_all()
    for record in records:
        if count%2 == 0:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="evenin")
        else:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="oddin")
        
        count += 1 
        
    c.execute("""SELECT net_income, phonen, personaln, lname, fname FROM karmand WHERE
              fname LIKE ? AND lname LIKE ? AND id_number LIKE ? AND net_income LIKE ? AND
              pph LIKE ? AND w_w_hours LIKE ? AND bank LIKE ? AND degree LIKE ? AND
              additional_wh LIKE ? AND personaln LIKE ? AND phonen LIKE ? AND dob LIKE ? AND
              person_in = ? ORDER BY reversed_name ASC""",
              ("%"+fn_entry.get()+"%", "%"+ln_entry.get()+"%", "%"+id_entry.get()+"%",
               "%"+pay_entry.get()+"%","%"+pph_entry.get()+"%", "%"+wwh_entry.get()+"%",
            "%"+bank_entry.get()+"%", "%"+dgr_entry.get()+"%", "%"+aw_entry.get()+"%",
            "%"+pn_entry.get()+"%", "%"+phn_entry.get()+"%", "%"+dob_entry.get()+"%", 0))
    
    records = c.fetchall()
    
    for record in records:
        if count%2 == 0:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="evenout")
        else:
            my_tree.insert(parent='',index='end',iid=count, text='',
                           values=(record[0],record[1],record[2],record[3],record[4]), tags="oddout")
        
        count += 1
    
    conn.commit()
    conn.close()
    
# returns the exact time into one float number    
def float_time():
    time= dt.datetime.now()
    hour = time.hour
    min = time.minute
    float_time = eval(f'{hour}.{min}')
    return float_time
    
# adds the entry time to db     
def person_in():
    try:
        selected = my_tree.focus()
        value = my_tree.item(selected, 'values')[2]
        conn = sqlite3.connect("karmand.db")
        c = conn.cursor()
        c.execute("UPDATE karmand SET in_hour=?, person_in=? WHERE personaln=?", (float_time(), 1, value))
        conn.commit()
        conn.close()
        query_db()
    except:
        pass

# returns False for person_in and calculates additional_wh in db  
def person_out():
    try:
        selected = my_tree.focus()
        value = my_tree.item(selected, 'values')[2]
        
        conn = sqlite3.connect("karmand.db")
        c = conn.cursor()
        c.execute("SELECT additional_wh, in_hour, total_work, w_w_hours, pph FROM karmand WHERE personaln=?", (value,))
        infos = c.fetchall()
        
        time = JalaliDatetime.now()
        total_work = infos[0][2] + abs( float_time() - infos[0][1])
        aw = total_work - infos[0][3]*time.daysinmonth
        if aw < 0:
            aw = 0
            
        c.execute("""UPDATE karmand SET person_in=?, additional_wh=?, total_work=?, net_income=? WHERE personaln=?""",
                (0, aw, total_work, payment(w_w_hours=infos[0][3], pph=infos[0][4], additional_wh=aw)["net_income"], value))
        conn.commit()
        conn.close()
        query_db()
    except:
        pass
    
#opens a new window to show pay check    
def pay_check(): 
    try:
        pay_win = Toplevel( bg="white")
        
        pay_win.lift()

        # adjust win size and locates it at center of scrn
        scr_w = root.winfo_screenwidth()
        scr_h = root.winfo_screenheight()

        pay_win_w = int((scr_w/4)*3)
        pay_win_h = int((scr_h/4)*3) - 75

        center_x = int(scr_w/2 - pay_win_w / 2)
        center_y = int(scr_h/2 - pay_win_h / 2)

        pay_win.geometry(f'{pay_win_w}x{pay_win_h}+{center_x}+{center_y}')
        pay_win.resizable(width=False, height=False)
        pay_win.update_idletasks()
        
        # saves an image of the pay check
        def save_pay():
            screenshot = pyautogui.screenshot(region=(pay_win.winfo_x()+10, pay_win.winfo_y()+30, pay_win_w-5,pay_win_h-32))
            save_path = askdirectory(initialdir="Desktop", mustexist=True, title="انتخاب محل ذخیره")
            
            def ask_name_func():
                ask_name = Toplevel( bg='grey')
                ask_name.title("انتخاب نام")
                ask_name.lift()
                center_x = int(root.winfo_screenwidth()/2 - ask_name.winfo_width()/ 2)
                center_y = int(root.winfo_screenheight()/2 - ask_name.winfo_height()/ 2)
                ask_name.geometry(f'250x50+{center_x}+{center_y}')
                icon = PhotoImage(file=os.path.join(os.path.dirname(__file__), "bamdadpng.png"))
                ask_name.iconphoto(False, icon,)
                
                ask_name.rowconfigure(index=0, weight=1)
                ask_name.columnconfigure(index=0, weight=1)
                ask_name.columnconfigure(index=1, weight=1)
                ask_name.columnconfigure(index=2, weight=1)
                
                ask_lbl = Label(ask_name, text="نام فایل", bg="grey")
                ask_lbl.grid(row=0, column=1, sticky="nsew")
                
                ask_entry = Entry(ask_name)
                ask_entry.grid(row=0, column=0, sticky="ew")
                
                def used_name_btn_func(event=""):
                    used_name.destroy()
                    ask_name_func()
                
                def get_name_entry(event=""):
                    global file_name
                    file_name = ask_entry.get()
                    dir = save_path+"/"+file_name+".png"
                    is_dir = os.path.exists(dir)
                    ask_name.destroy()
                    
                    if is_dir == True:
                    
                        global used_name
                        used_name = Toplevel(bg='white')
                        used_name.title("خطا")
                        used_name.lift()
                        center_x = int(root.winfo_screenwidth()/2 - used_name.winfo_width()/ 2)
                        center_y = int(root.winfo_screenheight()/2 - used_name.winfo_height()/ 2)
                        used_name.geometry(f'+{center_x}+{center_y}')
                        icon = PhotoImage(file=os.path.join(os.path.dirname(__file__), "error.png"))
                        used_name.iconphoto(False, icon)
                        lbl = Label(used_name, text= "فایلی مشابه با این اسم وجود دارد\nلطفا اسمی دیگر انتخاب کنید", fg="black", bg="white")
                        lbl.pack(side="top", padx=10, pady=2)
                        btn = Button(used_name, text="باشه", command=used_name_btn_func )
                        btn.pack()
                        used_name.bind("<Return>", func=used_name_btn_func)
                    
                    else:
                        ask_name.destroy()
                        screenshot.save(fp=dir,format="jpeg")
                        
                ask_btn = Button(ask_name, text="ذخیره", command=get_name_entry)
                ask_btn.grid(row=0, column=2, sticky="nsew")
                ask_name.bind("<Return>", func=get_name_entry)
                ask_name.mainloop()
            ask_name_func()
            
        pay_win.title("فیش حقوقی")
        
        file_dir2 = os.path.dirname(__file__)
        icon = PhotoImage(file=os.path.join(file_dir2, "bamdadpng.png"))
        pay_win.iconphoto(False, icon)

        pay_win.rowconfigure(index=0, weight=1)
        pay_win.rowconfigure(index=1, weight=1)
        pay_win.rowconfigure(index=2, weight=1)
        pay_win.rowconfigure(index=3, weight=1)
        pay_win.rowconfigure(index=4, weight=1)
        pay_win.rowconfigure(index=5, weight=1)

        pay_win.columnconfigure(index=0, weight=1)
        
        # datetime frame
        datetime_frame = Frame(pay_win, bg="white",height=40)
        datetime_frame.grid(row=0,column=0, sticky="new")
        
        dt_txt = " :تاریخ گزارش"
        date = JalaliDate.today()
        
        sep_frame = Frame(datetime_frame, bg="white", height=40)
        sep_frame.pack(side="left", fill="both")
        
        d_zer = ""
        mon_zer = ""
        
        if date.day < 10:
            d_zer = "0"
        if date.month < 10:
            mon_zer = "0"
            
        date_lbl = Label(sep_frame, text=f'{date.year}/{mon_zer}{date.month}/{d_zer}{date.day} {dt_txt}' , bg="white")
        date_lbl.pack(anchor=NW)
        
        time_txt = " :ساعت گزارش"
        time = JalaliDatetime.now()
        
        min_zer = ""
        h_zer = ""
        
        if time.minute < 10:
            min_zer = "0"
        if time.hour < 10:
            h_zer = "0"
        
        time_lbl = Label(sep_frame, text=f'{h_zer}{time.hour}:{min_zer}{time.minute}        {time_txt}', bg="white")
        time_lbl.pack(anchor=SW)
        
        logo_frame = Frame(datetime_frame, bg="white", height=40)
        logo_frame.pack(anchor=NE, fill="both")
        
        #resizing logo and packing
        file_dir1 = os.path.dirname(__file__)
        logo = Image.open(os.path.join(file_dir1, "bamdadpng.png"))
        resize = logo.resize((40,40))
        
        rsz_logo = ImageTk.PhotoImage(resize)
        
        logo_lbl = Label(logo_frame, image= rsz_logo)
        logo_lbl.image = rsz_logo
        logo_lbl.pack(side="right")
        
        bamdad_lbl = Label(logo_frame, text="دانش و فناوری بامداد",fg="blue", bg="white", font="Nexa 20")
        bamdad_lbl.pack(side="right")
        
        conn = sqlite3.connect("karmand.db")
        c = conn.cursor()
        c.execute("""SELECT fname, lname, dob, personaln, id_number, bank, degree, phonen, w_w_hours, pph,
                additional_wh FROM karmand WHERE personaln = ?""", (pn_entry.get(),))
        records = c.fetchall()
        
        #information frame
        info_frame = LabelFrame(pay_win, text="اطلاعات فردی", labelanchor=NE,font="Nexa 15", bg="white")
        info_frame.grid(row=1, column=0, sticky="nsew")
        
        info_frame.rowconfigure(index=0,weight=1)
        info_frame.rowconfigure(index=1,weight=1)
        info_frame.rowconfigure(index=2,weight=1)

        info_frame.columnconfigure(index=0 , weight=1)
        info_frame.columnconfigure(index=1 , weight=1)
        info_frame.columnconfigure(index=2 , weight=1)
        
        
        fn_lbl = Label(info_frame, text ="نام: "+records[0][0],font= "Nexa 16", justify="right", bg="white")
        fn_lbl.grid(row=0, column=2, sticky="nse", padx=10, pady=5, )
        
        ln_lbl = Label(info_frame, text ="نام خانوادگی: "+records[0][1],font= "Nexa 16", justify="right", bg="white" )
        ln_lbl.grid(row=1, column=2, sticky="nse", padx=10, pady=5)
        
        dob_lbl = Label(info_frame, text ="تاریخ تولد: "+records[0][2],font= "Nexa 16" , justify="right", bg="white")
        dob_lbl.grid(row=2, column=2, sticky="nse", padx=10, pady=5)
        
        pn_lbl = Label(info_frame, text ="شماره پرسنلی: "+records[0][3],font= "Nexa 16", justify="right", bg="white" )
        pn_lbl.grid(row=0, column=1, sticky="nse", padx=10, pady=5)
        
        id_lbl = Label(info_frame, text ="شماره ملی: "+records[0][4],font= "Nexa 16", justify="right", bg="white" )
        id_lbl.grid(row=1, column=1, sticky="nse", padx=10, pady=5)
        
        bank_lbl = Label(info_frame, text ="شماره حساب: "+records[0][5],font= "Nexa 16", justify="right", bg="white" )
        bank_lbl.grid(row=2, column=1, sticky="nse", padx=10, pady=5)
        
        dgr_lbl = Label(info_frame, text ="مدرک: "+records[0][6],font= "Nexa 16" , justify="right", bg="white")
        dgr_lbl.grid(row=0, column=0, sticky="nse", padx=10, pady=5)
        
        phn_lbl = Label(info_frame, text ="شماره تماس: "+records[0][7],font= "Nexa 16", justify="right", bg="white" )
        phn_lbl.grid(row=1, column=0, sticky="nse", padx=10, pady=5)
        
        bank_frame = Frame(info_frame, bg="white", height=60, width=100)
        bank_frame.grid(row=2, column=0, sticky="nse")
        
        img = bank_definer(records[0][5])
        bank_logo_lbl = Label(bank_frame, image= img, bg="white")
        bank_logo_lbl.image = img
        bank_logo_lbl.pack()
        
        # pay info titles frame
        titles_frame = Frame(pay_win, height=20)
        titles_frame.grid(row=2, column=0, sticky="ew")
        
        titles_frame.rowconfigure(index=0,weight=1)
        
        titles_frame.columnconfigure(index=0,weight=1)
        titles_frame.columnconfigure(index=1,weight=1)
        titles_frame.columnconfigure(index=2,weight=1)
        
        prof_title = LabelFrame(titles_frame, height=35)
        prof_title.grid(row=0, column=2, sticky="we")
        prof_title.propagate(False)
        prof_lbl = Label(prof_title, text=" مزایا  ",font="Nexa 15")
        prof_lbl.pack(anchor=CENTER)
        
        loss_title = LabelFrame(titles_frame, height=35)
        loss_title.grid(row=0, column=1, sticky="ew",)
        loss_title.propagate(False)
        loss_lbl = Label(loss_title, text="کسورات",font="Nexa 15")
        loss_lbl.pack(anchor=CENTER)
        
        dtil_title = LabelFrame(titles_frame, height=35)
        dtil_title.grid(row=0, column=0, sticky="ew")
        dtil_title.propagate(False)
        dtil_lbl = Label(dtil_title, text="جزییات",font="Nexa 15")
        dtil_lbl.pack(anchor=CENTER)
        
        pay_dic = payment(w_w_hours=records[0][8], pph=records[0][9], additional_wh=records[0][10])
        
        pay_frame = Frame(pay_win, bg="white")
        pay_frame.grid(row=3, column=0, sticky="nsew")
        
        pay_frame.rowconfigure(index=0,weight=1)
        
        pay_frame.columnconfigure(index=0,weight=1)
        pay_frame.columnconfigure(index=1,weight=1)
        pay_frame.columnconfigure(index=2,weight=1)
        
        prof_lf = LabelFrame(pay_frame, height=180, bg="white")
        prof_lf.grid(row=0, column=2, sticky="nsew")
        prof_lf.propagate(False)
        
        income_lbl = Label(prof_lf, text="حقوق پایه:  "+str(pay_dic["income"]) ,font="Nexa 18", bg="white")
        income_lbl.pack(anchor=NE)
        aw_lbl = Label(prof_lf, text="پاداش اضافه کاری:  "+str(pay_dic["extra_pay"]),font="Nexa 18", bg="white")
        aw_lbl.pack(anchor=E)
        
        loss_lf = LabelFrame(pay_frame, height=180, bg="white")
        loss_lf.grid(row=0, column=1, sticky="nsew")
        loss_lf.propagate(False)
        
        taxes_lbl = Label(loss_lf, text="مالیات:  "+str(pay_dic["taxes"]),font="Nexa 18", bg="white")
        taxes_lbl.pack(anchor=NE)
        insur_lbl = Label(loss_lf, text="بیمه:  "+str(pay_dic["insurance"]),font="Nexa 18", bg="white")
        insur_lbl.pack(anchor=E)
        
        dtil_lf = LabelFrame(pay_frame, height=180, bg="white")
        dtil_lf.grid(row=0, column=0, sticky="nsew")
        dtil_lf.propagate(False)
        
        tax_lbl = Label(dtil_lf, text="درصد مالیات:  "+"%"+str(pay_dic["tax"]*100),font="Nexa 18", bg="white")
        tax_lbl.pack(anchor=NE)
        insur_per_lbl = Label(dtil_lf, text="درصد بیمه:  "+"%"+"7.0",font="Nexa 18", bg="white")
        insur_per_lbl.pack(anchor=E)
        wwh_lbl = Label(dtil_lf, text="ساعت کار پایه در هفته:  "+str(records[0][8]),font="Nexa 18", bg="white")
        wwh_lbl.pack(anchor=E)
        pph_lbl = Label(dtil_lf, text="حقوق ساعتی:  "+str(records[0][9]),font="Nexa 18", bg="white")
        pph_lbl.pack(anchor=E)
        awh_lbl = Label(dtil_lf, text="مقدار اضافه کاری:  "+str(records[0][10]),font="Nexa 18", bg="white")
        awh_lbl.pack(anchor=E)
        
        total_frame = Frame(pay_win)
        total_frame.grid(row=4, column=0, sticky="ew")
        
        total_frame.rowconfigure(index=0, weight=1)
        
        total_frame.columnconfigure(index=0, weight=1)
        total_frame.columnconfigure(index=1, weight=1)
        total_frame.columnconfigure(index=2, weight=1)
        
        pay_total_lf = LabelFrame(total_frame, height=40)
        pay_total_lf.grid(row=0, column=2, sticky="nsew")
        pay_total_lf.propagate(False)
        pay_total_lbl = Label(pay_total_lf, text="مجموع :  "+str(pay_dic["total_pay"]),font="Nexa 18 bold" )
        pay_total_lbl.pack(side="right")
        
        loss_total_lf = LabelFrame(total_frame, height=40)
        loss_total_lf.grid(row=0, column=1, sticky="nsew")
        loss_total_lf.propagate(False)
        loss_total_lbl = Label(loss_total_lf, text="مجموع :  "+str(pay_dic["total_loss"]),font="Nexa 18 bold" )
        loss_total_lbl.pack(side="right")
        
        income_net_lf = LabelFrame(total_frame, height=40)
        income_net_lf.grid(row=0, column=0, sticky="nsew")
        income_net_lf.propagate(False)
        income_net_lbl = Label(income_net_lf, text="حقوق :  "+str(pay_dic["net_income"]),font="Nexa 18 bold" )
        income_net_lbl.pack(side="right")
        
        btns_frame = Frame(pay_win, width=120, bg="white")
        btns_frame.grid(row=5, column=0)
        
        save_btn = Button(btns_frame, text="ذخیره", font="Nexa 12 bold", command=save_pay)
        save_btn.pack(side="left", padx=10, fill="x")
        
        close_btn = Button(btns_frame, text="بستن", font="Nexa 12 bold", command=lambda: pay_win.destroy(),)
        close_btn.pack(side="right", padx=10, fill="x")
        
        pay_win.mainloop()
    except IndexError:
        pay_win.destroy()
        check_err = Toplevel(bg='white')
        check_err.title("خطا")
        check_err.lift(root)
        icon = PhotoImage(file=os.path.join(os.path.dirname(__file__), "error.png"))
        check_err.iconphoto(False, icon)
        lbl = Label(check_err, text=".کارمندی برای گرفتن فیش حقوقی انتخاب نشده", fg="black", bg="white")
        lbl.pack(side="top", padx=1, pady=2)
        btn = Button(check_err, text="باشه", font= "bold", command= lambda: check_err.destroy())
        btn.pack(side="bottom", padx=1, pady=1)
        check_err.mainloop()
    
# defines witch bank this number refers to   
def bank_definer(bank_num):
    logo_dir = os.path.join(os.path.dirname(__file__), "banks/unknownpng.png")
    bank_logo = Image.open(logo_dir)
    resized_logo = bank_logo.resize((80,60))
    
    
    if bank_num[0] == "6":
        if bank_num[1] == "2":
            if bank_num[0:6] == "627648":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/tosesaderatpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627961":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/sanatmadanpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "628023":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/maskanpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627760":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/postbankpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627412":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/eghtesadnovinpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "622106":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/parsianpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627488":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/karafarinpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "621986":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/samanpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627353":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/postbankpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "627381":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/ansarpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
        elif bank_num[1] == "3":
            if bank_num[0:6] == "639346":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/sinapng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "639607":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/sarmayepng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "636214":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/tatpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "639370":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/mehreghtesadpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((100,60))
        else:
            if bank_num[0:6] == "610433":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/melatpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "603799":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/melipng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "603770":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/keshavarzipng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "603769":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/saderatpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
    elif bank_num[0] == "5":
        if bank_num[1] == "0":
            if bank_num[0:6] == "502908":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/tosetaavonpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((90,90))
            elif bank_num[0:6] == "502229":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/pasargadpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((90,60))
            elif bank_num[0:6] == "502806":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/shahrpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((90,60))
            elif bank_num[0:6] == "502938":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/deypng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((90,60))
        else:
            if bank_num[0:6] == "589210":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/sepahpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((60,60))
            elif bank_num[0:6] == "589463":
                script_dir = os.path.dirname(__file__)
                logo_dir = os.path.join(script_dir, "banks/refahpng.png")
                bank_logo = Image.open(logo_dir)
                resized_logo = bank_logo.resize((90,60))
                
    rsz_bank_logo = ImageTk.PhotoImage(resized_logo)
    
    return rsz_bank_logo
        
            

    
# make the root window    
root = Tk()

con = sqlite3.connect('karmand.db')

# adjust win size and locates it at center of scrn
scr_w = root.winfo_screenwidth()
scr_h = root.winfo_screenheight()

root_w = int((scr_w/4)*3)
root_h = int((scr_h/4)*3)

center_x = int(scr_w/2 - root_w / 2)
center_y = int(scr_h/2 - root_h / 2)

root.geometry(f'{root_w}x{root_h}+{center_x}+{center_y}')
root.update_idletasks()

root.title("مدیریت کارمند")
file_dir = os.path.dirname(__file__)
icon = PhotoImage(file=os.path.join(file_dir, "bamdadpng.png"))
root.iconphoto(False, icon)

root.rowconfigure(index=0, weight=1)
root.rowconfigure(index=1, weight=1)
root.rowconfigure(index=2, weight=1)

root.columnconfigure(index=0, weight=1)

# Adds style 
style = ttk.Style()

#Theme
style.theme_use('default')

#Treeview Colors
style.configure("Treeview",
	background="#D3D3D3",
	foreground="black",
	rowheight=25,
	fieldbackground="#D3D3D3")

# Changes Selected Color
style.map('Treeview',
    background=[('selected', "#347083")])

# Creates a Treeview Frame
tree_frame = LabelFrame(root, text="کارمندان", font="Nexa 12 bold", labelanchor=NE)
tree_frame.grid(padx=10,row=0,column=0, sticky="nsew")

#adding weight to frame
tree_frame.columnconfigure(index=0, weight=1)
tree_frame.columnconfigure(index=1, weight=1)
tree_frame.rowconfigure(index=0, weight=1)

# Creates a Treeview Scrollbar
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side="right", fill="y")

# Creates The main Treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
my_tree.pack(expand="yes", fill="both")

# connects Scrollbar to treeview
tree_scroll.config(command=my_tree.yview)

# Defines Our Columns
my_tree['columns'] = ("حقوق", "شماره تماس", "شماره پرسنلی", "نام خانوادگی", "نام")

# Formats Our Columns
my_tree.column("#0", width=0, stretch=False)
my_tree.column("حقوق", anchor=CENTER, width=140,stretch=True)
my_tree.column("شماره تماس", anchor=CENTER, width=140,stretch=True)
my_tree.column("شماره پرسنلی", anchor=CENTER, width=100,stretch=True)
my_tree.column("نام خانوادگی", anchor=CENTER, width=140,stretch=True)
my_tree.column("نام", anchor=CENTER, width=140,stretch=True)


# Creates Headings
my_tree.heading("#0", text="", anchor=W)
my_tree.heading("حقوق", text="حقوق", anchor=CENTER)
my_tree.heading("شماره تماس", text="شماره تماس", anchor=CENTER)
my_tree.heading("شماره پرسنلی", text="شماره پرسنلی", anchor=CENTER)
my_tree.heading("نام خانوادگی", text="نام خانوادگی", anchor=CENTER)
my_tree.heading("نام", text="نام", anchor=CENTER)



# make treevie bi-color
my_tree.tag_configure('oddout', background="white")
my_tree.tag_configure('evenout', background="lightblue")
my_tree.tag_configure('evenin', background="limegreen")
my_tree.tag_configure('oddin', background="springgreen4")

# makes table if not created and fills treeview with db info
make_table()
query_db()

# makes frame for entry boxes
data_frame = LabelFrame(root, text="مشخصات کارمند", font="Nexa 12 bold",labelanchor=NE)
data_frame.grid(padx=10, row=1, column=0, sticky="nsew")

# adds weight to frame
data_frame.rowconfigure(index=0,weight=1)
data_frame.rowconfigure(index=1,weight=1)
data_frame.rowconfigure(index=2,weight=1)

data_frame.columnconfigure(index=0 , weight=1)
data_frame.columnconfigure(index=1 , weight=1)
data_frame.columnconfigure(index=2 , weight=1)
data_frame.columnconfigure(index=3 , weight=1)
data_frame.columnconfigure(index=4 , weight=1)
data_frame.columnconfigure(index=5 , weight=1)
data_frame.columnconfigure(index=6 , weight=1)
data_frame.columnconfigure(index=7 , weight=1)

# making the enries and labels
dgr_label = Label(data_frame, text="مدرک تحصیلی")
dgr_label.grid(row=0, column=1,sticky="nsew", padx=0, pady=10)
dgr_entry = Entry(data_frame)
dgr_entry.grid(row=0, column=0,sticky="nsew", padx=20, pady=10)

dob_label = Label(data_frame, text="تاریخ تولد")
dob_label.grid(row=0, column=3,sticky="nsew", padx=0, pady=10)
dob_entry = Entry(data_frame)
dob_entry.grid(row=0, column=2,sticky="nsew", padx=20, pady=10)

ln_label = Label(data_frame, text="نام خانوادگی")
ln_label.grid(row=0, column=5,sticky="nsew", padx=0, pady=10)
ln_entry = Entry(data_frame)
ln_entry.grid(row=0, column=4,sticky="nsew", padx=20, pady=10)

fn_label = Label(data_frame, text="نام")
fn_label.grid(row=0, column=7,sticky="nsew", padx=0, pady=10)
fn_entry = Entry(data_frame)
fn_entry.grid(row=0, column=6,sticky="nsew", padx=20, pady=10)
              
bank_label = Label(data_frame, text="شماره حساب")
bank_label.grid(row=1, column=1,sticky="nsew", padx=0, pady=10)
bank_entry = Entry(data_frame)
bank_entry.grid(row=1, column=0,sticky="nsew", padx=20, pady=10)

phn_label = Label(data_frame, text="شماره تماس")
phn_label.grid(row=1, column=3,sticky="nsew", padx=0, pady=10)
phn_entry = Entry(data_frame)
phn_entry.grid(row=1, column=2,sticky="nsew", padx=20, pady=10)

id_label = Label(data_frame, text="کد ملی")
id_label.grid(row=1, column=5,sticky="nsew", padx=0, pady=10)
id_entry = Entry(data_frame)
id_entry.grid(row=1, column=4,sticky="nsew", padx=20, pady=10)

pn_label = Label(data_frame, text="کد پرسنلی")
pn_label.grid(row=1, column=7,sticky="nsew", padx=0, pady=10)
pn_entry = Entry(data_frame)
pn_entry.grid(row=1, column=6,sticky="nsew", padx=20, pady=10)

aw_label = Label(data_frame, text="اضافه کار")
aw_label.grid(row=2, column=1,sticky="nsew", padx=0, pady=10)
aw_entry = Entry(data_frame)
aw_entry.grid(row=2, column=0,sticky="nsew", padx=20, pady=10)

wwh_label = Label(data_frame, text="ساعت کار در هفته")
wwh_label.grid(row=2, column=3,sticky="nsew", padx=0, pady=10)
wwh_entry = Entry(data_frame)
wwh_entry.grid(row=2, column=2,sticky="nsew", padx=20, pady=10)

pph_label = Label(data_frame, text="حقوق ساعتی")
pph_label.grid(row=2, column=5,sticky="nsew", padx=0, pady=10)
pph_entry = Entry(data_frame)
pph_entry.grid(row=2, column=4,sticky="nsew", padx=20, pady=10)

pay_label = Label(data_frame, text="حقوق")
pay_label.grid(row=2, column=7,sticky="nsew", padx=0, pady=10)
pay_entry = Entry(data_frame)
pay_entry.grid(row=2, column=6,sticky="nsew", padx=20, pady=10)

# make frame for buttons
button_frame = LabelFrame(root)
button_frame.grid(padx=10, row=2, column=0, sticky="nsew")

# add weight to frame
button_frame.rowconfigure(index=0, weight=1)

button_frame.columnconfigure(index=0 , weight=1)
button_frame.columnconfigure(index=1 , weight=1)
button_frame.columnconfigure(index=2 , weight=1)
button_frame.columnconfigure(index=3 , weight=1)
button_frame.columnconfigure(index=4 , weight=1)
button_frame.columnconfigure(index=5 , weight=1)
button_frame.columnconfigure(index=6 , weight=1)
button_frame.columnconfigure(index=7 , weight=1)

# making the buttons
update_button = Button(button_frame, text="ویرایش اطلاعات", font="Nexa 12 bold", command=update_db)
update_button.grid(row=0, column=0,sticky="nsew", padx=10, pady=10)

add_button = Button(button_frame, text="اضافه کردن کارمند", font="Nexa 12 bold", command=add_btn_func)
add_button.grid(row=0, column=1,sticky="nsew", padx=10, pady=10)

pay_check_button = Button(button_frame, text="دریافت فیش حقوقی", font="Nexa 12 bold", command=pay_check) 
pay_check_button.grid(row=0, column=2,sticky="nsew", padx=10, pady=10)

remove_one_button = Button(button_frame, text="حذف کارمند", font="Nexa 12 bold", command=remove_one)
remove_one_button.grid(row=0, column=3,sticky="nsew", padx=10, pady=10)

person_exit_button = Button(button_frame, text="خروج کارمند", font="Nexa 12 bold", command= person_out)
person_exit_button.grid(row=0, column=4,sticky="nsew", padx=10, pady=10)

person_entry_button = Button(button_frame, text="ورود کارمند", font="Nexa 12 bold", command= person_in)
person_entry_button.grid(row=0, column=5,sticky="nsew", padx=10, pady=10)

search_button = Button(button_frame, text="جست و جو", font="Nexa 12 bold", command= search)
search_button.grid(row=0, column=6,sticky="nsew", padx=10, pady=10)

clear_entries_button = Button(button_frame, text="بارگذاری مجدد", font="Nexa 12 bold", command=refresh)
clear_entries_button.grid(row=0, column=7,sticky="nsew", padx=10, pady=10)

# binds left-click to slect_record function
my_tree.bind("<ButtonRelease-1>", func=select_record)
root.bind("<Return>", func=search)
root.bind("<Control-Key-r>", func=refresh)

root.mainloop()










