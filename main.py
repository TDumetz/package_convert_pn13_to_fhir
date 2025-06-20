import sys
from convert_pn13_to_fhir.convert_pn13_to_fhir import convert_pn13_to_fhir_file

def main():
    if len(sys.argv) != 3:
        print("Usage : python src/convert_pn13_to_fhir/main.py fichier_entree.xml fichier_sortie.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_pn13_to_fhir_file(input_file, output_file)

if __name__ == "__main__":
    main()
