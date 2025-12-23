
# entity/Yayinevi.py
class Yayinevi:
    def __init__(self, id=None, yayinevi_ismi=None):
        self.id = id
        self.yayinevi_ismi=yayinevi_ismi

    def __repr__(self):
        return f"<ID {self.id} (yayinevi_ismi: {self.yayinevi_ismi})>"