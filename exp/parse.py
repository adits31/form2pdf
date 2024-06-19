import PyPDF2
from PyPDF2.generic import NameObject, TextStringObject

# Script to extract a list of all structured form fields on a PDF.
# Replace pdf_path with a path to your desired PDF file.
def extract_form_fields(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        writer = set_need_appearances_writer(writer)
        write_val = "Read"

        fields = {}
        for page in reader.pages:
            page_number = reader.get_page_number(page)
            if "/Annots" in page:
                annotations = page["/Annots"]
                writer.add_page(page)
                for annot in annotations:
                    field = annot.get_object()
                    if field.get("/Subtype") == "/Widget":
                        field_name = field.get("/T")
                        field_type = field.get("/FT")
                        field_value = field.get("/V")
                        fields[field_name] = {
                            "type": field_type,
                            "value": field_value
                        }
                        writer.update_page_form_field_values(writer.pages[page_number - 1], {field_name: write_val})
        
        with open("updated_form.pdf", "wb") as output_stream:
            writer.write(output_stream)

        return fields

def set_need_appearances_writer(writer):
    try:
        catalog = writer._root_object
        # get the AcroForm tree
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)
            })

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        # del writer._root_object["/AcroForm"]['NeedAppearances']
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer

if __name__ == '__main__':
    pdf_path = './form.pdf'
    fields = extract_form_fields(pdf_path)

    for field_name, field_info in fields.items():
        print(f"Field Name: {field_name}")
        print(f"  Type: {field_info['type']}")
        print(f"  Value: {field_info['value']}")
