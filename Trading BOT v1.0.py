#Import the necessary Tkinter items
import tkinter
from tkinter import Button, Label, messagebox, Radiobutton, BooleanVar, DoubleVar, IntVar, Toplevel, TclError
from datetime import datetime
 
# from trading_method import*
import Trading_method

import matplotlib.ticker as mticker

#Import items for render the plot
import matplotlib.pyplot as plt
from matplotlib.ticker import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

#Import an iterable item
from itertools import count

class TradingBot:

    def __init__(self,parent):
        #GUI for the program
        self.window = parent

        self.frame_1 = tkinter.Frame(parent)
        self.frame_1.grid(row=1,column=0,rowspan=2)

        self.frame_2 = tkinter.Frame(parent)
        self.frame_2.grid(row=1,rowspan=3,column=1)

        self.window.title("Trading BOT")
        self.closed_positions_data = {"Close at profit": 0, "Close at loss" : 0, "All opened positions" : 0, "Profitable positions" : 0,
                                                                        "Losed positions" : 0,"Overall ratio" : 0, "Overall account" : 0 }

        #it makes the graph
        plt.figure(figsize=(11, 6), dpi=100)
        plt.gcf().set_facecolor('#F0F0F0')
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.frame_2)
        self.canvas.get_tk_widget().grid(column=0, row=0)

        #define the used variables
        self.trade, self.open_pos, self.update, self.buy_pos, self.sell_pos = BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar()
        upper_lim, lower_lim, graph_size = IntVar(), IntVar(), IntVar()

        entry_variables = [upper_lim,lower_lim,graph_size]

        self.trade, self.open_pos, self.update, self.buy_pos, self.sell_pos = True, False, False, False, False

        self.trade_type = IntVar()
        self.huf_eur_currency = 405 #data scraping 

        self.settings, self.settings_main_win = [None,50,None,0.8,0,None,0.8,0], [10,10,300] 

        for element in range(len(entry_variables)):
            entry_variables[element].set(self.settings_main_win[element])

        
        #buttons to control the program    
        self.start_trading_button = Button(self.frame_1,text="Start trading",width=20,command=self.start_trading)
        self.start_trading_button.grid(row=0,column=0,columnspan=2,ipady=4,padx=5,pady=10)
        self.settings_button = Button(self.frame_1,text="Settings",width=20,command=self.settings_menu)
        self.settings_button.grid(row=21,column=0,columnspan=2,ipady=4,padx=5,pady=5) 
        self.stop_trading_button = Button(self.frame_1,text="Stop trading",width=20,command=self.stop_trading)
        self.stop_trading_button.grid(row=22,column=0,columnspan=2,ipady=4,padx=5,pady=10)
        self.stop_trading_button.config(state="disabled")

        self.trade_type_1 = Radiobutton(self.frame_1, variable = self.trade_type, value=1, text='Linear regression')
        self.trade_type_1.grid(row=16,column=0,columnspan=1,padx=5,pady=5,sticky="W") 
        self.trade_type_2 = Radiobutton(self.frame_1, variable = self.trade_type, value=2, text='Polynomial regression')
        self.trade_type_2.grid(row=17,column=0,columnspan=1,padx=5,pady=5,sticky="W") 
        self.trade_type_3 = Radiobutton(self.frame_1, variable = self.trade_type, value=3, text='Fuzzy logic')
        self.trade_type_3.grid(row=18,column=0,columnspan=1, padx=5,pady=5,sticky="W") 

        #Button(self.frame_1,text="Exit",width=20,command=self.window.destroy).grid(row=22,column=0,columnspan=2,ipady=4,padx=5,pady=5) 
        
        Label(self.frame_1,text='Actual position').grid(row=1,column=0,columnspan=2,padx=5,pady=5)
  
        #these lists contain the data for the category types
        type_of_lines = ['#e5e5e5','ridge']
        display_names = [None, None,'Current price:','Opened price:','Close at profit:','Close at loss:','Actual loss/gain:','All opened positions:',
                            'Profitable positions:', 'Losed positions:', 'Overall ratio [%]:','Overall account:','Upper limit:', 'Lower limit:','Graph size:']

        #generate the output windows
        for numbers in range(2,len(display_names)):
            Label(self.frame_1,bg=type_of_lines[0],relief=type_of_lines[1],width=16,text=display_names[numbers]).grid(row=numbers,column=0,padx=10,pady=5,sticky='W')
            if numbers >= (len(display_names)-3):
                self.set_upper_limit = tkinter.Entry(self.frame_1,textvariable=entry_variables[0],width=6,font=('calibre',10,'normal'))
                self.set_upper_limit.grid(row=12,column=1,padx=10,pady=5,sticky='W')
                self.set_lower_limit = tkinter.Entry(self.frame_1,textvariable=entry_variables[1],width=6,font=('calibre',10,'normal'))
                self.set_lower_limit.grid(row=13,column=1,padx=10,pady=5,sticky='W')
                self.set_graph_size = tkinter.Entry(self.frame_1,textvariable=entry_variables[2],width=6,font=('calibre',10,'normal'))
                self.set_graph_size.grid(row=14,column=1,padx=10,pady=5,sticky='W')
            else:
                Label(self.frame_1,bg=type_of_lines[0],relief=type_of_lines[1],width=6,text='--.--').grid(row=numbers,column=1,padx=10,pady=5,sticky='E')
                 
    
    def set_limits(self,item,list_of_x_values, list_of_y_values):
        #set limits in the plot if a position is opened

        upper_limit, lower_limit = DoubleVar(),DoubleVar()
        upper_limit = (float(self.set_upper_limit.get()))/100
        lower_limit = (float(self.set_lower_limit.get()))/100

        def erase_limits():
            #update the trading data
            lower, upper = lower_limit_line.pop(0),upper_limit_line.pop(0)
            self.open_pos,self.update, self.buy_pos, self.sell_pos = False, False, False, False
            self.closed_positions_data["All opened positions"] = (self.closed_positions_data["Profitable positions"] + self.closed_positions_data["Losed positions"])
            self.closed_positions_data["Overall ratio"] = float('{:05.2f}'.format((self.closed_positions_data["Profitable positions"] / self.closed_positions_data["All opened positions"]) * 100))
            self.closed_positions_data["Overall account"] += float('{:.0f}'.format(self.actual_loss_gain))

            #update the display with results
            Label(self.frame_1,bg='grey90',relief='ridge',text='--.--',width=6).grid(row=3,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text='--.--',width=6).grid(row=4,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text='--.--',width=6).grid(row=5,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text=self.closed_positions_data.get("All opened positions"),width=6).grid(row=7,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text=self.closed_positions_data.get("Profitable positions"),width=6).grid(row=8,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text=self.closed_positions_data.get("Losed positions"),width=6).grid(row=9,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text=self.closed_positions_data.get("Overall ratio"),width=6).grid(row=10,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text=self.closed_positions_data.get("Overall account"),width=6).grid(row=11,column=1,padx=10,pady=5,sticky='W')

            #remove the limit lines
            lower.remove(),upper.remove()

            #enable the input entries
            #self.entries_enable()

            #save the trading results
            self.save_results()

        if self.update == True:
            self.price_at_open = list_of_y_values[item]
            self.opened_position(list_of_y_values[item],upper_limit,lower_limit)
            self.update = False

        x1, y1 = [(list_of_x_values[0 if item < int(self.set_graph_size.get()) else item-int(self.set_graph_size.get())]), list_of_x_values[item]], [self.price_at_open + upper_limit, self.price_at_open + upper_limit]
        x2, y2 = [(list_of_x_values[0 if item < int(self.set_graph_size.get()) else item-int(self.set_graph_size.get())]), list_of_x_values[item]], [self.price_at_open - lower_limit, self.price_at_open - lower_limit]

        #calculate the actual gain or loss regarding the buy or sell position
        if self.buy_pos == True:
            upper_limit_line = plt.plot(x1,y1, color="green")
            lower_limit_line = plt.plot(x2,y2, color="red")
            self.actual_loss_gain = ((list_of_y_values[item]-self.price_at_open)*self.huf_eur_currency)
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(self.actual_loss_gain),width=6).grid(row=6,column=1,padx=10,pady=5,sticky='W')
        elif self.sell_pos == True:
            upper_limit_line = plt.plot(x1,y1, color="red")
            lower_limit_line = plt.plot(x2,y2, color="green")
            self.actual_loss_gain = ((self.price_at_open-list_of_y_values[item])*self.huf_eur_currency) 
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(self.actual_loss_gain),width=6).grid(row=6,column=1,padx=10,pady=5,sticky='W')
        
        #erase the limit lines if one of them reached and update the statistics
        if list_of_y_values[item] >= self.price_at_open + upper_limit and self.buy_pos == True:
            self.closed_positions_data["Profitable positions"] += 1
            erase_limits()

        elif list_of_y_values[item] <= self.price_at_open - lower_limit and self.buy_pos == True:
            self.closed_positions_data["Losed positions"] += 1
            erase_limits()
            
        elif list_of_y_values[item] >= self.price_at_open + upper_limit and self.sell_pos == True:
            self.closed_positions_data["Losed positions"] += 1
            erase_limits()
         
        elif list_of_y_values[item] <= self.price_at_open - lower_limit and self.sell_pos == True:
            self.closed_positions_data["Profitable positinos"] += 1
            erase_limits()

            
    def start_trading(self):
        #start to plot the data

        try:
            self.close_settings()
        except:
            pass

        if self.check_data() == True:

            self.stop_trading_button.config(state="normal")

            #disable the input entries
            self.entries_disable()

            if self.trade == True:
                self.trade, self.update = False, True

                list_of_x_values, list_of_y_values, next_value = self.prepare_data()

                def update(Frame): 
                    item = next(next_value)
                    #list_of_x_values[item] = self.date_and_time()
                    self.current_price(list_of_y_values[item]) 
                    currency_plot, = plt.gcf().get_axes()
                    currency_plot.cla()
                    currency_plot.plot(list_of_x_values[(0 if item < int(self.set_graph_size.get()) else 
                        item-int(self.set_graph_size.get())):item], list_of_y_values[(0 if item < int(self.set_graph_size.get()) else item-int(self.set_graph_size.get())):item])
                    plt.xticks(rotation=90,fontsize=8)
                    plt.xlabel('Time', fontsize=10)
                    plt.ylabel('Currency', fontsize=10)

                    if item > int(self.set_graph_size.get()):

                        if self.trade_type.get() == 1:
                            result = Trading_method.linear_regression(list_of_x_values[0:item],list_of_y_values[0:item],self.settings)
                            if result == "buy" and self.buy_pos == False and self.sell_pos == False:
                                self.open_pos, self.buy_pos, self.update = True, True, True
                                self.entries_disable()
                            elif result == "sell" and self.buy_pos == False and self.sell_pos == False:
                                self.open_pos, self.sell_pos, self.update = True, True, True
                                self.entries_disable()


                        elif self.trade_type.get() == 2:
                            result = Trading_method.polynomial_regression(list_of_x_values[0:item],list_of_y_values[0:item],self.settings)
                            if result == "buy" and self.buy_pos == False and self.sell_pos == False:
                                self.open_pos, self.buy_pos, self.update = True, True, True
                                self.entries_disable()
                            elif result == "sell" and self.buy_pos == False and self.sell_pos == False:
                                self.open_pos, self.sell_pos, self.update = True, True, True
                                self.entries_disable()


                        elif self.trade_type.get() == 3:
                            pass #Fuzzy logic

                    if self.open_pos == True:
                        self.set_limits(item,list_of_x_values,list_of_y_values)


                plt.figure(figsize=(11, 6), dpi=100)
                plt.gcf().set_facecolor('#F0F0F0')
                self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.frame_2)
                self.canvas.get_tk_widget().grid(column=0, row=0)
                plt.gcf().subplots()
                self.animatinon = FuncAnimation(plt.gcf(), update, interval=100, blit=False)   
            

    def prepare_data(self):
        #load the plot data from external file
        index = count()
        list_of_x_values, list_of_y_values = [], []
        y_values = open("xxxxxx",'r')
        while y_values.readline() != '':
            list_of_y_values.append(float(y_values.readline()))
        y_values.close()
        for i in range(50000):
            list_of_x_values.append(i)
        return list_of_x_values, list_of_y_values, index


    def stop_trading(self):
        #stop the data reading process
        self.trade = False
        self.entries_disable()
        self.animatinon.event_source.stop()


    def current_price(self,value):
        #update the display with the actual currency  
        value = '{:05.2f}'.format(value) 
        Label(self.frame_1,bg='grey90',relief='ridge',text=value,width=6).grid(row=2,column=1,padx=10,pady=5,sticky='W')


    def opened_position(self,price_at_open,upper_limit,lower_limit):
        # update the display with the data of the opened postion
        Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(price_at_open),width=6).grid(row=3,column=1,padx=10,pady=5,sticky='W')
        if self.buy_pos == True:
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(price_at_open + upper_limit),width=6).grid(row=4,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(price_at_open - lower_limit),width=6).grid(row=5,column=1,padx=10,pady=5,sticky='W')
        elif self.sell_pos == True:
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(price_at_open + upper_limit),width=6).grid(row=5,column=1,padx=10,pady=5,sticky='W')
            Label(self.frame_1,bg='grey90',relief='ridge',text='{:05.2f}'.format(price_at_open - lower_limit),width=6).grid(row=4,column=1,padx=10,pady=5,sticky='W')
        

    def entries_disable(self):
        #disable the input fields on the main screen
        entries = [self.set_upper_limit.config(state="disabled"),self.set_lower_limit.config(state="disabled"),self.set_graph_size.config(state="disabled"),
                    self.trade_type_1.configure(state="disabled"),self.trade_type_2.configure(state="disabled"),self.trade_type_3.configure(state="disabled")]


    def entries_enable(self):
        #enable the input fields on the main screen
        entries = [self.set_upper_limit.config(state="normal"),self.set_lower_limit.config(state="normal"),self.set_graph_size.config(state="normal"),
                    self.trade_type_1.configure(state="normal"),self.trade_type_2.configure(state="normal"),self.trade_type_3.configure(state="normal")]


    def check_data(self):
        #input data read and validation of main window
        upper_limit,lower_limit,graph_size = self.set_upper_limit.get(),self.set_lower_limit.get(),self.set_graph_size.get()
        if upper_limit.isdigit()==False or lower_limit.isdigit()==False or graph_size.isdigit()==False:
            messagebox.showinfo("Error", "The given input is invalid. It must be intiger number.")
            return False
        if int(upper_limit) < 5 or int(upper_limit) > 100: 
            messagebox.showinfo("Error", "Upper limit must be between 5 and 100.")
            return False
        if int(lower_limit) < 5 or int(lower_limit) > 100: 
            messagebox.showinfo("Error", "Lower limit must be between 5 and 100.")
            return False
        if int(graph_size) < 100 or int(graph_size) > 1000: 
            messagebox.showinfo("Error", "Graph size must be between 100 and 1000.")
            return False
        if self.trade_type.get() == 0:
            messagebox.showinfo("Info", "Choose one trading method.")
            return False
        else:
            return True
        
    def save_results(self):
        #save every positions statistics in a file
        results = open("xxxxx","w")
        for key, value in self.closed_positions_data.items():
            data = key + ":" + str(value) + "\n"
            results.write(data)
        results.close

    def date_and_time(self):
        #use the current date as the y axis value
        date_and_time = datetime.now()
        date_and_time = date_and_time.strftime("%Y:%M:%D-%H:%M:%S")
        return date_and_time

    def settings_menu(self):
        #create the settings menu to adjust the logic 
        self.settings_button.config(state="disabled")

        self.settings_menu = Toplevel(root)
        self.settings_menu.title("Settings")
        self.settings_menu.geometry("235x300")

        window_size,lin_coeff_of_det,lin_slope, poly_coeff_of_det, poly_slope  = IntVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar()
        display_names = ['General','Window size:','Linear regression','Coefficient of determination:','Slope:','Polynomial regression','Coefficient of determination:','Slope:']
        entry_variables = [None,window_size,None,lin_coeff_of_det,lin_slope,None,poly_coeff_of_det,poly_slope]

        for element in range(0,len(entry_variables)):
            if entry_variables[element] == None:
                Label(self.settings_menu,bg='grey90',relief='ridge',text=display_names[element],width=20).grid(row=element,column=1,padx=10,pady=5,sticky='W')
            else:
                Label(self.settings_menu,text=display_names[element]).grid(row=element,column=0,columnspan=2,padx=5,pady=5,sticky='W')
                tkinter.Entry(self.settings_menu,textvariable=entry_variables[element],width=6,font=('calibre',10,'normal')).grid(row=element,column=2,padx=10,pady=5,sticky='W')
                entry_variables[element].set(self.settings[element])


        self.save_button = Button(self.settings_menu,text="Save",width=30,command = lambda arg = entry_variables:  self.save_settings(arg))

        self.save_button.grid(row=9,column=1,columnspan=2,ipady=5,padx=5,pady=10)

        if self.open_pos == True:
            self.save_button.config(state="disable")
        else:
            self.save_button.config(state="normal")

        self.settings_menu.protocol("WM_DELETE_WINDOW", self.close_settings)


    def save_settings(self,entry_variables):
        #save the settings if the input data is correct - result will be saved into the settings list which will be used ba the trading methode
            try: 
                if(entry_variables[1].get() > 100 or entry_variables[1].get() < 1):
                    messagebox.showinfo("Error", "The given input must be between 1 and 100!")
                    return 
                elif(entry_variables[3].get() > 1 or entry_variables[3].get() < 0):
                    messagebox.showinfo("Error", "The given input must be between 0 and 1!")
                    return
                elif(entry_variables[6].get() > 1 or entry_variables[6].get() < 0):
                    messagebox.showinfo("Error", "The given input must be between 0 and 1!")
                    return
            except TclError:
                    messagebox.showinfo("Error", "The given input must be a number!")
                    return
            else:
                for element in range(0,len(self.settings)):
                    if entry_variables[element] != None:
                        if entry_variables[1].get() <= 100 and entry_variables[1].get() >= 1:
                            self.settings[element]=entry_variables[element].get()
                self.close_settings()


    def close_settings(self):
        #close the settings menu
        self.settings_button.config(state="normal")
        self.settings_menu.destroy()


if __name__ == "__main__":
    #Run the program
    root = tkinter.Tk()
    appliacation = TradingBot(root)
    root.mainloop()