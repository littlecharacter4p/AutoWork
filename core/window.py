import pyautogui
import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox as mb
from core.execute import *


class Window:
    def __init__(self):
        # build ui
        self.root = tk.Tk()
        self.root.title("Auto Work")
        self.root.geometry(f"{int(pyautogui.size()[0] / 3)}"
                           f"x{int(pyautogui.size()[1] / 3)}"
                           f"+{int(pyautogui.size()[0] / 2) - int(pyautogui.size()[0] / 6)}"
                           f"+{int(pyautogui.size()[1] / 2) - int(pyautogui.size()[1] / 6)}")
        MainFrame(self.root)

    def run(self):
        self.root.mainloop()


class MainFrame:
    def __init__(self, root):
        self.root = root
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        # 1.按钮区
        self.frame_top = tk.Frame(self.root)
        self.frame_top.columnconfigure(0, weight=1)
        self.frame_top.columnconfigure(1, weight=1)
        tk.Button(self.frame_top, text='新建', command=self.add_work, fg='blue', relief=GROOVE).grid(row=0, column=0, sticky='nsew')
        tk.Button(self.frame_top, text='刷新', command=self.refresh, fg='blue', relief=RIDGE).grid(row=0, column=1, sticky='nsew')
        self.frame_top.grid(row=0, column=0, sticky='nsew')
        # 2.数据区
        self.frame_bottom = tk.Frame(self.root)
        self.frame_bottom.columnconfigure(0, weight=1)
        self.frame_bottom.rowconfigure(0, weight=1)
        # 2.1TreeView
        columns = ("name", "status")
        headers = ("作业", "状态")
        self.tv = ttk.Treeview(self.frame_bottom, show="headings", columns=columns)
        for (column, header) in zip(columns, headers):
            self.tv.column(column, anchor="w")
            self.tv.heading(column, text=header, anchor="w")
        self.tv.grid(row=0, column=0, sticky='nsew')
        self.tv.bind('<Button-2>', self.show_menu)
        self.refresh()
        self.frame_bottom.grid(row=1, column=0, sticky='nsew')
        # 2.2右键菜单
        self.menu = tk.Menu(self.tv, tearoff=False)
        self.menu.add_command(label="运行", command=self.start_work)
        self.menu.add_command(label="停止", command=self.stop_work)
        self.menu.add_command(label="查看", command=self.show_work)
        # menu.add_command(label="修改", command=func)
        # menu.add_command(label="删除", command=func)

    def refresh(self):
        # 先清空数据
        x = self.tv.get_children()
        for item in x:
            self.tv.delete(item)
        # 再插入数据
        work_list = get_all_data(WORK_FILENAME)
        if work_list:
            for work_dict in work_list:
                if work_dict == run_work:
                    self.tv.insert('', 'end', values=(work_dict.get('name'), "运行"), iid=work_dict.get('wid'))
                else:
                    self.tv.insert('', 'end', values=(work_dict.get('name'), "停止"), iid=work_dict.get('wid'))

    def add_work(self):
        self.frame_top.destroy()
        self.frame_bottom.destroy()
        BuildFrame(self.root, ActionEnum.ADD)

    def show_menu(self, event):
        item = self.tv.identify_row(event.y)
        self.tv.selection_set(item)
        self.menu.post(event.x_root, event.y_root)

    def start_work(self):
        item = self.tv.selection()
        if item:
            print(f"{item} start...")

    def stop_work(self):
        item = self.tv.selection()
        if item:
            print(f"{item} stop...")

    def show_work(self):
        item = self.tv.selection()
        self.frame_top.destroy()
        self.frame_bottom.destroy()
        BuildFrame(self.root, ActionEnum.SHOW, item[0])


class BuildFrame:
    def __init__(self, root, action, wid=None):
        self.root = root
        self.action = action
        self.wid = wid
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=True, fill=BOTH)
        # 工作流程选项卡
        tab_flow = tk.Frame(self.tab_control)
        tab_flow.rowconfigure(0, weight=1)
        tab_flow.columnconfigure(0, weight=1)
        columns = ("step", "name")
        headers = ("步骤", "名称")
        self.tv = ttk.Treeview(tab_flow, show="headings", columns=columns)
        for (column, header) in zip(columns, headers):
            self.tv.column(column, anchor="w")
            self.tv.heading(column, text=header, anchor="w")
        if self.action == ActionEnum.ADD:
            tab_flow.columnconfigure(1, weight=1)
            self.tv.grid(row=0, column=0, columnspan=2, sticky='nsew')
            tk.Button(tab_flow, text='插入', command=self.insert, fg='blue', state=DISABLED).grid(row=1, column=0, sticky='nsew')
            tk.Button(tab_flow, text='关闭', command=self.close, fg='blue').grid(row=1, column=1, sticky='nsew')
        elif self.action == ActionEnum.SHOW or self.action == ActionEnum.MODIFY:
            self.tv.grid(row=0, column=0, sticky='nsew')
            tk.Button(tab_flow, text='返回', command=self.close, fg='blue').grid(row=1, column=0, sticky='nsew')
            if self.action == ActionEnum.MODIFY:
                # 右键菜单
                self.menu = tk.Menu(self.tv, tearoff=False)
                self.menu.add_command(label="查看", command=self.show_flow_item)
                self.menu.add_command(label="修改", command=self.modify_flow_item)
                self.menu.add_command(label="删除", command=self.delete_flow_item)
                self.tv.bind('<Button-2>', self.show_menu)
            self.show_flow()
        self.tab_control.add(tab_flow, text='作业流程')
        # 工作监控选项卡
        tab_monitor = tk.Frame(self.tab_control)
        tab_monitor.rowconfigure(0, weight=1)
        tab_monitor.columnconfigure(0, weight=1)
        self.tab_control.add(tab_monitor, text='作业监控')
        tk.Button(tab_monitor, text='关闭', command=self.close, fg='blue').grid(row=0, column=0, sticky='nsew')
        self.tab_control.select(tab_flow)

    def show_menu(self, event):
        item = self.tv.identify_row(event.y)
        self.tv.selection_set(item)
        self.menu.post(event.x_root, event.y_root)

    def show_flow(self):
        print("刷新数据")
        # 先清空数据
        x = self.tv.get_children()
        for item in x:
            self.tv.delete(item)
        # 再插入数据
        flow_dict = get_special_data(self.wid, FLOW_FILENAME)
        flow_item_list = flow_dict.get('flow')
        for flow_item_dict in flow_item_list:
            self.tv.insert('', 'end', values=(f"第{flow_item_dict.get('fid') + 1}步", flow_item_dict.get('name')), iid=flow_item_dict.get('fid'))

    def show_flow_item(self):
        item = self.tv.selection()
        if item:
            print(f"{item} show...")

    def modify_flow_item(self):
        item = self.tv.selection()
        if item:
            print(f"{item} modify...")

    def delete_flow_item(self):
        item = self.tv.selection()
        if item:
            print(f"{item} delete...")

    def insert(self):
        if run_status.full():
            result = mb.askokcancel("提示", "作业正在运行，请先停止！")
            print(result)
            return
        wt_thread = WorkThread(1, "工作线程")
        wt_thread.wid = 20220315154413
        wt_thread.setDaemon(True)
        wt_thread.start()

    def close(self):
        self.tab_control.destroy()
        MainFrame(self.root)


@unique
class ActionEnum(Enum):
    ADD = 1
    MODIFY = 2
    SHOW = 3
