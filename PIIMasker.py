import tempfile
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import ttkbootstrap as ttk
from pdf2image import convert_from_path
from ttkbootstrap.constants import *
import json
import os
from tkinter import filedialog, messagebox


class ImageEditor(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.scale_factor = None
        self.image_file_name = None
        self.tk_image = None

        # Grid configuration for layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a canvas with scrollbars
        self.canvas = ttk.Canvas(self, highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Place the canvas and scrollbars in the grid
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # Create buttons and place them at the bottom
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.create_buttons()

        self.image = None
        self.modified_image = None
        self.rectangles = []
        self.selected_rectangle = None
        self.start_x = None
        self.start_y = None
        self.image_file_name = None
        self.rect_coords_list = []  # List to store coordinates of rectangles

        self.canvas.bind("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def create_buttons(self):
        self.load_button = ttk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.save_button = ttk.Button(self.button_frame, text="Save Rectangles", command=self.save_rectangles)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.delete_rect_button = ttk.Button(self.button_frame, text="Delete Selected Rectangle",
                                             command=self.delete_rectangle)
        self.delete_rect_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.delete_image_button = ttk.Button(self.button_frame, text="Delete Inside Rectangle",
                                              command=self.delete_inside_rectangle)
        self.delete_image_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.save_image_button = ttk.Button(self.button_frame, text="Save Modified Image",
                                            command=self.save_modified_image)
        self.save_image_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

        self.process_folder_button = ttk.Button(self.button_frame, text="Process Folder", command=self.process_folder)
        self.process_folder_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        self.image_file_name = file_path
        original_image = None

        if file_path.lower().endswith('.pdf'):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
                temp_pdf.write(open(file_path, "rb").read())
                temp_pdf.flush()
                images_from_pdf = convert_from_path(temp_pdf.name)
                original_image = images_from_pdf[0]
        else:
            original_image = Image.open(file_path)

        # Scale image to fit the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.scale_factor = min(canvas_width / original_image.width, canvas_height / original_image.height)
        scaled_size = (int(original_image.width * self.scale_factor), int(original_image.height * self.scale_factor))
        self.image = original_image.resize(scaled_size, Image.Resampling.LANCZOS)

        self.modified_image = self.image.copy()
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.rect_coords_list.clear()
        self.rectangles.clear()
        # self.load_rectangles()

        # Read and apply scale_factor and rectangles
        if os.path.exists("rectangle_data.json"):
            with open("rectangle_data.json", "r") as file:
                data = json.load(file)
                self.scale_factor = self.scale_factor if self.scale_factor is not None else data.get("scale_factor", 1.0)  # Default to 1.0 if not found
                self.load_rectangles(data.get("rectangles", {}).get(self.image_file_name, []))

    def process_folder(self):
        source_folder = filedialog.askdirectory()
        if not source_folder:
            return

        # Read rectangle coordinates from rectangle_data.json
        if not os.path.exists("rectangle_data.json"):
            messagebox.showerror("Error", "No rectangle data found.")
            return

        with open("rectangle_data.json", "r") as file:
            data = json.load(file)

        # Check if the rectangle data for any image exists
        if not data:
            messagebox.showerror("Error", "No rectangle data available.")
            return

        scale_factor = data.get("scale_factor", 1.0)
        rectangles = data.get("rectangles", {})

        # Define a list of common image file extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']

        # Process each image file in the source folder
        for file_name in os.listdir(source_folder):
            file_path = os.path.join(source_folder, file_name)
            if file_name.lower().endswith('.pdf'):
                self.process_pdf(file_path, rectangles)
            else:
                if any(file_name.lower().endswith(ext) for ext in image_extensions):
                    image = Image.open(file_path)

                    # Apply masking for each set of coordinates
                    for coords in rectangles.values():
                        for rect_coords in coords:
                            scaled_coords = [c / scale_factor for c in rect_coords]
                            draw = ImageDraw.Draw(image)
                            # draw.rectangle([rect_coords[0], rect_coords[1], rect_coords[2], rect_coords[3]],
                            # fill="white")
                            draw.rectangle([scaled_coords[0], scaled_coords[1], scaled_coords[2], scaled_coords[3]],
                                           fill="white")

                    # Save the processed image in the 'masked' folder
                    masked_directory = os.path.join(os.path.dirname(source_folder), "masked")
                    if not os.path.exists(masked_directory):
                        os.makedirs(masked_directory)

                    save_path = os.path.join(masked_directory, file_name)
                    image.save(save_path)

        messagebox.showinfo("Info", "Folder processing complete.")

    def process_pdf(self, pdf_path, rect_data):
        with tempfile.TemporaryDirectory() as path:
            images_from_path = convert_from_path(pdf_path, output_folder=path)
            processed_images = []

            for image in images_from_path:
                # Apply masking for each set of coordinates
                for coords in rect_data.values():
                    for rect_coords in coords:
                        scaled_coords = [c / self.scale_factor for c in rect_coords]
                        draw = ImageDraw.Draw(image)
                        draw.rectangle([scaled_coords[0], scaled_coords[1], scaled_coords[2], scaled_coords[3]],
                                       fill="white")
                processed_images.append(image)

            # Save the processed images back to a PDF
            self.save_images_as_pdf(processed_images, pdf_path)

    def save_images_as_pdf(self, images, original_pdf_path):
        # Save the processed images in the 'masked' folder
        masked_directory = os.path.join(os.path.dirname(original_pdf_path), "masked")
        if not os.path.exists(masked_directory):
            os.makedirs(masked_directory)

        save_path = os.path.join(masked_directory, os.path.basename(original_pdf_path))
        images[0].save(save_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])

    def load_rectangles(self, rectangles):
        for rect_coords in rectangles:
            # Scale the coordinates based on the scale factor
            scaled_coords = [coord * self.scale_factor for coord in rect_coords]
            rect = self.canvas.create_rectangle(*scaled_coords, outline="red")
            self.rectangles.append(rect)

    def save_rectangles(self):
        if self.image_file_name and self.scale_factor is not None:
            data = {}
            if os.path.exists("rectangle_data.json"):
                with open("rectangle_data.json", "r") as file:
                    data = json.load(file)

            # data[self.image_file_name] = [self.canvas.coords(rect) for rect in self.rectangles]
            data = {
                "scale_factor": self.scale_factor,
                "rectangles": {self.image_file_name: [self.canvas.coords(rect) for rect in self.rectangles]}
            }

            with open("rectangle_data.json", "w") as file:
                json.dump(data, file, indent=4)

    def delete_rectangle(self):
        if self.selected_rectangle:
            try:
                # Find the index of the selected rectangle
                idx = self.rectangles.index(self.selected_rectangle)

                # Remove the rectangle from the canvas
                self.canvas.delete(self.selected_rectangle)

                # Remove the rectangle from both lists
                if idx < len(self.rect_coords_list):
                    del self.rect_coords_list[idx]
                del self.rectangles[idx]

                # Reset the selected rectangle
                self.selected_rectangle = None
            except ValueError:
                # Handle the case where the rectangle is not found in the list
                pass

    def delete_inside_rectangle(self):
        if self.selected_rectangle and self.modified_image:
            coords = self.canvas.coords(self.selected_rectangle)
            draw = ImageDraw.Draw(self.modified_image)
            draw.rectangle([coords[0], coords[1], coords[2], coords[3]], fill="white")  # Change fill color if needed
            self.update_canvas_image()

    def save_modified_image(self):
        if not self.modified_image:
            return

        if self.image_file_name.lower().endswith('.pdf'):
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                self.modified_image.save(save_path, "PDF", resolution=100.0)
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if save_path:
                self.modified_image.save(save_path)

    def update_canvas_image(self):
        self.tk_image = ImageTk.PhotoImage(self.modified_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        # Redraw all rectangles from the coordinates list
        self.rectangles.clear()  # Clear the old rectangle references
        for coords in self.rect_coords_list:
            rect = self.canvas.create_rectangle(*coords, outline="red")
            self.rectangles.append(rect)

    def on_left_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        clicked_on_rectangle = False

        # Reset the outline color of the previously selected rectangle
        if self.selected_rectangle:
            self.canvas.itemconfig(self.selected_rectangle, outline="red")

        for idx, rect in enumerate(self.rect_coords_list):
            if rect[0] < x < rect[2] and rect[1] < y < rect[3]:
                self.selected_rectangle = self.rectangles[idx]
                self.canvas.itemconfig(self.selected_rectangle, outline="blue")
                self.start_x, self.start_y = x, y
                clicked_on_rectangle = True
                break

        if not clicked_on_rectangle:
            self.selected_rectangle = None
            self.start_x, self.start_y = x, y
            new_rect_coords = [x, y, x, y]
            self.rect_coords_list.append(new_rect_coords)
            rect = self.canvas.create_rectangle(*new_rect_coords, outline="red")
            self.rectangles.append(rect)
            self.selected_rectangle = rect

    def on_drag(self, event):
        if self.selected_rectangle:
            curX, curY = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            idx = self.rectangles.index(self.selected_rectangle)

            # Check if the index is valid for rect_coords_list
            if 0 <= idx < len(self.rect_coords_list):
                self.rect_coords_list[idx] = [self.start_x, self.start_y, curX, curY]
                self.canvas.coords(self.selected_rectangle, self.start_x, self.start_y, curX, curY)

    def on_release(self, event):
        pass


if __name__ == "__main__":
    app = ttk.Window(themename="litera")
    app.geometry("1000x700")  # Set a typical size for the window
    app.title("PII Masker")  # Set window title
    ImageEditor(app).pack(expand=YES, fill=BOTH)
    app.mainloop()
