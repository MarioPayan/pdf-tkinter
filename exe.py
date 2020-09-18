import pathlib
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox as mb
from PyPDF2 import PdfFileWriter, PdfFileReader
import webbrowser

class PDFSplitter:
    root = Tk()
    inputpdf = None
    destinationPath = ""
    pdfName = StringVar()
    pathStr = StringVar()
    warningStr = StringVar()

    def __init__(self):
        self.destinationPath = pathlib.Path(__file__).parent.absolute()
        self.root.title("Separador de PDFs")
        self.root.geometry("950x500+10+20")
        self.mainFrame = Frame(self.root)
        self.editFrame = Frame(self.mainFrame)
        self.textbox = Text(self.editFrame)
        self.scrollbar = Scrollbar(self.editFrame)
        self.actionFrame = Frame(self.mainFrame)
        self.uploadButton = Button(self.actionFrame, text = 'Subir PDF', command=self.askForPDF)
        self.folderButton = Button(self.actionFrame, text = 'Seleccionar carpeta PDF', command=self.askForPath)
        self.generateFilesButton = Button(self.actionFrame, text = 'Exportar PDFs', state=DISABLED, command=self.exportPDFPages)
        self.textActionFrame = Frame(self.actionFrame)
        self.clearButton = Button(self.textActionFrame, text = 'Eliminar', command=self.clearText)
        self.copyButton = Button(self.textActionFrame, text = 'Copiar', command=self.copyText)
        self.pasteButton = Button(self.textActionFrame, text = 'Pegar', command=self.pasteText)
        self.messageFrame = Frame(self.actionFrame)
        self.helpButton = Button(self.actionFrame, text = 'Ayuda', command=self.goToHelp)
        self.warningLabel = Label(self.messageFrame, anchor='w', textvariable=self.warningStr)
        self.warningStr.set('Estado: Cargando...')
        self.pdfNameLabel = Label(self.messageFrame, anchor='w', textvariable=self.pdfName)
        self.pdfName.set('Esperando PDF...')
        self.pdfNameLabel.config(bg='yellow')
        self.pathLabel = Label(self.mainFrame, anchor='w',  textvariable=self.pathStr)
        self.pathStr.set(f'Directorio: {str(self.destinationPath)}')
        self.pathLabel.config(bg='green')
        self.setWarings()

    def startWithPDF(self, file):
        self.uploadPDF(file)

    def askForPDF(self):
        file = askopenfilename()
        if file:
            self.uploadPDF(file)

    def askForPath(self):
        self.destinationPath = askdirectory()
        self.pathStr.set(f'Directorio: {str(self.destinationPath)}')

    def uploadPDF(self, file):
        try:
            self.inputpdf = PdfFileReader(open(file, "rb"))
            self.pathStr.set(f'Directorio: {pathlib.Path(file).parent.absolute()}')
            self.pdfName.set(f'PDF: {pathlib.Path(file).name}')
            self.pdfNameLabel.config(bg='green')
            self.textbox.delete('1.0', END)
            for i in range(self.inputpdf.numPages):
                self.textbox.insert(END, f"Página #{i+1}\n")
            self.setWarings()
            self.generateFilesButton['state'] = "normal"
        except:
            mb.showerror("Un error ocurrió", "Posiblemente el archivo que usted está intentando subir no es un archivo PDF, por favor reviselo. Si el error persiste, contacte a Deft Soluciones")

    def getTextInput(self):
        return [x for x in self.textbox.get("1.0","end").splitlines() if x]

    def setWarings(self, event=None):
        warnings = []
        warningMessage = ''
        if not self.inputpdf:
            warnings += ['Debe subir un archivo']
        if self.inputpdf and self.inputpdf.numPages > len(self.getTextInput()):
            n = self.inputpdf.numPages - len(self.getTextInput())
            warnings += [f'Faltan {n} nombres de páginas por indicar']
        if self.inputpdf and len(self.getTextInput()) > self.inputpdf.numPages:
            n = len(self.getTextInput()) - self.inputpdf.numPages
            warnings += [f'Sobran {n} nombres de páginas']
        if (warnings):
            self.generateFilesButton['state'] = 'disabled'
            self.warningLabel.config(bg='yellow')
        else:
            self.generateFilesButton['state'] = 'normal'
            self.warningLabel.config(bg='green')
        warningMessage = "\n".join(warnings) if warnings else 'Todo listo para generar sus PDF'
        self.warningStr.set(f'Estado: {warningMessage}')

    def clearText(self):
        self.textbox.delete('1.0', END)

    def copyText(self):
        self.textbox.clipboard_clear()
        self.textbox.clipboard_append(self.textbox.get("1.0","end"))

    def pasteText(self):
        self.textbox.delete('1.0', END)
        self.textbox.insert(END, self.textbox.clipboard_get())

    def goToHelp(self):
         webbrowser.open(
            'https://www.rethink.org/advice-and-information/about-mental-illness/learn-more-about-symptoms/worried-about-your-mental-health/',
            new=0, autoraise=True
        )

    def filePath(self, name):
        return str(self.destinationPath) + '/' + name + '.pdf'

    def packPDFPages(self):
        pagesNames = self.getTextInput()
        PDFPagesDict = {}
        for i in range(self.inputpdf.numPages):
            output = PdfFileWriter()
            if pagesNames[i] not in PDFPagesDict:
                PDFPagesDict[pagesNames[i]] = output
            PDFPagesDict[pagesNames[i]].addPage(self.inputpdf.getPage(i))
        return PDFPagesDict

    def replaceOmitCancel(self):
        duplicateFiles = 0
        answer = True
        for name, pdf in self.packPDFPages().items():
            if pathlib.Path(self.filePath(name)).is_file():
                duplicateFiles += 1
        if (duplicateFiles > 0):
            answer = mb.askyesnocancel(
                f'{duplicateFiles} Archivos duplicados',
                f'{duplicateFiles} de los PDFs que está intentando generar ya existen en el directorio \n {self.destinationPath} \n ¿Desea reemplazarlos?',
            )
        return answer

    def exportPDFPages(self):
        duplicateAction = self.replaceOmitCancel()
        if (duplicateAction is None):
            mb.showinfo(
                'Cancelado',
                'Sus PDFs NO han sido generados'
            )
            return 0
        pdfPack = self.packPDFPages().items()
        for name, pdf in pdfPack:
            if (duplicateAction or not pathlib.Path(self.filePath(name)).is_file()):
                with open(self.filePath(name), "wb") as outputStream:
                    pdf.write(outputStream)
        mb.showinfo(
            'Completado',
            f'{len(pdfPack)} PDFs han sido generados en el directorio {self.destinationPath}'
        )

    def render(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.mainFrame.grid(row=0, column=0, padx=10, pady=(25, 5), sticky=N+S+E+W)
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.textActionFrame.grid_rowconfigure(0, weight=1),
        self.textActionFrame.grid_columnconfigure(3, weight=1)
        self.editFrame.grid(row=0, column=0, sticky=N+S+E+W)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.textbox.pack(fill="both")
        self.textbox.config(yscrollcommand=self.scrollbar.set)
        self.textbox.bind("<Key>", self.setWarings)
        self.scrollbar.config(command=self.textbox.yview)
        self.actionFrame.grid(row=0, column=1, sticky=N+S+E+W)
        self.uploadButton.pack(fill='both')
        self.textActionFrame.pack(fill='both')
        self.clearButton.grid(row=0, column=0, sticky=N+S+E+W)
        self.copyButton.grid(row=0, column=1, sticky=N+S+E+W)
        self.pasteButton.grid(row=0, column=2, sticky=N+S+E+W)
        self.folderButton.pack(fill='both')
        self.generateFilesButton.pack(fill='both')
        self.messageFrame.pack(fill='both', pady=10)
        self.messageFrame.grid_rowconfigure(0, weight=1),
        self.messageFrame.grid_columnconfigure(1, weight=1)
        self.helpButton.pack(fill="y", side="bottom", anchor='se')
        self.warningLabel.pack(fill='both')
        self.pdfNameLabel.pack(fill='both')
        self.pathLabel.grid(row=1, column=0, sticky="ws", pady=10)
        self.root.mainloop()

pdfs = PDFSplitter()

if len(sys.argv) > 1:
    pdfs.startWithPDF(sys.argv[1])

pdfs.render()