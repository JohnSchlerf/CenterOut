from tkinter import Tk
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilenames
import os


def get_name(prompt="Name of Volunteer", default_value="Volunteer"):
    """Prompt for a subject's name using a dialog

    Parameters
    ----------
    prompt : string, optional
        Text above the text entry cell. IF not supplied, defaults to a
        generic "Name of Volunteer"

    default_value : string, optional
        The default value to put into the dialog. If not supplied, the
        default is "Volunteer"

    Returns
    -------
    subject_name : string
        Returns the value entered in the dialog
    """
    top = Tk()
    top.update()

    subject_name = askstring(
        '', prompt, parent=top, initialvalue=default_value
        )

    top.destroy()
    return subject_name


def get_target_files(directory="target_files"):
    """Quick prompt to load target files

    It's possible to select multiple, but the list will be sorted by the
    alphabetical order of filenames.

    Parameters
    ----------
    directory : string, optional
        A directory to look in for target files. The default is "target_files"

    Returns
    -------
    target_list : list(string)
        Returns a list of every file that was selected, in order.
    """
    top = Tk()
    top.update()
    # Path management
    orig_dir = os.path.abspath(os.curdir)
    os.chdir(directory)

    file_names = askopenfilenames(parent=top)

    top.destroy()
    os.chdir(orig_dir)

    return file_names



if __name__=="__main__":
    print(name_dialog())
