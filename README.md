# package_convert_pn13_to_fhir
Script Python permettant de convertir un prescription médicale au standard PN13 (fichier XML) en une ressource MedicationRequest au standard FHIR (fichier JSON).


## Crédit

Le mapping est basé sur celui d'Intérop'Santé (mise à jour du 05/05/2025) :
https://build.fhir.org/ig/Interop-Sante/hl7.fhir.fr.medication/ConceptMap-PN13-FHIR-prescmed-practitioner-identite-conceptmap.html
https://packages2.fhir.org/xig/hl7.fhir.fr.medication%7Ccurrent/ConceptMap/PN13-FHIR-prescmed-patient-id-seul-conceptmap
https://build.fhir.org/ig/Interop-Sante/hl7.fhir.fr.medication/ConceptMap-PN13-FHIR-prescmed-medicationnoncompound-conceptmap.html
https://build.fhir.org/ig/Interop-Sante/hl7.fhir.fr.medication/ConceptMap-PN13-FHIR-prescmed-practitioner-identite-conceptmap.html 


## 🧩 Fonctionnalités

- Lecture d'un fichiers PN13 en entrée
- Transformation de plusieurs champs pour leur intégration dans un fichier FHIR.
- Pour être exécuté, l'environnement du script doit contenir le fichier Excel qui représente la table de médicament et le fichiers CSV qui représente la table des voies d'administration. Ces derniers sont mis à jour si le code de la prescription n'est pas présent dans la table.
- Fait apparaitre un extrait des ressources Medication et Practitioner.
- Génération d'un fichier FHIR en sortie.



## 📦 Installation

### Cloner ce dépôt

```bash
git clone https://github.com/TDumetz/package_convert_pn13_to_fhir.git
cd package_convert_pn13_to_fhir
```

## Utilisation
- La version de votre python doit être supérieur ou égale à la 3.11.13
- L'environnement doit contenir le script, le fichier XML, le fichier Excel et le fichier CSV
