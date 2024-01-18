import matplotlib.pyplot as plt
import numpy as np
import math

#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class ResultPlot:
    def __init__(self, parentRunViewer) -> None:
        fig = plt.figure()
        ax = np.array([[fig.add_subplot(2, 2, 1), fig.add_subplot(2, 2, 2)], [fig.add_subplot(2, 2, 3), None]])
        ax[1, 1] = fig.add_subplot(2, 2, 4, sharex=ax[1, 0], sharey=ax[1, 0])
        fig.canvas.mpl_connect('button_press_event', self.fig_click)

        # Uncomment this block
        # canvas = FigureCanvasTkAgg(fig, master=parentRunViewer.subWindow)
        # canvas_widget = canvas.get_tk_widget()
        # canvas_widget.pack()

        # toolbar = NavigationToolbar2Tk(canvas, parentRunViewer.subWindow)
        # toolbar.update()
        # canvas_widget.pack()

        # Comment plt lines below
        plt.tight_layout()
        plt.show(block=False)

        self.figure = fig
        self.axis = ax
        self.parentRunViewer = parentRunViewer

    def plot_result(self, vals = None, coeffImage = None, image = None, denImage = None):
        ax = self.axis
        if vals is not None:
            ax[0, 0].cla()
            ax[0, 0].plot(vals)
        if coeffImage is not None:
            ax[0, 1].cla()
            ax[0, 1].imshow(coeffImage, cmap='gray')
        if image is not None:
            ax[1, 0].cla()
            ax[1, 0].imshow(image, cmap='gray')
        if denImage is not None:
            ax[1, 1].cla()
            ax[1, 1].imshow(denImage, cmap='gray')
        self.figure.canvas.draw()
        #plt.draw()

    def plot_to_image(self, vals):
        # Turn off interactive mode
        plt.ioff()

        # Create a new figure
        dpi = 100
        res = (1024, 768)
        fig, ax = plt.subplots(figsize=(res[0]/dpi,res[1]/dpi), dpi=dpi)

        # Plot the values on the new figure
        ax.plot(vals)
        # ax.set_title(title)
        # ax.set_xlabel(xlabel)
        # ax.set_ylabel(ylabel)
        
        fig.canvas.draw()
        numpy_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        numpy_image = numpy_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        # Save the plot without displaying it
        plt.close(fig)
        plt.ion()

        return numpy_image

    def fig_click(self, event):
        if event.inaxes == self.axis[0, 0]:
            coeffId = math.floor(event.xdata)
            self.parentRunViewer.change_coeff(coeffId)

    def destroy(self):
        plt.close(self.figure)
