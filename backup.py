from tkinter import filedialog, colorchooser
from tkinter.messagebox import showerror, askyesno
import ttkbootstrap as ttk

if __name__ == '__main__':
    # defining global variables
    WIDTH = 750
    HEIGHT = 560
    file_path = ""
    pen_size = 3
    pen_color = "black"

    mw = ttk.Window(themename='cosmo')
    # mw.attributes('-fullscreen', True)
    mw.geometry('810x880+300+110')

    # icon images for the application
    app_icon = ttk.PhotoImage(file="assets/base_logo_white_background.png").subsample(12, 12)
    select_area = ttk.PhotoImage(file="assets/icons/select-object-filled-icon.png").subsample(12, 12)
    free_form_select_area = ttk.PhotoImage(file='assets/icons/free-form-selection.png').subsample(45, 45)
    finalize_image = ttk.PhotoImage(file='assets/icons/finalize-icon.png').subsample(12, 12)
    preview_image = ttk.PhotoImage(file='assets/icons/preview-icon.png').subsample(12, 12)
    window_close = ttk.PhotoImage(file='assets/icons/window-close-icon.png').subsample(12, 12)
    open_file = ttk.PhotoImage(file='assets/icons/open-file-icon-vector.png').subsample(12, 12)

    mw.iconphoto(False, app_icon)
    mw.title('PII - Masker | Prepare')

    # the left frame to contain the 4 buttons
    left_frame = ttk.Frame(mw, width=200, height=600)
    left_frame.pack(side="left", fill="y")

    load_file_btn = ttk.Button(left_frame, image=open_file, style="success-link")
    select_area_btn = ttk.Button(left_frame, image=select_area, style="success-link")
    free_form_btn = ttk.Button(left_frame, image=free_form_select_area, style="success-link")
    finalize_btn = ttk.Button(left_frame, image=finalize_image, style="success-link")
    preview_btn = ttk.Button(left_frame, image=preview_image, style="success-link")
    close_btn = ttk.Button(left_frame, image=window_close, style="success-link")

    load_file_btn.pack(pady=5)
    select_area_btn.pack(pady=5)
    free_form_btn.pack(pady=5)
    finalize_btn.pack(pady=5)
    preview_btn.pack(pady=5)
    close_btn.pack(pady=5)

    # the right canvas for displaying the image
    canvas = ttk.Canvas(mw, width=WIDTH, height=HEIGHT)
    canvas.pack()

    # label
    filter_label = ttk.Label(left_frame, text="Select Filter:", background="white")
    filter_label.pack(padx=0, pady=2)

    # a list of filters
    image_filters = ["Contour", "Black and White", "Blur", "Detail", "Emboss", "Edge Enhance", "Sharpen", "Smooth"]

    # combobox for the filters
    filter_combobox = ttk.Combobox(left_frame, values=image_filters, width=15)
    filter_combobox.pack(padx=10, pady=5)

    mw.mainloop()
