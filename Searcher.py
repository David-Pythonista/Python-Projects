from tkinter import Tk,Button,RIGHT,LEFT,filedialog,StringVar,Entry, messagebox

class Application():
    "Create a window for the searcher program."
    def __init__(self):
        self.window = Tk()
        self.window.title("Searcher")
        self.output = StringVar()
        self.result = Entry(self.window,width = 25, textvariable = self.output)
        self.result.pack()
        self.sample, self.target = [],[]
        Button(self.window, text ="Load sample file",width=20,
               command =self.load_sample).pack(side=LEFT,padx=5,pady=5)
        Button(self.window, text="Load target file",width=20,
               command =self.load_target).pack(side=LEFT,padx=5,pady=5)
        Button(self.window, text="Start", width =20,
               command =self.start).pack(side=RIGHT,padx=5,pady=5)
        self.window.mainloop()

    def load_sample(self):
        "Load an external file from the given path. It will be the sample file."
        try:
            self.sample_file = filedialog.askopenfile(filetypes=[("All","*")])
            self.sample = self.sample_file.readlines()
            self.sample_file.close()
            self.tester(self.sample)
            return self.sample
        except:
            messagebox.showinfo("Error", "Couldn't load the file. Use txt file!")

    def load_target(self):
        "Load an external file from the given path. It will be the target file."
        try:
            self.target_file = filedialog.askopenfile(filetypes=[("All","*")])
            self.target = self.target_file.readlines()
            self.target_file.close()
            self.tester(self.target)
            return self.target
        except:
            messagebox.showinfo("Error", "Couldn't load the file. Use txt file!")

    def tester(self,file):
        "Test whether the loaded files are empty or not."
        if file == []:
            self.output.set("Empty file.")
        else:
            self.output.set("")

    def length_of_sample(self,sample):
        "Returns with the lenght of the sample."
        self.length = 0
        for index in range(len(self.sample)):
            if self.sample[index][-1] == '\n':
                self.length += len(sample[index])-1
            else:
                self.length += len(sample[index])
        return self.length

    def start(self):
        "Starts the searching method."
        if self.sample != [] and self.target != []:
            self.match_finder(self.sample, self.target)
        else:
            self.output.set("Select (a) file(s)!")

    def match_finder(self, sample, target):
        "Returns the number of matches."
        self.length_of_sample(self.sample)
        number_of_errors = 0
        for row_t in range(len(target)):
            for column_t in range(len(target[row_t])):

                char_matches = 0
                if target[row_t][column_t] == sample[0][0] or sample[0][0] == ' ':

                    for row_s in range(len(sample)):
                        for column_s in range(len(sample[row_s])):

                            try:
                                if ((target[row_t+row_s])[column_t+column_s] == \
                                    (sample[row_s])[column_s]) or \
                                    (sample[row_s])[column_s] == ' ':

                                    char_matches += 1

                                    if char_matches == self.length :
                                        char_matches = 0
                                        number_of_errors += 1
                            except:
                                self.output.set("Error, please try again.")

        massage = "The number of pattern(s): " + str(number_of_errors)
        self.output.set(massage)

if __name__ == '__main__':
    program = Application()