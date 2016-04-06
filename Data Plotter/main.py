#!/usr/bin/env python3
###################################################################
#
#   CSSE1001/7030 - Assignment 2
#
#   Student Username: s4392687
#
#   Student Name: Maxwell Bo
#
###################################################################

#####################################
# Support given below - DO NOT CHANGE
#####################################

from assign2_support import *

#####################################
# End of support 
#####################################

# Add your code here
from collections import OrderedDict

class AnimalData(object):
    """
    A class responsible for storing AnimalDataSet objects, and relevant information
    pertaining to their use, such as their name, string representation,
    colour and display flags.
    """
    def __init__(self) -> None:
        """
        Constructor: AnimalData()
        """
        self._index = -1
        self._animalObjects = OrderedDict()
        self._colourFlags = []
        self._selectedFlags = []

    def load_data(self, filename: str) -> any:
        """
        Loads in data from the given filename

        load_data(str) -> Union[int, bool]
        """
        dataset = AnimalDataSet(filename)

        if dataset.get_name() not in self._animalObjects:
            self._index += 1
            self._animalObjects[dataset.get_name()] = dataset
            self._colourFlags.append(COLOURS[self._index])
            self._selectedFlags.append(True)
            return self._index
        else:
            return False

    def get_animal_names(self) -> list:
        """
        Returns a list of animal names (as strings) in the order
        they were loaded in.

        get_animal_names(AnimalData) -> List[str]
        """
        return list(self._animalObjects.keys())

    def get_animal(self: super, animal: str) -> AnimalDataSet:
        """
        Returns a reference to an AnimalDataSet object given
        an animal’s name.
        """
        return self._animalObjects[animal]

    def is_colour(self, index: int) -> str:
        """
        Returns the colour the indexth animal data is to 
        be displayed and plotted with.
        """
        return self._colourFlags[index]

    def is_selected(self, index: int) -> bool:
        """
        Informs as to whether the indexth animal data is to
        be displayed.
        """
        return self._selectedFlags[index]

    def select(self, index: int) -> None:
        """
        Sets the indexth data set flag, indicating that the animal 
        data should be displayed.
        """
        self._selectedFlags[index] = True

    def deselect(self, index: int) -> None:
        """
        Clears the indexth data set flag, indicating that the animal
        data should not be displayed.
        """
        self._selectedFlags[index] = False

    def get_ranges(self) -> tuple:
        """
        Returns a 4-tuple of the form
        (min_height, max_height, min_weight, max_weight).

        If no sets are selected the method will return a 4-tuple of
        (None, None, None, None) 

        get_ranges(AnimalData) -> Union[
                                        Tuple[float, float, float, float], 
                                        Tuple[None, None, None, None]
                                        ]
        """
        heights = []
        weights = []
        for animal in [self.get_animal(name) for index, name in enumerate(self.get_animal_names())\
        if self.is_selected(index) is True]:
            heights.append(animal.get_height_range()[0])
            heights.append(animal.get_height_range()[1])
            weights.append(animal.get_weight_range()[0])
            weights.append(animal.get_weight_range()[1])

        if heights and weights:
            return (min(heights), max(heights), min(weights), max(weights))
        else:
            return (None, None, None, None)

    def to_tabbed_string(self, index: int) -> str:
        """
        Returns a padded string summarising the indexth
        data set.
        """
        if self.is_selected(index) is True:
            return LABEL_FORMAT.format( 
                    self.get_animal_names()[index],
                    len(self.get_animal(self.get_animal_names()[index]).get_data_points()), 
                    "Visible"
                    )
        else:
            return LABEL_FORMAT.format( 
                    self.get_animal_names()[index],
                    len(self.get_animal(self.get_animal_names()[index]).get_data_points()), 
                    "Hidden"
                    )

class SelectionBox(tk.Listbox):
    """
    A class that extends tkinter.Listbox providing methods that easily 
    allow data retrieval and the addition/update of new entries
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Constructor: SelectionBox(tkinter.Frame, **kwargs)
        """
        super().__init__(*args, **kwargs)

    def get_index(self) -> int:
        """
        Returns the index of the entry highlighted
        
        Preconditions:
        If there is no entry highlighted, the program will
        throw an error dialog box.
        """
        return self.curselection()

    def make_entry(self, entry: str, colour: str) -> None:
        """
        Creates a new entry, with colour.
        """
        self.insert(tk.END, entry)
        self.itemconfig(tk.END, {'fg': colour})

    def update_entry(self, index: int, entry: str, colour: str) -> None:
        """
        Updates a pre-existing entry with a new colour
        and string.
        """
        self.delete(index)
        self.insert(index, entry)
        self.itemconfig(index, {'fg': colour})

class Plotter(tk.Canvas):
    """
    A class that exends tkinter.Canvas, providing methods that handle mouse movement
    and window resize events, data loading and point plotting.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Constructor: Plotter(tkinter.Frame, **kwargs)
        """
        super().__init__(*args, **kwargs)
        
        self.bind("<Configure>", self.on_resize)
        self._canvasWidth = 0
        self._canvasHeight = 0

        self.bind('<Motion>', self.on_motion)
        self.bind("<Leave>", self.on_leave)

        self._displayingData = False
        self.pushedLabel = ""

        self._translator = CoordinateTranslator(1, 1, 1, 2, 1, 2)
        self._vertical_line = self.create_line(0, 0, 0, 0)
        self._horizontal_line = self.create_line(0, 0, 0, 0)
        
        self._cache = None
        
    def on_resize(self, event: tk.Event) -> None:
        """
        Given a <Configure> tkinter.Event, assigns its attributes
        to Plotter private instance variables for later use.

        Triggers a refresh event, if the Plotter has an AnimalData cache
        """
        self._canvasWidth = event.width
        self._canvasHeight = event.height
        if self._cache:
            self.refresh_with(self._cache)

    def on_motion(self, event: tk.Event) -> None:
        """
        Given a mouse <Motion> tkinter.Event, uses its coordinate attributes
        to reposition the crosshair.

        These coordinates are translated, and pushed as a string to 
        a public field.
        """
        if self._displayingData:
            self.coords(self._horizontal_line, event.x, 0, event.x, self._canvasHeight)
            self.coords(self._vertical_line, 0, event.y, self._canvasWidth, event.y)
            self.pushedLabel = "Height: {0:.2f}cm  Weight: {1:.2f}kg".format(
                                self._translator.get_height(event.x), 
                                self._translator.get_weight(event.y)
                                )

    def on_leave(self, event: tk.Event) -> None:
        """
        Accepts a tkinter.Event, and makes the 
        crosshair invisible

        An empty string is pushed to a public field.
        """
        self.coords(self._horizontal_line, 0, 0, 0, 0)
        self.coords(self._vertical_line, 0, 0, 0, 0)
        self.pushedLabel = ""

    def refresh_with(self, data: AnimalData) -> None:
        """
        Given a AnimalData object, caches it to a Plotter private instance
        variable for use. 

        Reinitializes a CoordinateTranslator with new ranges 
        and canvas dimensions, wipes the canvas clean, 
        and replots all the points again. 

        If there are datasets flagged to displayed,
        sets flags so that the Plotter knows if it 
        should draw crosshairs / display labels. 
        """
        self._cache = data
        if None not in self._cache.get_ranges():
            self._translator.__init__(
                                self._canvasWidth, 
                                self._canvasHeight,
                                self._cache.get_ranges()[0], 
                                self._cache.get_ranges()[1], 
                                self._cache.get_ranges()[2],
                                self._cache.get_ranges()[3]
                                )
            self._displayingData = True
        else:
            self._displayingData = False

        self.delete('point')
        for index, value in enumerate(self._cache.get_animal_names()):
            if self._cache.is_selected(index):
                colour = self._cache.is_colour(index)
                dataset = self._cache.get_animal(value).get_data_points()
                for point in dataset:
                    newX, newY = self._translator.get_coords(point[0], point[1])
                    self.plot_point(newX, newY, colour)

    def plot_point(self, x: float, y: float, colour: str) -> None:
        """
        Given x and y coordinates, and colour, plots a 5 x 5 rectangle filled with colour, 
        with its centre lying on the provided coordinates.

        Plotted points are tagged with 'point'. 
        """
        self.create_rectangle((x-2.5), (y-2.5), (x+2.5), (y+2.5),  fill=colour, tag='point')

class AnimalDataPlotApp(object):
    """
    A class that creates a GUI for plotting animal weights and heights.
    """
    def __init__(self, master: tk.Tk) -> None:
        """
        Constructor: AnimalDataPlotApp(tkinter.Tk)
        """
        self._master = master
        self._master.title('Animal Data Plot App')
        self._master.bind('<Motion>', self.on_motion)
        self._master.grab_set()

        self._menubar = tk.Menu(self._master)
        self._filemenu = tk.Menu(self._menubar, tearoff=0)
        self._filemenu.add_separator()
        self._filemenu.add_command(label="Open", command=self.load_file)
        self._menubar.add_cascade(label="File", menu=self._filemenu)
        self._master.config(menu=self._menubar)

        self._LHS = tk.Frame(self._master)
        self._LHS.pack(side=tk.LEFT, anchor=tk.N, fill=tk.Y)

        self._sets_label = tk.Label(self._LHS, text="Animal Data Sets")
        self._sets_label.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)

        self._buttons_frame = tk.Frame(self._LHS)
        self._buttons_frame.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)
        self._select = tk.Button(self._buttons_frame, text = "Select", command = self.select)
        self._select.pack(side=tk.LEFT, anchor=tk.E, expand=True, fill=tk.X)
        self._deselect = tk.Button(self._buttons_frame, text = "Deselect", command = self.deselect)
        self._deselect.pack(side=tk.LEFT, anchor=tk.E, expand=True, fill=tk.X)

        self._selection_box = SelectionBox(self._LHS, width=30, bg = "#DDDDDD", font = SELECTION_FONT)
        self._selection_box.pack(side=tk.TOP, anchor=tk.W, fill=tk.Y, expand=True)

        self._RHS = tk.Frame(self._master)
        self._RHS.pack(side=tk.LEFT, anchor=tk.N, expand=True, fill=tk.BOTH)
        
        self._pointerText = tk.StringVar()
        self._pointerText.set("")
        self._pointer_label = tk.Label(self._RHS, textvariable=self._pointerText)
        self._pointer_label.pack(side=tk.TOP, anchor=tk.N)

        self._plotter = Plotter(self._RHS, bg='white')
        self._plotter.pack(expand=True, fill=tk.BOTH)

        self._data = AnimalData()

    def on_motion(self, event: tk.Event) -> None:
        """
        Accepts a tkinter.Event, and updates a label with a string
        pulled from a Plotter public field.
        """
        self._pointerText.set(self._plotter.pushedLabel)

    def load_file(self) -> None:
        """
        Opens a file selection dialogbox.

        If a valid file is selected, updates the AnimalData object, 
        updates the SelectionBox object and refreshes the Plotter object
        with the updated AnimalData object.  
        """
        filename = filedialog.askopenfilename( filetypes =  (   
                                            ("All files", "*.*"), 
                                            ("CSV files", "*.csv")
                                            ) )
        if filename:
            try: 
                newIndex = self._data.load_data(filename)
                if newIndex is not False:
                    self._plotter.refresh_with(self._data)
                    self._selection_box.make_entry(
                                            self._data.to_tabbed_string(newIndex),
                                            self._data.is_colour(newIndex)
                                            )
            except:
                messagebox.showerror("File Error", 
                "{0} is an invalid Animal Data file".format(filename))

    def select(self) -> None:
        """
        Flags the highlighted dataset as "Visible", updates the SelectionBox 
        object and refreshes the Plotter object with the updated AnimalData object.  
        """
        try:
            index = self._selection_box.get_index()[0]
            self._data.select(index)
            self._plotter.refresh_with(self._data)
            self._selection_box.update_entry(
                                            index, 
                                            self._data.to_tabbed_string(index),
                                            self._data.is_colour(index)
                                            )
        except:
            messagebox.showerror("Unable to change flag", 
            "Please choose a dataset from the list below to select")
    
    def deselect(self) -> None: 
        """
        Flags the highlighted dataset as "Hidden", updates the SelectionBox 
        object and refreshes the Plotter object with the updated AnimalData object.  
        """
        try:
            index = self._selection_box.get_index()[0]
            self._data.deselect(index)
            self._plotter.refresh_with(self._data)
            self._selection_box.update_entry(
                                            index, 
                                            self._data.to_tabbed_string(index), 
                                            self._data.is_colour(index)
                                            )
        except:
            messagebox.showerror("Unable to change flag",
            "Please choose a dataset from the list below to deselect")



##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
# 
# This code will run the interact function if
# you use Run -> Run Module  (F5)
# Because of this we have supplied a "stub" definition
# for interact above so that you won't get an undefined
# error when you are writing and testing your other functions.
# When you are ready please change the definition of interact above.
###################################################

def main():
    root = tk.Tk()
    app = AnimalDataPlotApp(root)
    root.geometry("800x400")
    root.mainloop()

if __name__ == '__main__':
    main()