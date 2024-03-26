from typing import Set


class Product:

    def __init__(self,
                 name: str,
                 product_no: str,
                 vat_percent: str,
                 categories: Set[str],
                 unit_price_incl_vat: str
                 ):
        self.unit_price_incl_vat = unit_price_incl_vat
        self.categories = categories
        self.vat_percent = vat_percent
        self.product_no = product_no
        self.name = name

    def update_categories(self, categories: Set):
        self.categories = self.categories | categories
