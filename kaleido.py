import Tkinter as tk
import spectrum_analyzer as sa
import AppKit
import subprocess
import tkFileDialog
import ttk
import time
import os
import PIL
from PIL import Image, ImageOps, ImageTk, ImageChops
from pylab import *
from scipy.io import wavfile


ximg = 0
yimg = 0
oldbandvals = []
bandvals = []


class GUI(tk.Frame):
    def __init__(self, master):
        # Main window initializations
        tk.Frame.__init__(self, master)
        self.master.title("Kaleidolator")
        self.master.resizable(False, False)
        self.master.tk_setPalette(background='#e6e6e6')
        self.grid(row=0, column=0)
        self.x = (self.master.winfo_screenwidth() - self.master.winfo_reqwidth()) / 6
        self.y = (self.master.winfo_screenheight() - self.master.winfo_reqheight()) / 150
        self.master.geometry("+{}+{}".format(self.x, self.y))
        self.master.config(menu=tk.Menu(self.master))

        # Key Binding initializations
        self.master.protocol('WM_DELETE_WINDOW', self.click_cancel)
        self.master.bind('<Escape>', self.click_cancel)
        self.master.bind('<Return>', self.client_run)

        # Variable initializations
        self.selected_files = tuple()
        self.file_count = tk.StringVar(value='')
        self.string_width = tk.StringVar(value='')
        self.string_height = tk.StringVar(value='')
        self.string_startx = tk.StringVar(value='')
        self.string_starty = tk.StringVar(value='')
        self.string_imgrot = tk.StringVar(value='')
        self.buttonA = tk.StringVar(value='')
        self.buttonB = tk.StringVar(value='')
        self.buttonC = tk.StringVar(value='')
        self.string_mic = tk.StringVar(value='')
        self.savestart = tk.StringVar(value='0')
        self.saveend = tk.StringVar(value='50')

        self.lowcut = tk.StringVar(value='250')
        self.midlowcut = tk.StringVar(value='500')
        self.midcut = tk.StringVar(value='2000')
        self.midhighcut = tk.StringVar(value='4000')
        self.highcut = tk.StringVar(value='8000')

        self.lowmult = tk.StringVar(value='10')
        self.midlowmult = tk.StringVar(value='10')
        self.midmult = tk.StringVar(value='10')
        self.midhighmult = tk.StringVar(value='10')
        self.highmult = tk.StringVar(value='10')

        self.loaddropdown = tk.StringVar(value="A")

        self.widthdropdown = tk.StringVar(value="Low")
        self.heightdropdown = tk.StringVar(value="Mid/Low")
        self.xstartdropdown = tk.StringVar(value="Mid")
        self.ystartdropdown = tk.StringVar(value="Mid/High")
        self.rotdropdown = tk.StringVar(value="High")

        self.img_op_var = tk.StringVar(value='Multiply')

        self.slider_valsx = 1
        self.slider_valsy = 1
        self.slider_valh = 1
        self.slider_valw = 1
        self.slider_valr = 0

        self.val_height = 0
        self.val_width = 0
        self.val_startx = 0
        self.val_starty = 0
        self.val_imgrot = 0

        self.solarval = tk.StringVar(value='')
        self.open_file = tk.StringVar(value='')
        self.counter = int(1)
        self.image_size = (0, 0)
        self.sizethumb = (200, 200)
        self.genx = tk.StringVar(value="1280")
        self.geny = tk.StringVar(value="720")
        self.frame_size = (1920, 1080)

        self.val_ycrop1 = 0
        self.val_xcrop1 = 0
        self.val_ycrop2 = 1
        self.val_xcrop2 = 1
        self.invert_bool = tk.BooleanVar()
        self.greyscale_bool = tk.BooleanVar()
        self.bw_bool = tk.BooleanVar()
        self.s2sbool = tk.BooleanVar()
        self.mic_input_bool = tk.BooleanVar()
        self.wav_input_bool = tk.BooleanVar()
        self.wavsavebool = tk.BooleanVar()
        self.neg_bool = tk.BooleanVar()

        self.secondimg = 0

        ttk.Style().configure('green/black.TButton', foreground='darkgreen', background='white')
        ttk.Style().configure('red/black.TButton', foreground='darkred', background='white')

        self.preview = Image.new('RGB', self.sizethumb)
        self.img_source = Image.new('RGB', self.sizethumb)

        # Frame initializations
        self.frame = Image.new('RGB', self.frame_size)
        self.image_frame = ImageFrame(self.master, self.frame, self.frame_size)
        self.file_frame = tk.Frame(self)
        self.file_frame.grid(row=0, column=0, sticky='n', padx=15)
        self.frame_ui = tk.Frame(self)
        self.frame_ui.grid(row=1, column=0, sticky='s', pady=30)

        # Canvas initializations
        self.preview_canvas = tk.Canvas(self.file_frame, width=200, height=200, relief='raised', border=2)

        # Label initializations
        self.label_title = tk.Label(self.file_frame, text='Load an image into A, B or C', fg='white',
                                    bg='darkblue')
        self.label_audio = tk.Label(self.file_frame, text='Set band cutoffs and multipliers', fg='white',
                                    bg='darkblue')
        self.label_wav = tk.Label(self.file_frame, text='           Load a .wav           ', fg='white', bg='darkblue')
        self.label_width = tk.Label(self.frame_ui, text='Width in pixels', fg='white', bg='black')
        self.label_height = tk.Label(self.frame_ui, text='Height in pixels', fg='white', bg='black')
        self.label_startx = tk.Label(self.frame_ui, text='Starting x pixel', fg='white', bg='black')
        self.label_starty = tk.Label(self.frame_ui, text='Starting y pixel', fg='white', bg='black')
        self.label_micx = tk.Label(self.frame_ui, text='Microphone Input \nMultiplier', fg='white', bg='black')
        self.label_imgrot = tk.Label(self.frame_ui, text='Starting rotation', fg='white', bg='black')
        self.label_imgsize = tk.Label(self.file_frame, text='Source Image Size:{}'.format(self.image_size), fg='white',
                                      bg='darkblue')

        # Entry Box initializations
        self.entry_width = tk.Entry(self.frame_ui, bg='white', textvariable=self.string_width, width=8)
        self.entry_height = tk.Entry(self.frame_ui, bg='white',  textvariable=self.string_height, width=8)
        self.entry_startx = tk.Entry(self.frame_ui, bg='white',  textvariable=self.string_startx, width=8)
        self.entry_starty = tk.Entry(self.frame_ui, bg='white',  textvariable=self.string_starty, width=8)
        self.entry_imgrot = tk.Entry(self.frame_ui, bg='white',  textvariable=self.string_imgrot, width=8)
        self.entry_savestart = tk.Entry(self.frame_ui, bg='white',  textvariable=self.savestart, width=8)
        self.entry_saveend = tk.Entry(self.frame_ui, bg='white',  textvariable=self.saveend, width=8)

        self.entry_lowcut = tk.Entry(self.file_frame, bg='white',  textvariable=self.lowcut, width=8)
        self.entry_midlowcut = tk.Entry(self.file_frame, bg='white',  textvariable=self.midlowcut, width=8)
        self.entry_midcut = tk.Entry(self.file_frame, bg='white',  textvariable=self.midcut, width=8)
        self.entry_midhighcut = tk.Entry(self.file_frame, bg='white',  textvariable=self.midhighcut, width=8)
        self.entry_highcut = tk.Entry(self.file_frame, bg='white',  textvariable=self.highcut, width=8)

        self.entry_lowmult = tk.Entry(self.file_frame, bg='white', textvariable=self.lowmult, width=8)
        self.entry_midlowmult = tk.Entry(self.file_frame, bg='white', textvariable=self.midlowmult, width=8)
        self.entry_midmult = tk.Entry(self.file_frame, bg='white', textvariable=self.midmult, width=8)
        self.entry_midhighmult = tk.Entry(self.file_frame, bg='white', textvariable=self.midhighmult, width=8)
        self.entry_highmult = tk.Entry(self.file_frame, bg='white', textvariable=self.highmult, width=8)

        self.entry_genx = tk.Entry(self.file_frame, bg='white', textvariable=self.genx, width=8)
        self.entry_geny = tk.Entry(self.file_frame, bg='white', textvariable=self.geny, width=8)

        # Slider initializations
        self.slider_width = tk.Scale(self.frame_ui, bg='white', variable=self.string_width,
                                     relief='ridge', orient='horizontal',
                                     sliderlength=50, from_=1, to=100, length=250)
        self.slider_height = tk.Scale(self.frame_ui, bg='white', variable=self.string_height,
                                      relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=1, to=100, length=250)
        self.slider_startx = tk.Scale(self.frame_ui, bg='white', variable=self.string_startx,
                                      relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=0, to=100, length=250)
        self.slider_starty = tk.Scale(self.frame_ui, bg='white', variable=self.string_starty,
                                      relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=0, to=100, length=250)
        self.slider_imgrot = tk.Scale(self.frame_ui, bg='white', variable=self.string_imgrot,
                                      relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=-360, to=360, length=250)
        self.slider_mic = tk.Scale(self.frame_ui, bg='white', variable=self.string_mic,
                                   relief='ridge', orient='vertical',
                                   sliderlength=50, from_=1000, to=1, length=200)
        self.slider_width.set(1)
        self.slider_height.set(1)

        # Button initializations
        self.button_run = ttk.Button(self.frame_ui, text='Run', width=15, style='green/black.TButton',
                                     command=self.click_run)
        self.button_save = ttk.Button(self.frame_ui, text='Save', width=15, style='red/black.TButton',
                                      command=lambda: self.client_save(self.frame, 0))
        self.submit_button = tk.Button(self.file_frame, text='Load', command=self.click_load)
        self.cancel_button = tk.Button(self.file_frame, text='Cancel', command=self.click_cancel)
        self.file_button = tk.Button(self.file_frame,
                                     default='active', text='Select file...', command=self.file_picker, anchor='w')
        self.wav_file_button = tk.Button(self.file_frame, default='active',
                                         text='Select file...', command=self.wav_file_picker, anchor='w')
        self.wav_submit_button = tk.Button(self.file_frame, text='Load', command=self.wav_load_file)

        self.imgA = ttk.Button(self.file_frame, text='A',
                               width=5, style='green/black.TButton', command=lambda: self.image_switch(self.buttonA))
        self.imgB = ttk.Button(self.file_frame, text='B',
                               width=5, style='green/black.TButton', command=lambda: self.image_switch(self.buttonB))
        self.imgC = ttk.Button(self.file_frame, text='C',
                               width=5, style='green/black.TButton', command=lambda: self.image_switch(self.buttonC))

        # Check Button initializations
        self.save_to_source = tk.Checkbutton(self.frame_ui, text='Set as new source', variable=self.s2sbool)
        self.mic_input_box = tk.Checkbutton(self.frame_ui, text='Use mic as input', variable=self.mic_input_bool)
        self.wav_input_box = tk.Checkbutton(self.frame_ui, text='Use wav as input', variable=self.wav_input_bool)
        self.invertcolour_box = tk.Checkbutton(self.file_frame, text='Invert Colour', variable=self.invert_bool)
        self.greyscale_box = tk.Checkbutton(self.file_frame, text='Greyscale', variable=self.greyscale_bool)
        self.bw_box = tk.Checkbutton(self.file_frame, text='Black/White', variable=self.bw_bool)
        self.wavsavebox = tk.Checkbutton(self.frame_ui, text='Save Range', variable=self.wavsavebool)
        # self.negbox = tk.Checkbutton(self.frame_ui, text='(-)', variable=self.neg_bool)

        self.load_dropdown = tk.OptionMenu(self.file_frame, self.loaddropdown, "A", "B", "C")

        self.width_dropdown = tk.OptionMenu(self.frame_ui, self.widthdropdown,
                                            "Low", "Mid/Low", "Mid", "Mid/High", "High")
        self.height_dropdown = tk.OptionMenu(self.frame_ui, self.heightdropdown,
                                             "Low", "Mid/Low", "Mid", "Mid/High", "High")
        self.xstart_dropdown = tk.OptionMenu(self.frame_ui, self.xstartdropdown,
                                             "Low", "Mid/Low", "Mid", "Mid/High", "High")
        self.ystart_dropdown = tk.OptionMenu(self.frame_ui, self.ystartdropdown,
                                             "Low", "Mid/Low", "Mid", "Mid/High", "High")
        self.rot_dropdown = tk.OptionMenu(self.frame_ui, self.rotdropdown,
                                          "Low", "Mid/Low", "Mid", "Mid/High", "High")
        self.img_op_dropdown = tk.OptionMenu(self.file_frame, self.img_op_var,
                                             "Multiply", "Add", "Difference", "Add Modulus", "Subtract Modulus",
                                             "Lighter", "Darker")

        self.width_dropdown.config(width=10)
        self.height_dropdown.config(width=10)
        self.xstart_dropdown.config(width=10)
        self.ystart_dropdown.config(width=10)
        self.rot_dropdown.config(width=10)
        self.img_op_dropdown.config(width=10)

        # Widget Placement
        self.label_width.grid(row=1, column=0, sticky='w')
        self.label_height.grid(row=2, column=0, sticky='w')
        self.label_startx.grid(row=3, column=0, sticky='w')
        self.label_starty.grid(row=4, column=0, sticky='w')
        self.label_imgrot.grid(row=5, column=0, sticky='w')

        self.entry_width.grid(row=1, column=2)
        self.entry_height.grid(row=2, column=2)
        self.entry_startx.grid(row=3, column=2)
        self.entry_starty.grid(row=4, column=2)
        self.entry_imgrot.grid(row=5, column=2)

        self.width_dropdown.grid(row=1, column=3)
        self.height_dropdown.grid(row=2, column=3)
        self.xstart_dropdown.grid(row=3, column=3)
        self.ystart_dropdown.grid(row=4, column=3)
        self.rot_dropdown.grid(row=5, column=3)
        self.img_op_dropdown.grid(row=11, column=3)

        self.entry_savestart.grid(row=7, column=0)
        self.entry_saveend.grid(row=8, column=0)

        self.slider_width.grid(row=1, column=1)
        self.slider_height.grid(row=2, column=1)
        self.slider_startx.grid(row=3, column=1)
        self.slider_starty.grid(row=4, column=1)
        self.slider_imgrot.grid(row=5, column=1)
        # self.slider_mic.grid(row=1, column=3, rowspan=5)

        self.button_run.grid(row=8, column=1, pady=10)
        self.mic_input_box.grid(row=8, column=2)
        self.wav_input_box.grid(row=9, column=2)
        self.button_save.grid(row=7, column=1, pady=10)
        self.save_to_source.grid(row=7, column=2)
        self.wavsavebox.grid(row=9, column=0, pady=10)
        # self.negbox.grid(row=6, column=1)

        self.label_title.grid(row=0, column=0, pady=10)
        self.label_audio.grid(row=0, column=2, columnspan=2, pady=10)

        self.file_button.grid(row=1, column=0)
        self.load_dropdown.grid(row=2, column=0)
        self.submit_button.grid(row=3, column=0)
        self.imgA.grid(row=9, column=0)
        self.imgB.grid(row=10, column=0)
        self.imgC.grid(row=11, column=0)
        self.label_wav.grid(row=5, column=0)
        self.wav_file_button.grid(row=6, column=0)
        self.wav_submit_button.grid(row=7, column=0)

        self.preview_canvas.grid(row=1, column=1, rowspan=7)
        self.label_imgsize.grid(row=8, column=1, pady=10)
        self.invertcolour_box.grid(row=9, column=1)
        self.greyscale_box.grid(row=10, column=1)
        self.bw_box.grid(row=11, column=1)

        self.entry_lowcut.grid(row=1, column=2)
        self.entry_midlowcut.grid(row=2, column=2)
        self.entry_midcut.grid(row=3, column=2)
        self.entry_midhighcut.grid(row=4, column=2)
        self.entry_highcut.grid(row=5, column=2)

        self.entry_genx.grid(row=8, column=2)
        self.entry_geny.grid(row=8, column=3)


        self.entry_lowmult.grid(row=1, column=3)
        self.entry_midlowmult.grid(row=2, column=3)
        self.entry_midmult.grid(row=3, column=3)
        self.entry_midhighmult.grid(row=4, column=3)
        self.entry_highmult.grid(row=5, column=3)
        self.cancel_button.grid(row=7, column=3)

    def click_cancel(self, event=None):
        print("The user clicked 'Cancel'")
        self.master.destroy()

    def click_load(self):
        load_dest = self.loaddropdown.get()
        self.load_file()
        self.img_prefactor()
        self.update_sliders()
        self.client_run(None)
        self.redraw_preview()
        if load_dest == 'A':
            self.buttonA = self.open_file
        if load_dest == 'B':
            self.buttonB = self.open_file
            self.secondimg = 1
            self.imgB = Image.open(self.buttonB)
        if load_dest == 'C':
            self.buttonC = self.open_file

    def click_run(self):
        wav_input_bool = self.wav_input_bool.get()
        mic_input_bool = self.mic_input_bool.get()
        savestart = self.savestart.get()
        saveend = self.saveend.get()
        savestart = int(savestart)
        saveend = int(saveend)
        if wav_input_bool:
            self.frame_size = (1920, 1080)
            self.genx = 1920
            self.geny = 1080
            for i in range(savestart, saveend):
                self.client_run(i)
                # self.redraw_preview()
                self.update()
                # print '-------------------------------------------------'
        while mic_input_bool:
            t1 = time.time()
            self.client_run(None)
            t2 = time.time()
            # self.redraw_preview()
            t3 = time.time()
            self.image_frame.update()
            t4 = time.time()
            print ('client run: %fs,' % (t2 - t1),
                   'redraw prev: %fs,' % (t3 - t2),
                   'update: %fs' % (t4 - t3),
                   'total runtime: %fs' % (t4 - t1),
                   'framerate: %i' % (1 / (t4 - t1)))
            # print '-------------------------------------------------'
        else:
            self.client_run(None)
            self.redraw_preview()
            self.update()

    def click_slider(self, event=None):
        self.client_run(None)
        self.redraw_preview()

    def client_run(self, i, event=None):
        t0 = time.time()
        img_source = self.img_source
        wavsavebool = self.wavsavebool.get()
        img_source = img_source.rotate(int(self.val_imgrot))
        t1 = time.time()
        sample_coords = self.calculate_sample_coords(i)
        t2 = time.time()
        if int(self.val_width) == 1:
            if int(self.val_height) == 1:
                self.frame = self.draw_1_x_1()
                ImageFrame(self.master, self.frame, self.frame_size)
                if wavsavebool:
                    self.client_save(self.frame, i)
                return
        t3 = time.time()
        chunk = self.draw_chunk(img_source, sample_coords)
        t4 = time.time()
        self.calculate_grid_array()
        t5 = time.time()
        save_frame = self.draw_image_frame(self.frame, chunk, self.frame_size)
        if wavsavebool:
            self.client_save(save_frame, i)
        t6 = time.time()
        print ('load and spin: %fs,' % (t1 - t0),
               'calc coords: %fs,' % (t2 - t1),
               '1x1: %fs' % (t3 - t2),
               'draw chunk: %fs' % (t4 - t3),
               'create frame: %fs' % (t5 - t4),
               'draw frame: %fs' % (t6 - t5),
               'runtime: %fs' % (t6 - t0),
               'framerate: %f' % (1 / (t6 - t0)))

    def client_save(self, frame, i):
        f = self.open_file
        fn = os.path.basename(f)
        s2sbool = self.s2sbool.get()
        wav_input_bool = self.wav_input_bool.get()
        if wav_input_bool:
            if i < 10:
                frame.save("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/000{}_{}.jpg".format(i, fn))
                return
            if i < 100:
                frame.save("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/00{}_{}.jpg".format(i, fn))
                return
            if i < 1000:
                frame.save("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/0{}_{}.jpg".format(i, fn))
                return
            else:
                frame.save("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/{}_{}.jpg".format(i, fn))
            return
        if os.path.exists("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/{}_{}.jpg".format(i, fn)):
            i += 1
            self.client_save(frame, i)
        frame.save("/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/{}_{}.jpg".format(fn, i))
        if s2sbool:
            self.open_file = (
                "/Users/bradyn/Desktop/Kaleidolator/Kaleidolator2.0/saves/{}_{}.jpg".format(fn, i))
            self.img_prefactor()
            self.redraw_preview()
            self.update_sliders()
            self.update()
            return

    def image_switch(self, i):
        self.open_file = i
        self.img_prefactor()
        self.update_sliders()
        self.client_run(None)
        self.redraw_preview()

    def load_file(self):
        global ximg, yimg
        self.counter = 0
        if self.selected_files:
            loading = LoadingFrame(self.master, len(self.selected_files))
            self._toggle_state('disabled')
            for path in self.selected_files:
                loading.progress['value'] += 1
                self.update()
                time.sleep(0.5)
                with open(path) as f:
                    self.open_file = path
            loading.destroy()
            self._toggle_state('normal')
            self.preview = Image.open(self.open_file)
            self.img_source = Image.open(self.open_file)
            ximg, yimg = self.img_source.size
            self.image_size = self.img_source.size

    def file_picker(self):
        self.selected_files = tkFileDialog.askopenfilenames(parent=self)
        self.file_count.set('{} file(s)'.format(len(self.selected_files)))

    def wav_file_picker(self):
        self.wav_file = tkFileDialog.askopenfilenames(parent=self)
        self.file_count.set('{} file(s)'.format(len(self.selected_files)))

    def wav_load_file(self):
        self.counter = 0
        if self.wav_file:
            loading = LoadingFrame(self.master, len(self.wav_file))
            self._toggle_state('disabled')
            for path in self.wav_file:
                loading.progress['value'] += 1
                self.update()
                time.sleep(0.5)
                with open(path) as f:
                    self.wav_path = path
            loading.destroy()
            self._toggle_state('normal')
            # print self.wav_path
            self.wav_read_paramaters()

    def wav_read_paramaters(self):
        self.sampFreq, self.snd = wavfile.read(self.wav_path)
        self.snd = self.snd / (2. ** 15)
        samples, channels = self.snd.shape
        wav_length = float(samples) / float(self.sampFreq)
        self.s1 = self.snd[:, 0]
        self.START = 0
        framerate = 25
        frames = wav_length * framerate
        self.samples_per_frame = samples / frames
        self.freqspacing = float(self.sampFreq / self.samples_per_frame)

        low = self.lowcut.get()
        midlow = self.midlowcut.get()
        mid = self.midcut.get()
        midhigh = self.midhighcut.get()
        high = self.highcut.get()

        self.lowcut = int(int(low) / self.freqspacing)
        self.midlowcut = int(int(midlow) / self.freqspacing)
        self.midcut = int(int(mid) / self.freqspacing)
        self.midhighcut = int(int(midhigh) / self.freqspacing)
        self.highcut = int(int(high) / self.freqspacing)

        self.lowaven = int(self.lowcut)
        self.midlowaven = int(self.midlowcut - self.lowcut)
        self.midaven = int(self.midcut - self.midlowcut)
        self.midhighaven = int(self.midhighcut - self.midcut)
        self.highaven = int(self.highcut - self.midhighcut)

        print ('length', wav_length, frames, self.samples_per_frame, self.freqspacing,
               'lowcut', self.lowcut, (int(self.lowcut) * int(self.freqspacing)),
               'midlowcut', self.midlowcut, (int(self.midlowcut) * int(self.freqspacing)),
               'midcut', self.midcut, (int(self.midcut) * int(self.freqspacing)),
               'midhighcut', self.midhighcut, (int(self.midhighcut) * int(self.freqspacing)),
               'highcut', self.highcut, (int(self.highcut) * int(self.freqspacing)),
               'averagers', self.lowaven, self.midlowaven, self.midaven, self.midhighaven, self.highaven)

        # self.wav_fft_output(int(frames))

    def wav_fft_output(self, frames):
        for i in range(0,frames):
            self.wav_run(i)

    def wav_run(self, i):
        global oldbandvals
        self.sum1 = 0
        self.sum2 = 0
        self.sum3 = 0
        self.sum4 = 0
        self.sum5 = 0
        self.s1 = self.snd[i * self.samples_per_frame:(i + 1) * self.samples_per_frame, 0]

        n = len(self.s1)
        p = fft(self.s1)
        nUniquePts = int(ceil((n + 1) / 2.0))
        p = p[0:nUniquePts]
        p = abs(p)
        p = p / float(n)
        p = p ** 2
        if n % 2 > 0:
            p[1:len(p)] = p[1:len(p)] * 2
        else:
            p[1:len(p) - 1] = p[1:len(p) - 1] * 2

        y = np.fft.fft(self.s1[self.START:self.START + self.samples_per_frame])
        spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
        spec_x = np.fft.fftfreq(int(self.samples_per_frame), d=1.0 / self.sampFreq)
        # print spec_x[i]
        peak_check = 0
        for s in range(0, self.lowcut):
            if spec_y[s] >= peak_check:
                peak_check = spec_y[s]
                peak_freq = spec_x[s]
            self.sum1 = spec_y[s] + self.sum1
            s += 1
        for s in range(self.lowcut, self.midlowcut):
            if spec_y[s] >= peak_check:
                peak_check = spec_y[s]
                peak_freq = spec_x[s]
            self.sum2 = spec_y[s] + self.sum2
            s += 1
        for s in range(self.midlowcut, self.midcut):
            if spec_y[s] >= peak_check:
                peak_check = spec_y[s]
                peak_freq = spec_x[s]
            self.sum3 = spec_y[s] + self.sum3
            s += 1
        for s in range(self.midcut, self.midhighcut):
            if spec_y[s] >= peak_check:
                peak_check = spec_y[s]
                peak_freq = spec_x[s]
            self.sum4 = spec_y[s] + self.sum4
            s += 1
        for s in range(self.midhighcut, self.highcut):
            if spec_y[s] >= peak_check:
                peak_check = spec_y[s]
                peak_freq = spec_x[s]
            self.sum5 = spec_y[s] + self.sum5
            s += 1

        lowmult = int(self.lowmult.get())
        midlowmult = int(self.midlowmult.get())
        midmult = int(self.midmult.get())
        midhighmult = int(self.midhighmult.get())
        highmult = int(self.highmult.get())

        ave1 = int(self.sum1 / self.lowaven * lowmult)
        ave2 = int(self.sum2 / self.midlowaven * midlowmult)
        ave3 = int(self.sum3 / self.midaven * midmult)
        ave4 = int(self.sum4 / self.midhighaven * midhighmult)
        ave5 = int(self.sum5 / self.highaven * highmult)

        bandvals = [ave1, ave2, ave3, ave4, ave5]
        peak_check = 20 * log10(peak_check)
        self.peak_freq = peak_freq
        # print bandvals, i, 'Peak freq and intensity:', peak_freq, peak_check
        return bandvals

    def img_prefactor(self):
        self.preview = Image.open(self.open_file)
        self.img_source = Image.open(self.open_file)
        invert_bool = self.invert_bool.get()
        greyscale_bool = self.greyscale_bool.get()
        bw_bool = self.bw_bool.get()
        if invert_bool:
            self.preview = ImageOps.invert(self.preview)
            self.img_source = ImageOps.invert(self.img_source)
        if greyscale_bool:
            self.preview = self.preview.convert('L')
            self.img_source = self.img_source.convert('L')
        if bw_bool:
            self.preview = self.preview.convert('1')
            self.img_source = self.img_source.convert('1')
        self.preview = self.preview.rotate(int(self.val_imgrot))
        self.img_source = self.img_source.rotate(int(self.val_imgrot))

    def redraw_preview(self):
        self.img_prefactor()
        self.preview.thumbnail(self.sizethumb)
        self.image_preview = ImageTk.PhotoImage(self.preview)
        self.preview_blanker = self.preview_canvas.create_rectangle(0, 0, 204, 204, fill='black')
        self.preview_canvas.create_image(100, 100, image=self.image_preview)
        self.draw_rectangle()

    def update_sliders(self):
        self.slider_width.destroy()
        self.slider_height.destroy()
        self.slider_startx.destroy()
        self.slider_starty.destroy()
        self.slider_width = tk.Scale(self.frame_ui, variable=self.string_width, relief='ridge', orient='horizontal',
                                     sliderlength=50, from_=1, to=ximg, length=250, command=self.click_slider)
        self.slider_height = tk.Scale(self.frame_ui, variable=self.string_height, relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=1, to=yimg, length=250, command=self.click_slider)
        self.slider_startx = tk.Scale(self.frame_ui, variable=self.string_startx, relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=1, to=ximg, length=250, command=self.click_slider)
        self.slider_starty = tk.Scale(self.frame_ui, variable=self.string_starty, relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=1, to=yimg, length=250, command=self.click_slider)
        self.slider_imgrot = tk.Scale(self.frame_ui, variable=self.string_imgrot, relief='ridge', orient='horizontal',
                                      sliderlength=50, from_=-360, to=360, length=250, command=self.click_slider)
        self.slider_width.grid(row=1, column=1)
        self.slider_height.grid(row=2, column=1)
        self.slider_startx.grid(row=3, column=1)
        self.slider_starty.grid(row=4, column=1)
        self.slider_imgrot.grid(row=5, column=1)
        self.slider_startx.set(int(ximg / 3))
        self.slider_starty.set(int(yimg / 2))
        self.label_imgsize.destroy()
        self.label_imgsize = tk.Label(self.file_frame, text='Source Image Size:{}'.format(self.image_size), fg='white',
                                      bg='darkblue')
        self.label_imgsize.grid(row=8, column=1, pady=10)

    def draw_chunk(self, img_source, sample_coords):
        # Creation of Kaleido pieces
        img_sample = img_source.crop(sample_coords)
        image_flip = ImageOps.flip(img_sample)
        image_mirror = ImageOps.mirror(img_sample)
        image_mifl = ImageOps.mirror(image_flip)
        chunk_size = (2 * int(self.val_width), 2 * int(self.val_height))
        self.image_chunk = Image.new('RGB', chunk_size)
        self.image_chunk.paste(img_sample, (0, 0))
        self.image_chunk.paste(image_mirror, (int(self.val_width), 0))
        self.image_chunk.paste(image_flip, (0, int(self.val_height)))
        self.image_chunk.paste(image_mifl, (int(self.val_width), int(self.val_height)))
        return self.image_chunk

    def draw_1_x_1(self):
        invert_bool = self.invert_bool.get()
        greyscale_bool = self.greyscale_bool.get()
        bw_bool = self.bw_bool.get()
        img_source = self.img_source
        frame_size = self.frame_size
        if invert_bool:
            r, g, b = img_source.getpixel((int(self.val_startx), int(self.val_starty)))
            frame = Image.new('RGB', frame_size, (r, g, b))
            return frame
        if bw_bool:
            img_source = img_source.convert('1')
            pixcolour = img_source.getpixel((int(self.val_startx), int(self.val_starty)))
            frame = Image.new('L', frame_size, pixcolour)
            return frame
        if greyscale_bool:
            img_source = img_source.convert('L')
            pixcolour = img_source.getpixel((int(self.val_startx), int(self.val_starty)))
            frame = Image.new('L', frame_size, pixcolour)
            return frame
        else:
            try:
                r, g, b = img_source.getpixel((int(self.val_startx), int(self.val_starty)))
                frame = Image.new('RGB', frame_size, (r, g, b))
                return frame
            except TypeError:
                pixcolour = img_source.getpixel((int(self.val_startx), int(self.val_starty)))
                frame = Image.new('RGB', frame_size, pixcolour)
                return frame
            except IndexError:
                return

    def draw_image_frame(self, frame, chunk, frame_size):
        for r in range(self.grid_height):
            for p in range(self.grid_width):
                frame.paste(chunk, (self.chunk_width * p, 0))
            frame.paste(frame, (0, self.chunk_height * r))
        x = int(self.genx)
        y = int(self.geny)
        generated_x, generated_y = frame_size
        excessx = generated_x - x
        excessy = generated_y - y
        val_xcrop1 = 0 + (excessx / 2)
        val_xcrop2 = val_xcrop1 + x
        val_ycrop1 = 0 + (excessy / 2)
        val_ycrop2 = val_ycrop1 + y
        coords = (val_xcrop1, val_ycrop1, val_xcrop2, val_ycrop2)
        self.frame = frame.crop(coords)
        if self.secondimg:
            img_op_var = self.img_op_var.get()
            if img_op_var == "Darker":
                self.frame = PIL.ImageChops.darker(self.frame, self.imgBrot)
            if img_op_var == "Lighter":
                self.frame = PIL.ImageChops.lighter(self.frame, self.imgBrot)
            if img_op_var == "Multiply":
                self.frame = PIL.ImageChops.multiply(self.frame, self.imgBrot)
            if img_op_var == "Add":
                self.frame = PIL.ImageChops.add(self.frame, self.imgBrot)
            if img_op_var == "Difference":
                self.frame = PIL.ImageChops.difference(self.frame, self.imgBrot)
            if img_op_var == "Add Modulus":
                self.frame = PIL.ImageChops.add_modulo(self.frame, self.imgBrot)
            if img_op_var == "Subtract Modulus":
                self.frame = PIL.ImageChops.subtract_modulo(self.frame, self.imgBrot)
            # if self.peak_freq <= 1000:
            #     self.frame = PIL.ImageChops.multiply(self.frame, self.imgBrot)
            # if self.peak_freq >= 1000:
            #     self.frame = PIL.ImageChops.darker(self.frame, self.imgBrot)
            # else:
            #     self.frame = PIL.ImageChops.multiply(self.frame, self.imgBrot)
        ImageFrame(root, self.frame, frame_size)
        return self.frame

    def draw_rectangle(self):
        rec_y_offset = int(1)
        rec_x_offset = int(1)
        rec_y_offset_divider = float(1)
        rec_x_offset_divider = float(1)
        if ximg > yimg:
            preview_height = (float(yimg) / float(ximg) * 200)
            rec_y_offset = ((200 - preview_height) / 2)
            rec_y_offset_divider = float(ximg) / float(yimg)
        if yimg > ximg:
            preview_width = (float(ximg) / float(yimg) * 200)
            rec_x_offset = ((200 - preview_width) / 2)
            rec_x_offset_divider = float(yimg) / float(ximg)
        sample_coords = self.sample_coords
        xpreview_scalefactor = ximg / float(200)
        ypreview_scalefactor = yimg / float(200)
        rec1 = (sample_coords[0] / xpreview_scalefactor / rec_x_offset_divider) + int(rec_x_offset)
        rec2 = (sample_coords[1] / ypreview_scalefactor / rec_y_offset_divider) + int(rec_y_offset)
        rec3 = (sample_coords[2]/ xpreview_scalefactor / rec_x_offset_divider) + int(rec_x_offset)
        rec4 = (sample_coords[3] / ypreview_scalefactor / rec_y_offset_divider) + int(rec_y_offset)
        rec_coords = [rec1, rec2, rec3, rec4]
        self.preview_canvas.create_rectangle(rec_coords, outline='red', width=3)

    def calculate_grid_array(self):
        # Calculate the number of rows and columns the sample needs to be pasted
        geny = self.geny
        genx = self.genx
        self.chunk_width, self.chunk_height = self.image_chunk.size
        self.grid_height = int(int(geny) / int(self.chunk_height)) + (int(geny) % int(self.chunk_height) > 0)
        self.grid_width = int(int(genx)) / int(self.chunk_width) + (int(genx) % int(self.chunk_width) > 0)
        # Symmetry check, if odd, even it if even do nothing
        if self.grid_width % 2:
            self.grid_width += 1
        if self.grid_height % 2:
            self.grid_height += 1
        if int(self.chunk_height) < 0:
            self.chunk_height += 1
        if int(self.chunk_width) < 0:
            self.chunk_width += 1
        self.frame_size = (int(self.grid_width) * int(self.chunk_width), int(self.grid_height) * int(self.chunk_height))
        self.grid_size = (self.grid_width, self.grid_height)
        # self.frame.resize(self.frame_size)
        self.frame = Image.new('RGB', self.frame_size)

    def calculate_sample_coords(self, i):
        self.get_sliders()
        mic_input_bool = self.mic_input_bool.get()
        wav_input_bool = self.wav_input_bool.get()
        self.val_imgrot = int(self.slider_valr)
        self.val_height = int(self.slider_valh)
        self.val_width = int(self.slider_valw)
        self.val_startx = int(self.slider_valsx)
        self.val_starty = int(self.slider_valsy)
        if mic_input_bool:
            self.get_randoms(None)
        if wav_input_bool:
            self.get_randoms(i)
        self.val_ycrop2 = int(self.val_starty) + (int(self.val_height / 2 + self.val_height % 2))
        self.val_xcrop2 = int(self.val_startx) + (int(self.val_width / 2 + self.val_width % 2))
        self.val_ycrop1 = int(self.val_starty) - (int(self.val_height / 2 + self.val_height % 2))
        self.val_xcrop1 = int(self.val_startx) - (int(self.val_width / 2 + self.val_width % 2))
        self.sample_coords = (self.val_xcrop1, self.val_ycrop1, self.val_xcrop2, self.val_ycrop2)
        return self.sample_coords

    def get_sliders(self):
        self.slider_valsx = self.string_startx.get()
        self.slider_valw = self.string_width.get()
        self.slider_valh = self.string_height.get()
        self.slider_valsy = self.string_starty.get()
        self.slider_valr = self.string_imgrot.get()

    def get_randoms(self, i):
        mic_input_bool = self.mic_input_bool.get()
        wav_input_bool = self.wav_input_bool.get()
        if mic_input_bool:
            newbandvals = speca.one_run(bandvals)
        if wav_input_bool:
            newbandvals = self.wav_run(i)

        fft_height = self.heightdropdown.get()
        fft_width = self.widthdropdown.get()
        fft_startx = self.xstartdropdown.get()
        fft_starty = self.ystartdropdown.get()
        fft_rot = self.rotdropdown.get()

        if fft_height == "Low":
            fft_height = int(newbandvals[0])
        if fft_height == "Mid/Low":
            fft_height = int(newbandvals[1])
        if fft_height == "Mid":
            fft_height = int(newbandvals[2])
        if fft_height == "Mid/High":
            fft_height = int(newbandvals[3])
        if fft_height == "High":
            fft_height = int(newbandvals[4])

        if fft_width == "Low":
            fft_width = int(newbandvals[0])
        if fft_width == "Mid/Low":
            fft_width = int(newbandvals[1])
        if fft_width == "Mid":
            fft_width = int(newbandvals[2])
        if fft_width == "Mid/High":
            fft_width = int(newbandvals[3])
        if fft_width == "High":
            fft_width = int(newbandvals[4])

        if fft_startx == "Low":
            fft_startx = int(newbandvals[0])
        if fft_startx == "Mid/Low":
            fft_startx = int(newbandvals[1])
        if fft_startx == "Mid":
            fft_startx = int(newbandvals[2])
        if fft_startx == "Mid/High":
            fft_startx = int(newbandvals[3])
        if fft_startx == "High":
            fft_startx = int(newbandvals[4])

        if fft_starty == "Low":
            fft_starty = int(newbandvals[0])
        if fft_starty == "Mid/Low":
            fft_starty = int(newbandvals[1])
        if fft_starty == "Mid":
            fft_starty = int(newbandvals[2])
        if fft_starty == "Mid/High":
            fft_starty = int(newbandvals[3])
        if fft_starty == "High":
            fft_starty = int(newbandvals[4])

        if fft_rot == "Low":
            fft_rot = int(newbandvals[0])
        if fft_rot == "Mid/Low":
            fft_rot = int(newbandvals[1])
        if fft_rot == "Mid":
            fft_rot = int(newbandvals[2])
        if fft_rot == "Mid/High":
            fft_rot = int(newbandvals[3])
        if fft_rot == "High":
            fft_rot = int(newbandvals[4])


        self.val_height = int(self.slider_valh) + fft_height
        self.val_width = int(self.slider_valw) + fft_width
        self.val_startx = int(self.slider_valsx) + fft_startx
        self.val_starty = int(self.slider_valsy) + fft_starty
        self.val_imgrot = int(self.slider_valr) + fft_rot + i

        if self.secondimg:
            self.imgBrot = self.imgB

    def _toggle_state(self, state):
        state = state if state in ('normal', 'disabled') else 'normal'
        widgets = (self.file_button, self.submit_button, self.cancel_button)
        for widget in widgets:
            widget.configure(state=state)


class LoadingFrame(tk.Frame):
    def __init__(self, master, count):
        tk.Frame.__init__(self, master, borderwidth=5, relief='groove')
        self.grid(row=0, column=0)
        tk.Label(self, text="Your file is being uploaded").pack(padx=15, pady=10)
        self.progress = ttk.Progressbar(self, orient='horizontal', length=250, mode='determinate')
        self.progress.pack(padx=15, pady=10)
        self.progress['value'] = 0
        self.progress['maximum'] = count
        self.tkraise()


class ImageFrame(tk.Frame):
    def __init__(self, master, frame_saved, frame_size):
        tk.Frame.__init__(self, master, borderwidth=10, relief='groove')
        self.grid(row=0, column=1, rowspan=2)
        self.image_canvas = tk.Canvas(self, width=720, height=720)
        self.image_canvas.pack()
        self.image_rendered = ImageTk.PhotoImage(frame_saved)
        self.image_canvas.create_image(360, 360, image=self.image_rendered)


# class WavReader:
#     def __init__(self):
#         self.sampFreq, self.snd = wavfile.read(self.wav_path)
#         self.snd = self.snd / (2. ** 15)
#         samples, channels = self.snd.shape
#         wav_length = float(samples) / float(self.sampFreq)
#         self.s1 = self.snd[:, 0]
#         self.START = 0
#         framerate = 25
#         frames = wav_length * framerate
#         self.samples_per_frame = samples / frames
#         self.freqspacing = float(self.sampFreq / self.samples_per_frame)
#
#         low = self.lowcut.get()
#         midlow = self.midlowcut.get()
#         mid = self.midcut.get()
#         midhigh = self.midhighcut.get()
#         high = self.highcut.get()
#
#         self.lowcut = int(int(low) / self.freqspacing)
#         self.midlowcut = int(int(midlow) / self.freqspacing)
#         self.midcut = int(int(mid) / self.freqspacing)
#         self.midhighcut = int(int(midhigh) / self.freqspacing)
#         self.highcut = int(int(high) / self.freqspacing)
#
#         self.lowaven = int(self.lowcut)
#         self.midlowaven = int(self.midlowcut - self.lowcut)
#         self.midaven = int(self.midcut - self.midlowcut)
#         self.midhighaven = int(self.midhighcut - self.midcut)
#         self.highaven = int(self.highcut - self.midhighcut)
#
#         print ('length', wav_length, frames, self.samples_per_frame, self.freqspacing, 'lowcut', self.lowcut,
#                (int(self.lowcut) * int(self.freqspacing)), 'midlowcut', self.midlowcut,
#                (int(self.midlowcut) * int(self.freqspacing)), 'midcut', self.midcut,
#                (int(self.midcut) * int(self.freqspacing)), 'midhighcut', self.midhighcut,
#                (int(self.midhighcut) * int(self.freqspacing)), 'highcut', self.highcut,
#                (int(self.highcut) * int(self.freqspacing)), 'averagers', self.lowaven, self.midlowaven, self.midaven,
#                self.midhighaven, self.highaven)
#
#     def wav_file_picker(self):
#         self.wav_file = tkFileDialog.askopenfilenames(parent=self)
#         self.file_count.set('{} file(s)'.format(len(self.selected_files)))
#
#     def wav_load_file(self):
#         self.counter = 0
#         if self.wav_file:
#             loading = LoadingFrame(self.master, len(self.wav_file))
#             for path in self.wav_file:
#                 loading.progress['value'] += 1
#                 self.update()
#                 time.sleep(0.5)
#                 with open(path) as f:
#                     self.wav_path = path
#             loading.destroy()
#             print self.wav_path
#             self.wav_read_paramaters()
#
#     def wav_run(self, i):
#         global oldbandvals
#         self.sum1 = 0
#         self.sum2 = 0
#         self.sum3 = 0
#         self.sum4 = 0
#         self.sum5 = 0
#         self.s1 = self.snd[i * self.samples_per_frame:(i + 1) * self.samples_per_frame, 0]
#         n = len(self.s1)
#         p = fft(self.s1)
#         nUniquePts = int(ceil((n + 1) / 2.0))
#         p = p[0:nUniquePts]
#         p = abs(p)
#         p = p / float(n)
#         p = p ** 2
#         if n % 2 > 0:
#             p[1:len(p)] = p[1:len(p)] * 2
#         else:
#             p[1:len(p) - 1] = p[1:len(p) - 1] * 2
#         y = np.fft.fft(self.s1[self.START:self.START + self.samples_per_frame])
#         spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
#         # spec_x = np.fft.fftfreq(self.samples_per_frame, d=1.0 / self.sampFreq)
#         # print spec_x[i]
#         for s in range(0, self.lowcut):
#             self.sum1 = spec_y[s] + self.sum1
#             s += 1
#         for s in range(self.lowcut, self.midlowcut):
#             self.sum2 = spec_y[s] + self.sum2
#             s += 1
#         for s in range(self.midlowcut, self.midcut):
#             self.sum3 = spec_y[s] + self.sum3
#             s += 1
#         for s in range(self.midcut, self.midhighcut):
#             self.sum4 = spec_y[s] + self.sum4
#             s += 1
#         for s in range(self.midhighcut, self.highcut):
#             self.sum5 = spec_y[s] + self.sum5
#             s += 1
#
#         lowmult = self.lowmult.get()
#         midlowmult = self.midlowmult.get()
#         midmult = self.midmult.get()
#         midhighmult = self.midhighmult.get()
#         highmult = self.highmult.get()
#
#         ave1 = int(self.sum1 / self.lowaven * int(lowmult))
#         ave2 = int(self.sum2 / self.midlowaven * int(midlowmult))
#         ave3 = int(self.sum3 / self.midaven * int(midmult))
#         ave4 = int(self.sum4 / self.midhighaven * int(midhighmult))
#         ave5 = int(self.sum5 / self.highaven * int(highmult))
#
#         bandvals = [ave1, ave2, ave3, ave4, ave5]
#         print bandvals, i
#         return bandvals


if __name__ == '__main__':
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info['LSUIElement'] = True
    root = tk.Tk()
    speca = sa.SpectrumAnalyzer()
    app = GUI(root)
    subprocess.call(['/usr/bin/osascript', '-e', 'tell app "Finder" to set frontmost of process "Python" to true'])
    app.mainloop()
