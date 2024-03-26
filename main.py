import config
import objects

from typing import Set
from lxml import etree

"""
Dict with product objects indexed with their ID
This ensures that the parts will be unique
"""
products_dict: dict[str: objects.Product] = {}

"""
Load the RelaxNG schema
"""
relaxng_schema = etree.RelaxNG(file=config.RELAXNG_SCHEMA_FILE)

"""
Iterate and parse the xmls

    output_elementTree = etree.parse(xml_path)  # <class 'xml.etree.ElementTree.ElementTree'>
    output_root_element = output_elementTree.getroot()  # <class 'xml.etree.ElementTree.Element'>
"""

for xml_path in config.xml_list:
    config.logger.info(f"Processing {xml_path}")
    input_ElementTree = etree.ElementTree(file=xml_path)  # ElementTree
    input_root = input_ElementTree.getroot()

    """
    1. split ./vehicle/name at / (if / in the NAME)
    """
    categories_from_vehicle_name: Set = set()

    if (name_element := input_root.find("./vehicle/name")) is not None:
        if len(split_name_at_slash := name_element.text.split('/')) > 1:
            categories_from_vehicle_name.add(split_name_at_slash[0].strip())
            categories_from_vehicle_name.add(split_name_at_slash[1].strip())
        else:
            categories_from_vehicle_name.add(name_element.text.strip())
    else:
        config.logger.error("./vehicle/name does not exists in the XML. Skipping the XML.")
        continue

    """
    Find all products in the XML
    """
    product_list = input_root.findall(".//product")

    for product in product_list:
        """
        Iterate the children elements of <PRODUCT> and get the data.
        """
        name: str = ""
        product_no: str = ""
        vat_percent: str = "0"
        unit_price_incl_vat: str = "0"

        for product_child in product.findall("./*"):
            """
            Check, if the following tags is in <product>. Skip product if not.
            """
            if product_child.text is not None:  # if the element value is empty, it messes up the RelaxNG validation
                match product_child.tag:
                    case "name":
                        name = product_child.text
                    case "product_no":
                        product_no = product_child.text
                    case "vat_percent":
                        vat_percent = product_child.text
                    case "unit_price_incl_vat":
                        unit_price_incl_vat = product_child.text

                    case _:
                        continue

            """
        Extract part categories. Iterate its ancestors and look for the <category> tag.
        """
        main_categories_set: Set[str] = set()
        for ancestor in etree.AncestorsIterator(product):
            if ancestor.tag == "category":
                # we need <category><name>
                if len(category_name := ancestor.findall("./name")) == 1:
                    main_categories_set.add(category_name[0].text)
                else:
                    config.logger.error(
                        "The category has more than one name tag. Skipping adding the category to the product.")

        """
        Check if the object with the product_no exists, and create it if not.
        """
        if product_no not in products_dict:
            products_dict[product_no] = objects.Product(name=name,
                                                        product_no=product_no,
                                                        vat_percent=vat_percent,
                                                        unit_price_incl_vat=unit_price_incl_vat,
                                                        categories=categories_from_vehicle_name | main_categories_set)
        else:
            # Just update the categories for the given product_no
            products_dict[product_no].update_categories(categories_from_vehicle_name | main_categories_set)
"""
Iterate the spare parts
1. find all product_nos
2. iterate product_nos 
    3. check if the product_no is in the output_xml tree
        - if yes, add categories
        - if not, add it and add categories
        - { product_no: ['category'] }
        - { product_no: name }
        - { product_no: vat_percent }
        - { product_no: unit_price_incl_vat } - if not present or empty -> 0
        - t.j. toto mozes zajebat do objektu "product"
    2. check their parents (if parent = category, then take the name and put it in the list
        - do this until None (or whatever is the root)
AncestorsIterator
"""



"""
Generate the output XML.

Create the root element SHOP for the output xml
"""
output_root = etree.Element("SHOP")  # <class 'lxml.etree._Element'>

for product in products_dict:
    product_object: objects.Product = products_dict[product]

    """
    <SHOPITEM>
        self.name = name
            - <NAME>
        self.categories = categories
            - <categories><category>
        self.unit_price_incl_vat = unit_price_incl_vat
            - <PRICE>
        self.vat_percent = vat_percent
            - <VAT>
        self.product_no = product_no
            - <EAN> (mandatory)


    """
    shopitem = etree.SubElement(output_root, "SHOPITEM")

    """
    <NAME>
    """
    if product_object.name != "":
        product_name = etree.SubElement(shopitem, "NAME")
        product_name.text = product_object.name
    """
    <EAN> (has to be first?)
    """
    product_ean = etree.SubElement(shopitem, "EAN")
    product_ean.text = product_object.product_no

    """
    <PRICE>
    """
    product_price = etree.SubElement(shopitem, "PRICE")
    product_price.text = product_object.unit_price_incl_vat

    """
    <VAT>
    """
    product_vat = etree.SubElement(shopitem, "VAT")
    product_vat.text = product_object.vat_percent

    """
    <categories><category>
    """
    product_categories = etree.SubElement(shopitem, "CATEGORIES")

    for category in product_object.categories:
        product_category = etree.SubElement(product_categories, "CATEGORY")
        product_category.text = category

output_ElementTree = etree.ElementTree(output_root)  # <class 'lxml.etree._ElementTree'>

"""
Validate the XML with RelaxNG and print its error.log
"""

relaxng_schema.validate(output_ElementTree)
config.logger.info(relaxng_schema.error_log)

"""
Write the validated tree to the output XML
"""
output_ElementTree.write(f"{config.OUTPUT_XML}", encoding='utf-8', pretty_print=True)
