from os import listdir

# i know this isn't the right way to do it but it works
__all__ = [p.split(".")[0] for p in listdir("handles") if not p.startswith("__")]