import tkinter as tk
from PIL import Image, ImageTk
import datetime


def get_date():
    # majority 'borrowed' from StackOverflow (user: gsteff )
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(time_format, t):
        return t.strftime(time_format).replace('{S}', str(t.day) + suffix(t.day))

    date_string = custom_strftime('%A, %B {S}', datetime.datetime.now())
    return date_string


def main():
    root = tk.Tk()
    root.title('Good Morning')
    root.geometry('800x600')
    root.bind("<Escape>", lambda event: root.destroy())

    root.grid()

#    root.overrideredirect(True)
#    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    width = 800
    height = 600

    morning_background = Image.open("green_hills.jpg").copy().resize((width, height))
    morning_background_image = ImageTk.PhotoImage(morning_background)

    background = tk.Canvas(width=width, height=height, bg='blue')
    background.grid(row=0, column=0, rowspan=20, columnspan=20)

    background.create_image(0, 0, image=morning_background_image, anchor=tk.NW)

    background.create_text(width*.5, height*.4,
                           font="AvantGarde 40 normal",
                           text="Good Morning Jack!",
                           fill="white")

    date = get_date()
    background.create_text(width*.5, height*.5,
                           font="AvantGarde 20 normal",
                           text="Today is " + date,
                           fill="white")

    root.mainloop()


if __name__ == "__main__":
    main()
