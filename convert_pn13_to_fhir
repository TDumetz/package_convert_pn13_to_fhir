#!/usr/bin/env python3
# script_pn13_to_fhir_v27.py

# importations
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime
from typing import Optional
from typing import Union
import pandas as pd
import re



# 1) Mapping simples : un champ PN13 permet de remplir un champ FHIR
SIMPLE_MAPPING = {
    ".//Messages[@Phast-id_message]":('MedicationRequest.groupIdentifier.value'),
    ".//Prescription/Dh_prescription": ('authoredOn',),
    ".//Prescription/Unité_hébergement": ('supportingInformation', 0, 'identifier'),
    ".//Prescription/Unité_resp_médicale": ('supportingInformation', 1, 'identifier'),
    ".//Prescription/Commentaire": ("note", 0, "text"),
    ".//Prescription/Commentaire_structuré/Identification_auteur/Identifiant": ('note', 1, 'authorReference', 'identifier', 'value'),
    ".//Prescription/Commentaire_structuré/Texte": ("note", 3, "text"),
    ".//Prescription/Rens_compl/Valeur_rens_compl": ("note", 4, "text"),
    ".//Prescription/Elément_prescr_médic/Id_élément_prescr": ('identifier','value'),
    ".//Prescription/Elément_prescr_médic/Libellé_élément_prescr": ("note", 5, "text"),
    ".//Prescription/Elément_prescr_médic/Urgent": ('priority',),
    ".//Prescription/Elément_prescr_médic/Voie_administration": ('dosageInstruction', 'route', 'coding', 'code'),
    ".//Prescription/Elément_prescr_médic/Lieu_administration": ('dispenseRequest', 'performer', 'display'),
    ".//Prescription/Elément_prescr_médic/Dispositif_associé": ('supportingInformation', 'display'),
    ".//Prescription/Elément_prescr_médic/Posologie": ("note", 6, "text"),
    ".//Prescription/Elément_prescr_médic/Dh_début": ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'start',),
    ".//Prescription/Elément_prescr_médic/Dh_fin": ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'end',),
    ".//Prescription/Elément_prescr_médic/Indication": ('note', 7, 'text'),
    ".//Prescription/Elément_prescr_médic/Commentaire": ("note", 8, "text"),
    ".//Prescription/Elément_prescr_médic/Commentaire_structuré/Identification_auteur/Identifiant": ('note', 2, 'authorReference', 'identifier', 'value'),
    ".//Prescription/Elément_prescr_médic/Commentaire_structuré/Texte": ("note", 9, "text"),
    ".//Prescription/Elément_prescr_médic/GoNogo": ('status',),
    ".//Prescription/Elément_prescr_médic/Motif_attente": ('statusReason', 'text'),
    ".//Prescription/Elément_prescr_médic/Conditions_application": ('note', 10, 'text'),
    ".//Elément_posologie/Frq_échelle": ('dosageInstruction', 'timing', 'repeat', 'periodUnit'),
    ".//Elément_posologie/Fréquence_structurée/Frq_durée": ('dosageInstruction', 'timing', 'repeat', 'period'),
    ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_1_J": ('dosageInstruction', 'timing', 'repeat', 'dayOfWeek'),
    ".//Elément_posologie/Fréquence_structurée/Frq_multiplicité": ('dosageInstruction', 'timing', 'repeat', 'frequency'),
    ".//Elément_posologie/Fréquence_structurée/Frq_libellé": ('dosageInstruction', 'text'),
    ".//Elément_posologie/Fréquence_structurée/Frq_libellé": ('dosageInstruction', 'text'),
    ".//Elément_posologie/Int_temps_ev_début": ('dosageInstruction', 'timing', 'repeat', 'offset'),
    ".//Elément_posologie/Quantité/Nombre": ('dosageInstruction', 'doseAndRate', 'doseQuantity', 'value'),
    ".//Elément_posologie/Quantité/Unité": ('dosageInstruction', 'doseAndRate', 'doseQuantity', 'code'),
    ".//Elément_posologie/Débit/Nombre": ('dosageInstruction', 'doseAndRate', 'rateQuantity', 'value'),
    ".//Elément_posologie/Débit/Unité": ('dosageInstruction', 'doseAndRate', 'rateQuantity', 'code'),
    ".//Prescription/Elément_prescr_médic/Composant_prescrit/Non_substituable": ('substitution', 'allowedBoolean'),
    ".//Prescription/Elément_prescr_médic/Composant_prescrit/Référent_poso": ('dosageInstruction', 'doseAndRate', 'extension', 'valueReference'),
    ".//Séjour/Id_séjour" : ('encounter', 'identifier', 'value'),
    ".//Patient/Ipp":('subject', 'identifier', 'value'),
}

# 2) Mappings composites : plusieurs champs du PN13 vont permettre de créer un champ FHIR
COMPOSITE_MAPPING = {
  (
    ".//Prescription/Commentaire_structuré/Identification_auteur/Nom_usage",
    ".//Prescription/Commentaire_structuré/Identification_auteur/Prénom_usage",
    ".//Prescription/Commentaire_structuré/Identification_auteur/Titre",
  ):('note', 1, 'authorReference', 'display'),
  (".//Prescription/Elément_prescr_médic/Commentaire_structuré/Identification_auteur/Nom_usage",
    ".//Prescription/Elément_prescr_médic/Commentaire_structuré/Identification_auteur/Prénom_usage",
    ".//Prescription/Elément_prescr_médic/Commentaire_structuré/Identification_auteur/Titre",
  ): ('note', 2, 'authorReference', 'display'),
    (".//Patient/Nom_usuel",
    ".//Patient/Prénoms"): ('subject', 'display'),
    (".//Elément_posologie/Int_temps_év_début/Nombre",
     ".//Elément_posologie/Int_temps_év_début/Unité"
    ): ("dosageInstruction", "timing", "repeat", "offset")
}

# 3) Mappings statiques : champs qui n'existent pas dans le PN13 donc directement injecté dans le FHIR
STATIC_MAPPING = {
    ("intent",): "order",
}


# 4) Mapping conditionnel : on injecte target_path si condition_path vide
#    Chacun peut avoir son propre PN13 XPath, condition FHIR et cible FHIR

CONDITIONAL_MAPPING = [
    {
        'pn13_xpath': ".//Prescription/Rens_compl",#champ à injecter
        'condition_path': ('note', 4, 'text'),#si ce champ est vide
        'target_path': ('supportingInformation', 'reference'),#dans ce champ
    },
    {
      'pn13_xpath': ".//Prescription/Elément_prescr_médic/Dh_début_prescrite",
      'condition_path': ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'start',),
      'target_path': ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'start',),
    },
    {
      'pn13_xpath': ".//Prescription/Elément_prescr_médic/Dh_fin_prescrite",
      'condition_path': ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'end',),
      'target_path': ('dosageInstruction', 'timing', 'repeat', 'boundsPeriod', 'end',),
    }
]

#mapping de la ressource medication
COMPONENT_MAPPINGS = {
    "Code_composant_1": ('code', 'coding', 0, 'code'),
    "Libellé_composant":('code', 'text'),
    ".//Prescription/Elément_prescr_médic/Forme": ('form', 'coding', 'code'),
    ".//Prescription/Elément_prescr_médic/Fourniture": ('valueBoolean',),
    }


# mapping des valeures du PN13 vers les valeurs du FHIR de la fréquence → (frequency, period, periodUnit)
FREQ_MAP = {
    "TLJ":   (1, 1, "d"),     # 1 fois par 1 jour
    ("1000000","0100000","0010000","0001000","0000100","0000010","0000001"):   (1, 7, "d"),#1 fois par semaine sans prendre en compte quel est le jour
}


# 5) Transformations spécifiques des champs PN13 avant de les injecter dans le FHIR

#fonction de transformation du format de la date
def format_dateTime(datetime_str: Optional[str]) -> Optional[str]:
    """
    Transforme une chaîne 'YYYYMMDDHHMMSS' en 'YYYY-MM-DDTHH:MM:SS'.
    Retourne la chaîne brute dès qu’elle ne fait pas exactement 14 chiffres.

    :param datetime_str: chaîne 'YYYYMMDDHHMMSS'
    :return: chaîne ISO ou chaîne brute si conditions non remplies
    """
    # 0) On ne touche pas aux valeurs None
    if datetime_str is None:
        return None

    # 1) On ne touche qu’aux strings ; sinon on renvoie tel quel
    if not isinstance(datetime_str, str):
        return datetime_str

    s = datetime_str.strip()

    # 2) On exige exactement 14 caractères tous chiffres,
    #    sinon on renvoie la chaîne brute immédiatement
    if len(s) != 14 or not s.isdigit():
        return datetime_str

    # 3) Parsing strict (devrait marcher si on a 14 chiffres)
    try:
        dt = datetime.strptime(s, "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # En théorie on n’y arrive pas, mais on reste safe
        return datetime_str


#donne une valeur au champ "priority" dans le FHIR à parti de "Urgent" dans le PN13
def format_priority(flag_str: str):
  flag = flag_str.strip()
  if flag == "true":
    return "urgent"
  if flag == "false":
    return "routine"


#fonction pour transformer les valeurs des booléens
def format_boolean(flag_str: str) -> Union[bool, str]:
    """
    Transforme une chaîne PN13 :
      '1' → True
      '0' → False
    Dans tous les autres cas, renvoie la chaîne brute telle quelle.
    """
    if flag_str is None:
        return None
    raw = flag_str  # on garde la version originale
    f = raw.strip()
    if f == "1":
        return True
    if f == "0":
        return False
    # Fallback : renvoie la chaîne brute non modifiée
    return raw


#donne une valeur au champ "status" dans le FHIR à parti de "GONOGO" dans le PN13
def format_status(flag_str: Optional[str]) -> Optional[Union[str, bool]]:
    """
    Transforme le code PN13 de GONOGO en status FHIR :
      '0' -> 'unknown'
      '1' -> 'on-hold'
      '2' -> 'active'
      '3' -> 'active'
      '4' -> 'cancelled'

    Si flag_str est None ou vide → renvoie None (aucune clé créée).
    Si flag_str n'est pas l'un de ces codes → renvoie la chaîne brute.
    """
    if flag_str is None:
        return None
    raw = flag_str  # on conserve la version originale
    flag = raw.strip()
    if not flag:
        # champ absent ou vide en PN13 → on ne crée pas la clé FHIR
        return None

    mapping = {
        "0": "unknown",
        "1": "on-hold",
        "2": "active",
        "3": "active",
        "4": "cancelled",
    }
    # si c'est un code connu, on retourne la valeur FHIR
    if flag in mapping:
        return mapping[flag]
    # sinon, on retourne raw tel quel pour l'injecter dans le FHIR
    return raw

#donne une valeur au champ "periodUnit" ou "period" dans le FHIR à parti de "Frq_échelle" dans le PN13
def format_frq_echelle(flag_str: Optional[str]) -> Optional[Union[str, bool]]:
    """
    Transforme le code PN13 de Frq_échelle en DosageInstruction.timing.repeat.periodUnit FHIR :
      '1' -> 's'
      '2' -> 'min'
      '3' -> 'h'
      '4' -> 'd'
      '5' -> 'wk'
      '6' -> 'mo'
      '7' -> 'a'

    Si flag_str est None ou vide → renvoie None (aucune clé créée).
    Si flag_str n'est pas l'un de ces codes → renvoie la chaîne brute.
    """
    if flag_str is None:
        return None
    raw = flag_str  # on conserve la version originale
    flag = raw.strip()
    if not flag:
        # champ absent ou vide en PN13 → on ne crée pas la clé FHIR
        return None

    mapping = {
        "1": "s",
        "2": "min",
        "3": "h",
        "4": "d",
        "5": "wk",
        "6": "mo",
        "7": "a",
    }
    # si c'est un code connu, on retourne la valeur FHIR
    if flag in mapping:
        return mapping[flag]
    # sinon, on retourne raw tel quel pour l'injecter dans le FHIR
    return raw


#donne une valeur au champ "dayOfWeek" dans le FHIR à parti de "Frq_filtreVal_1_J" dans le PN13
def format_frq_filtreVal_1_J(flag_str: Optional[str]) -> Optional[Union[str, bool]]:
    """
    Transforme le code PN13 de Frq_échelle en DosageInstruction.timing.repeat.periodUnit FHIR :
      '1' -> 'mon'
      '2' -> 'tue'
      '3' -> 'wed'
      '4' -> 'thu'
      '5' -> 'fri'
      '6' -> 'sat'
      '7' -> 'sun'

    Si flag_str est None ou vide → renvoie None (aucune clé créée).
    Si flag_str n'est pas l'un de ces codes → renvoie la chaîne brute.
    """
    if flag_str is None:
        return None
    raw = flag_str  # on conserve la version originale
    flag = raw.strip()
    if not flag:
        # champ absent ou vide en PN13 → on ne crée pas la clé FHIR
        return None

    mapping = {
        "1": "mon",
        "2": "tue",
        "3": "wed",
        "4": "thu",
        "5": "fri",
        "6": "sat",
        "7": "sun",
    }
    # si c'est un code connu, on retourne la valeur FHIR
    if flag in mapping:
        return mapping[flag]
    # sinon, on retourne raw tel quel pour l'injecter dans le FHIR
    return raw


#fonction pour transformer de façon inversé les valeurs des booléens
def format_boolean_inverse(flag_str: str) -> bool:
    """
    '1' -> False, '0' -> True. Retourne None pour autres.
    """
    f = flag_str.strip()
    if f == "1":
        return False
    if f == "0":
        return True
    return None

#fonction qui renvoie None si l'unité de la quantité est "dose"
def filter_dose_unit(raw: str) -> Optional[str]:
    """
    Retourne None si l’unité est 'dose' (non injectée dans FHIR),
    sinon retourne la chaîne nettoyée.
    """
    if not raw:
        return None
    value = raw.strip().lower()
    if value == "dose":
        return None  # Ne pas injecter
    return raw.strip()

#fonction qui renvoie None si l'unité du débit est "dose"
def filter_debit_unit(raw: str) -> Optional[str]:
    """
    Retourne None si l’unité est 'dose' (non injectée dans FHIR),
    sinon retourne la chaîne nettoyée.
    """
    if not raw:
        return None
    value = raw.strip().lower()
    if value == "dose":
        return None  # Ne pas injecter
    return raw.strip()


#préfixes rajoutés devant la valeur des champs
def prefix_comment(raw: str) -> str:
    return f"Commentaire sur la prescription: {raw.strip()}"

def prefix_element_prescrit(raw: str) -> str:
    return f"Libellé textuel du médicament: {raw.strip()}"

def prefix_posologie(raw: str) -> str:
    return f"Libellé textuel de la posologie: {raw.strip()}"

def prefix_indication(raw: str) -> str:
    return f"Indication sur la ligne de prescription: {raw.strip()}"

def prefix_comment2(raw: str) -> str:
    return f"Commentaire sur la ligne de prescription: {raw.strip()}"


def prefix_application(raw: str) -> str:
    return f"Condition d'application sur la ligne de prescription: {raw.strip()}"


def prefix_patient_reference(raw: str) -> str:
    """
    Transforme 'Ipp' → 'Patient/Ipp'
    """
    return f"Patient/{raw.strip()}"


# Application des fonctions de transformation aux champs sélectionnés
TRANSFORMS = {
    ".//Prescription/Dh_prescription": format_dateTime,
    ".//Prescription/Elément_prescr_médic/Dh_début_prescrite": format_dateTime,
    ".//Prescription/Elément_prescr_médic/Dh_début": format_dateTime,
    ".//Prescription/Elément_prescr_médic/Dh_fin_prescrite": format_dateTime,
    ".//Prescription/Elément_prescr_médic/Dh_fin": format_dateTime,
    ".//Prescription/Commentaire":prefix_comment,
    ".//Prescription/Commentaire_structuré/Texte":prefix_comment,
    ".//Prescription/Elément_prescr_médic/Libellé_élément_prescr":prefix_element_prescrit,
    ".//Prescription/Elément_prescr_médic/Posologie":prefix_posologie,
    ".//Prescription/Elément_prescr_médic/Indication":prefix_indication,
    ".//Prescription/Elément_prescr_médic/Commentaire":prefix_comment2,
    ".//Prescription/Elément_prescr_médic/Commentaire_structuré/Texte":prefix_comment2,
    ".//Prescription/Elément_prescr_médic/Conditions_application":prefix_application,
    ".//Elément_posologie/Frq_échelle":format_frq_echelle,
    ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_1_J":format_frq_filtreVal_1_J,
    ".//Prescription/Elément_prescr_médic/Composant_prescrit/Non_substituable": format_boolean_inverse,
    ".//Patient/Ipp":prefix_patient_reference,
    ".//Elément_posologie/Quantité/Unité":filter_dose_unit,
    ".//Elément_posologie/Débit/Unité":filter_debit_unit,
}

# Application des fonctions de transformation aux champs sélectionnés (pour la ressource Medication)
COMPONENT_TRANSFORMS = {
    ".//Prescription/Elément_prescr_médic/Fourniture":format_boolean,
}

# Fonctions utilitaires pour lecture et injection
def set_deep(d: dict, path, value):
    """
    Injecte `value` dans `d` selon `path`.
    - Si `path` est une chaîne, convertit-la en tuple.
    - Un segment int désigne un index de liste.
    - Un segment str désigne une clé de dict.
    """
    # Normalisation du chemin
    if isinstance(path, str):
        path = (path,)
    cur = d
    for i, key in enumerate(path):
        is_last = (i == len(path) - 1)
        if isinstance(key, int):
            # Doit être une liste
            if not isinstance(cur, list):
                raise TypeError(f"Expected list at segment {key}, got {type(cur)}")
            # Étendre la liste
            while len(cur) <= key:
                cur.append({})
            if is_last:
                cur[key] = value
            else:
                cur = cur[key]
        else:
            # Doit être un dict
            if not isinstance(cur, dict):
                raise TypeError(f"Expected dict at segment '{key}', got {type(cur)}")
            if is_last:
                cur[key] = value
            else:
                # Préparer le container suivant selon segment suivant
                next_key = path[i+1]
                if isinstance(next_key, int):
                    cur = cur.setdefault(key, [])
                else:
                    cur = cur.setdefault(key, {})


#Fonction pour donner une valeur au champ ("groupIdentifier","value") si il est vide
def set_group_identifier_from_filename(fhir: dict, filename: str):
    """
    Si fhir['groupIdentifier']['value'] est absent ou vide,
    extrait du nom de fichier les chiffres qui suivent le dernier '_'
    et les place dans groupIdentifier.value.
    """
    # 1) Si groupIdentifier.value existe et n'est pas vide, on ne touche à rien
    gi = fhir.get("groupIdentifier")
    if gi and gi.get("value", "").strip():
        return

    # 2) Nom du fichier sans chemin
    basename = os.path.basename(filename)

    # 3) Cherche toutes les occurrences d'underscore suivi de chiffres
    matches = re.findall(r'_(\d+)', basename)
    if not matches:
        return  # Rien trouvé

    # 4) Prend la DERNIÈRE séquence trouvée
    group_value = matches[-1]

    # 5) Initialise le champ si besoin
    if "groupIdentifier" not in fhir or not isinstance(fhir["groupIdentifier"], dict):
        fhir["groupIdentifier"] = {}

    # 6) Affecte la valeur
    fhir["groupIdentifier"]["value"] = group_value


#fonction pour ajouter un champ avec la valeur "system" si un autre champ est non vide
def add_system_if_code(fhir: dict,
                       code_path: tuple,
                       system_url: str):
    """
    Si code_path existe et non vide, injecte system_url dans
    le même coding[index]['system'].
    """
    try:
        # Descend dans le dict/list selon code_path
        cur = fhir
        for seg in code_path:
            cur = cur[seg]
    except (KeyError, IndexError, TypeError):
        return  # chemin introuvable → rien à faire

    # cur est la valeur de code_path
    if not isinstance(cur, str) or not cur.strip():
        return

    # On remonte pour construire le chemin system
    system_path = code_path[:-1] + ("system",)
    set_deep(fhir, system_path, system_url)


#fonction pour ajouter "device" si le champ dispositif associé prend une valeur
def add_device_if_dispositif(fhir: dict,
                             root: ET.Element,
                             pn13_xpath: str = ".//Prescription/Elément_prescr_médic/Dispositif_associé",
                             fhir_path: tuple = ("supportingInformation", "type"),
                             device_value: str = "device"):
    """
    Si la balise PN13 Dispositif_associé a une valeur non vide,
    injecte dans `fhir` à `fhir_path` la valeur `device_value`.
    """
    raw = root.findtext(pn13_xpath, default="").strip()
    if not raw:
        return
    set_deep(fhir, fhir_path, device_value)


#fonction pour ajouter "Patient" si le champ Ipp associé prend une valeur
def add_type_if_patient(fhir: dict,
                             root: ET.Element,
                             pn13_xpath: str = ".//Patient/Ipp",
                             fhir_path: tuple = ('subject', 'type'),
                             value: str = "Patient"):
    """
    Si la balise PN13 Ipp a une valeur non vide,
    injecte dans `fhir` à `fhir_path` la valeur `value`.
    """
    raw = root.findtext(pn13_xpath, default="").strip()
    if not raw:
        return
    set_deep(fhir, fhir_path, value)


#fonction pour ajouter "usual" si le champ Ipp associé prend une valeur
def add_use_if_patient(fhir: dict,
                             root: ET.Element,
                             pn13_xpath: str = ".//Patient/Ipp",
                             fhir_path: tuple = ('subject', 'identifier', 'use'),
                             value: str = "usual"):
    """
    Si la balise PN13 Ipp a une valeur non vide,
    injecte dans `fhir` à `fhir_path` la valeur `value`.
    """
    raw = root.findtext(pn13_xpath, default="").strip()
    if not raw:
        return
    set_deep(fhir, fhir_path, value)


#fonction qui permet d'ajouter l'extension que l'on souhaite au champ que l'on souhaite
def add_field_extension(fhir: dict,
                        field_path: tuple,
                        extension: dict):
    """
    Parcourt le champ indiqué ; si sa valeur existe et n'est pas vide,
    ajoute `extension` dans une liste fhir[...]...["extension"].
    Si le champ était déjà un dict unique, on le wrappe en liste.
    """
    # 1) Navigation jusqu’au parent et à la clé finale
    parent = fhir
    for seg in field_path[:-1]:
        if isinstance(seg, int):
            if not isinstance(parent, list) or seg >= len(parent):
                return
            parent = parent[seg]
        else:
            if not isinstance(parent, dict) or seg not in parent:
                return
            parent = parent[seg]

    key = field_path[-1]
    # 2) Récupère la valeur
    if isinstance(key, int):
        if not isinstance(parent, list) or key >= len(parent):
            return
        val = parent[key]
    else:
        val = parent.get(key)

    # 3) N’injecte que si non vide
    if val is None:
        return
    if isinstance(val, str) and not val.strip():
        return
    if isinstance(val, dict) and not val:
        return

    # 4) Prépare la liste d’extensions existante ou nouvelle
    #    Peut-être déjà un dict, peut-être une liste, peut-être absent
    if isinstance(val, dict):
        raw_ext = val.get("extension")
        if raw_ext is None:
            exts = []
        elif isinstance(raw_ext, list):
            exts = raw_ext
        else:
            # wrappe le dict existant dans une liste
            exts = [raw_ext]
        # y ajoute la nouvelle extension
        exts.append(extension)
        # réaffecte la liste dans la clé
        val["extension"] = exts

    else:
        # cas primitif → champ compagnon "_key"
        ext_holder_key = f"_{key}"
        holder = parent.setdefault(ext_holder_key, {})
        raw_ext = holder.get("extension")
        if raw_ext is None:
            exts = []
        elif isinstance(raw_ext, list):
            exts = raw_ext
        else:
            exts = [raw_ext]
        exts.append(extension)
        holder["extension"] = exts


#Base Excel du médicament
EXCEL_PATH = "./table_test_conversion_UI.xlsx"

# ─── 3) Vérifie que le fichier existe ────────────────────────────────────
if not os.path.isfile(EXCEL_PATH):
    raise FileNotFoundError(f"Le fichier Excel n’a pas été trouvé : {EXCEL_PATH!r}")

# ─── 4) Votre fonction de chargement / mise à jour de la table ────────────
def load_med_table(xlsx_path: str,
                   code_col: str = "UCD13",
                   label_col: str = "PRODUIT") -> dict:
    df = pd.read_excel(xlsx_path, dtype=str).fillna("")
    return {
        row[code_col].strip(): row[label_col].strip()
        for _, row in df.iterrows()
        if row[code_col].strip()
    }


#Fonction pour mettre à jour la base de donnée du médicament si le code UCD du médicament n'est pas déjà présent
def ensure_med_in_table(code: str,
                        label: str,
                        code_col: str = "UCD13",
                        label_col: str = "PRODUIT"):
    """
    Utilise EXCEL_PATH défini ci-dessus pour vérifier/ajouter une ligne.
    """
    df = pd.read_excel(EXCEL_PATH, dtype=str)
    if code in df[code_col].astype(str).values:
        return
    new = {c: "" for c in df.columns}
    new[code_col]  = code
    new[label_col] = label
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
    print(f"Attention un médicament a été ajouté au fichier {os.path.basename(EXCEL_PATH)} : {code} → {label}")

# ─── 5) Chargez la table en mémoire si besoin ─────────────────────────────
MED_MAPPING = load_med_table(EXCEL_PATH)

#Fonction pour créer la ressource medication et rajouter les champs relatif au médicament dedans
def map_repeated_composants(root: ET.Element,
                            fhir: dict,
                            base_xpath: str,
                            component_mappings: dict,
                            component_transforms: dict = None):
    contained = fhir.setdefault("contained", [])
    comps = root.findall(base_xpath)

    for idx, comp in enumerate(comps, start=1):
        # Récupération du code et du libellé PN13
        code_pn13  = (comp.findtext("Code_composant_1", "") or "").strip()
        label_pn13 = (comp.findtext("Libellé_composant", "") or "").strip()

        # Définir l'id de la medication = code_pn13 si dispo, sinon fallback
        med_id = code_pn13 if code_pn13 else f"med{idx}"

        med = {
            "resourceType": "Medication",
            "id": med_id
        }

        # Met à jour la base médicament si le code n’est pas déjà présent
        ensure_med_in_table(code_pn13, label_pn13)

        # Injection des autres mappings
        for pn13_xpath, fhir_paths in component_mappings.items():
            paths = [fhir_paths] if isinstance(fhir_paths, tuple) else fhir_paths
            if pn13_xpath.startswith("/") or pn13_xpath.startswith(".//"):
                elements = root.findall(pn13_xpath)
            else:
                elements = comp.findall(pn13_xpath)

            for el in elements:
                raw = (el.text or "").strip()
                if not raw:
                    continue

                if component_transforms and pn13_xpath in component_transforms:
                    raw = component_transforms[pn13_xpath](raw)
                    if raw is None:
                        continue

                for p in paths:
                    set_deep(med, p, raw)

        # Ajoute systématiquement med["code"]["coding"][0]["system"] si manquant
        coding_list = med.get("code", {}).get("coding", [])
        for coding in coding_list:
            if "system" not in coding or not coding["system"].strip():
                coding["system"] = "http://data.esante.gouv.fr/ansm/medicament/UCD"

        contained.append(med)

#création de l'extension de fourniture dans Medication 
MY_EXTENSION = {
    "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medication-to-dispense"
}

#Fonction pour créer la ressource practitioner et rajouter les champs relatif au praticien dedans
def map_repeated_practitioners(root: ET.Element,
                                fhir: dict,
                                base_xpath: str,
                                practitioner_mappings: dict,
                                practitioner_transforms: dict = None):
    """
    Crée des ressources Practitioner et ajoute automatiquement une référence
    dans MedicationRequest.requester vers le premier Practitioner inséré.
    """
    contained = fhir.setdefault("contained", [])
    practs = root.findall(base_xpath)

    # Trouver où insérer après les Medication
    insert_index = len(contained)
    for i, res in enumerate(contained):
        if res.get("resourceType") == "Medication":
            insert_index = i + 1

    first_practitioner_id = None

    for idx, pr in enumerate(practs, start=1):
        practitioner_id = f"pract{idx}"
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id
        }

        for pn13_xpath, fhir_paths in practitioner_mappings.items():
            paths = [fhir_paths] if isinstance(fhir_paths, tuple) else fhir_paths

            if pn13_xpath.startswith("/") or pn13_xpath.startswith(".//"):
                elements = root.findall(pn13_xpath)
            else:
                elements = pr.findall(pn13_xpath)

            for el in elements:
                raw = (el.text or "").strip()
                if not raw:
                    continue

                if practitioner_transforms and pn13_xpath in practitioner_transforms:
                    raw = practitioner_transforms[pn13_xpath](raw)
                    if raw is None:
                        continue

                for p in paths:
                    set_deep(practitioner, p, raw)

        # Insère dans contained
        contained.insert(insert_index, practitioner)
        insert_index += 1

        # Mémoriser le premier practitionner ajouté
        if first_practitioner_id is None:
            first_practitioner_id = practitioner_id

    # Si au moins un praticien a été ajouté, on le lie dans MedicationRequest
    if first_practitioner_id:
        fhir["requester"] = {
            "reference": f"#{first_practitioner_id}"
        }


#Base CSV des voies d'administration
CSV_PATH = "./table_test_voies_administration.csv"

# ─── 3) Vérifie que le fichier existe ────────────────────────────────────
if not os.path.isfile(CSV_PATH):
    raise FileNotFoundError(f"Le fichier CSV n’a pas été trouvé : {CSV_PATH!r}")

# ─── 4) Fonction de chargement de la table CSV ────────────────────────────
def load_voie_table(csv_path: str,
                    code_col:  str = "VOIE",      # nom exact trouvé
                    label_col: str = "LIBELLE") -> dict:
    df = pd.read_csv(csv_path, dtype=str, encoding="latin-1").fillna("")
    mapping = {}
    for _, row in df.iterrows():
        raw_code = (row.get(code_col) or "").strip()
        raw_lbl  = (row.get(label_col) or "").strip()
        if raw_code:
            mapping[raw_code] = raw_lbl
    return mapping

# ─── 5) Fonction pour mettre à jour la table si un code n’est pas présent ─
def update_voie_table(code: str,
                      label: str,
                      code_col:  str = "VOIE",
                      label_col: str = "LIBELLE"):
    """
    Vérifie si `code` est dans la colonne `code_col` du CSV.
    Si absent, ajoute une nouvelle ligne {code_col: code, label_col: label}.
    """
    df = pd.read_csv(CSV_PATH, dtype=str, encoding="latin-1").fillna("")
    # Utilise row.get pour éviter KeyError
    if code in df[code_col].astype(str).values:
        return
    new_row = {c: "" for c in df.columns}
    new_row[code_col]  = code
    new_row[label_col] = label
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False, encoding="latin-1")
    print(f"Attention une voie d'administration a été ajouté au fichier {os.path.basename(CSV_PATH)} : {code} → {label}")


# ─── 6) Chargez la table en mémoire si besoin ─────────────────────────────
VOIE_MAPPING = load_voie_table(CSV_PATH)

#fonction pour adapter le format de <Durée><Nombre>…</Nombre><Unité>…</Unité></Durée> pour qu'il soit accepté au standard FHIR
def parse_duration(nombre: str, unite: str) -> dict:
    """
    À partir de <Durée><Nombre>…</Nombre><Unité>…</Unité></Durée>,
    renvoie {"duration": x, "durationUnit": u} conforme à FHIR.

    - Si unite == "HHMM", on lit nombre comme HHMM (ex. "0800" → 8 h).
       • 0800 → 8 h
       • 0830 → 8 h et 30 min (480+30 = 510 min)
    - Sinon, on essaie d’interpréter unite comme ‘h’, ‘min’, ‘d’, etc.
    """
    raw_num  = (nombre or "").strip()
    raw_unit = (unite  or "").strip().upper()

    # Cas spécial HHMM
    if raw_unit == "HHMM" and len(raw_num) == 4 and raw_num.isdigit():
        h = int(raw_num[:2])
        m = int(raw_num[2:])
        if m == 0:
            return {"duration": h, "durationUnit": "h"}
        total_min = h * 60 + m
        return {"duration": total_min, "durationUnit": "min"}

    # Cas spécial MMSS
    if raw_unit == "MMSS" and len(raw_num) == 4 and raw_num.isdigit():
        m = int(raw_num[:2])
        s = int(raw_num[2:])
        if s == 0:
            return {"duration": m, "durationUnit": "min"}
        total_s = m * 60 + s
        return {"duration": total_s, "durationUnit": "s"}

    # Sinon, tentative de conversion nombre + unité
    # 1) convertir le nombre en float/int
    try:
        if "," in raw_num:
            val = float(raw_num.replace(",", "."))
        elif "." in raw_num:
            val = float(raw_num)
        else:
            val = int(raw_num)
    except Exception:
        # on garde la chaîne brute si échec
        return {"duration": raw_num, "durationUnit": unite}

    # 2) normaliser l’unité en code FHIR à partir des codes de l'UCUM
    u = raw_unit.lower()
    unit_map = {
        "s":"s", "seconde":"s", "secondes":"s", "sec":"s", "second":"s", "seconds":"s", "S":"s", "SS":"s",
        "min": "min", "mn": "min", "minute": "min", "minutes": "min", "M":"min", "MM":"min",
        "h": "h", "heure": "h", "heures": "h", "hour":"h", "hours":"h", "H":"h", "HH":"h",
        "d": "d", "j": "d", "jour": "d", "jours": "d", "days" :"d", "day":"d", "J":"d", "JJ":"d",
        "wk": "wk", "week":"wk", "weeks":"wk", "sem": "wk","semaine":"wk","semaines":"wk", 
        "mo": "mo", "month": "mo", "months": "mo", "mois":"mo",
        "a": "a","an":"a","ans":"a","année":"a","années":"a", "year":"a", "years":"a"
    }
    code = unit_map.get(u, unite)
    return {"duration": val, "durationUnit": code}


#Fonction pour transformer la valeur de la Fréquence en PN13 vers les champs frequency, period et periodUnit
def inject_timing_from_pn13(med: dict, raw: str):
    """
    Si freq_pn13 correspond à une clé de FREQ_MAP, 
    injecte dans fhir['dosageInstruction']['timing'] 
    les trois champs frequency, period, periodUnit.
    """
    if not raw or raw not in FREQ_MAP:
        return
    freq, period, unit = FREQ_MAP[raw]
    repeat = med.setdefault("dosageInstruction", {}) \
                .setdefault("timing", {})        \
                .setdefault("repeat", {})
    repeat["frequency"]  = freq
    repeat["period"]     = period
    repeat["periodUnit"] = unit


#fonction pour intégrer tous les champs concernant le jour et l'heure de prise du médicament
def map_structured_frequency(root: ET.Element, fhir: dict):
    """
    Parcourt tous les filtres sous
      <Elément_posologie>
        <Fréquence_structurée>
          <Frq_filtre>
            <Frq_filtreVal_1_N>…</Frq_filtreVal_1_N>
            <Frq_filtreVal_2>…</Frq_filtreVal_2>
            …
            <Frq_filtreVal_6>…</Frq_filtreVal_6>
          </Frq_filtre>
        </Fréquence_structurée>
      </Elément_posologie>

    Au lieu de créer une liste de dosageInstruction, ce code :
    1) S’assure que fhir["dosageInstruction"] est un dict unique.
    2) Récupère l’éventuel periodUnit déjà présent (issu du mapping Frq_échelle).
    3) Applique (et écrase si nécessaire) chaque filtre l’un après l’autre 
       dans le même "timing.repeat" de ce dict.
    4) Si plusieurs filtres apparaissent, le dernier en date prend le pas, 
       mais fhir["dosageInstruction"] reste toujours un dict.
    """

    # ─── 1) S’assurer que dosageInstruction est un dict ────────────────
    di_root = fhir.get("dosageInstruction")
    if not isinstance(di_root, dict):
        # Si c’était une liste ou autre, on remplace par un dict tout neuf.
        di_root = {"timing": {"repeat": {}}}
        fhir["dosageInstruction"] = di_root

    # À partir d’ici, di_root est forcément un dict.
    repeat_root = di_root.setdefault("timing", {}).setdefault("repeat", {})

    # ─── 2) Extraire eventuel periodUnit déjà mappé par Frq_échelle ────
    existing_period_unit = repeat_root.get("periodUnit")

    # ─── 3) Parcours de chaque filtre, en écrasant successivement ──────

    # 3.1) Frq_filtreVal_1_N → “jour de la semaine”
    for el1 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_1_N"
    ):
        raw1 = (el1.text or "").strip()
        if not raw1.isdigit():
            continue
        day_index = int(raw1)

        # On réinitialise le bloc repeat pour ce filtre
        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "wk"

        dow_map = {
            1: "mon", 2: "tue", 3: "wed", 4: "thu",
            5: "fri", 6: "sat", 7: "sun"
        }
        repeat_root["dayOfWeek"] = [dow_map.get(day_index, "mon")]
        repeat_root["frequency"] = 1
        repeat_root["period"]    = 1
        # Si plusieurs Frq_filtreVal_1_N apparaissent, le dernier écrase.

    # 3.2) Frq_filtreVal_2 → “jour du mois”
    for el2 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_2"
    ):
        raw2 = (el2.text or "").strip()
        if not raw2.isdigit():
            continue
        jour_du_mois = int(raw2)

        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "mo"
        repeat_root["frequency"]  = 1
        repeat_root["period"]     = 1
        # Si l’on veut préciser “BYMONTHDAY”, on pourrait ajouter :
        # repeat_root["extension"] = [{
        #     "url": "http://hl7.org/fhir/StructureDefinition/Timing-rrule",
        #     "valueString": f"FREQ=MONTHLY;BYMONTHDAY={jour_du_mois}"
        # }]

    # 3.3) Frq_filtreVal_3 → “jour de l’année”
    for el3 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_3"
    ):
        raw3 = (el3.text or "").strip()
        if not raw3.isdigit():
            continue
        jour_de_l_annee = int(raw3)

        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "a"
        repeat_root["frequency"]  = 1
        repeat_root["period"]     = 1
        # Pour “BYYEARDAY” :
        # repeat_root["extension"] = [{
        #     "url": "http://hl7.org/fhir/StructureDefinition/Timing-rrule",
        #     "valueString": f"FREQ=YEARLY;BYYEARDAY={jour_de_l_annee}"
        # }]

    # 3.4) Frq_filtreVal_4 → “numéro de la semaine”
    for el4 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_4"
    ):
        raw4 = (el4.text or "").strip()
        if not raw4.isdigit():
            continue
        semaine = int(raw4)

        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "a"
        repeat_root["frequency"]  = 1
        repeat_root["period"]     = 1
        # Pour “BYWEEKNO” :
        # repeat_root["extension"] = [{
        #     "url": "http://hl7.org/fhir/StructureDefinition/Timing-rrule",
        #     "valueString": f"FREQ=YEARLY;BYWEEKNO={semaine}"
        # }]

    # 3.5) Frq_filtreVal_5 → “numéro du mois”
    for el5 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_5"
    ):
        raw5 = (el5.text or "").strip()
        if not raw5.isdigit():
            continue
        mois = int(raw5)

        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "a"
        repeat_root["frequency"]  = 1
        repeat_root["period"]     = 1
        # Pour “BYMONTH” :
        # repeat_root["extension"] = [{
        #     "url": "http://hl7.org/fhir/StructureDefinition/Timing-rrule",
        #     "valueString": f"FREQ=YEARLY;BYMONTH={mois}"
        # }]

    # 3.6) Frq_filtreVal_6 → “rang de l’occurrence”
    for el6 in root.findall(
        ".//Elément_posologie/Fréquence_structurée/Frq_filtre/Frq_filtreVal_6"
    ):
        raw6 = (el6.text or "").strip()
        if not raw6.isdigit():
            continue
        rang = int(raw6)

        repeat_root.clear()
        repeat_root["periodUnit"] = existing_period_unit or "d"
        repeat_root["frequency"]  = rang
        repeat_root["period"]     = 1
        # Pour “2ᵉ mardi du mois” ou autre combinaison, ajouter ici
        # l’extension RRule appropriée.


def offset_from_nombre_unite(nombre: str, unite: str) -> Optional[int]:
    try:
        val = int(nombre.strip())
    except ValueError:
        return None
    u = unite.strip().lower()
    facteur = {
        "min": 1,
        "minute": 1,
        "minutes": 1,
        "h": 60,
        "heure": 60,
        "heures": 60,
        "j": 1440,
        "jour": 1440,
        "jours": 1440,
    }
    return val * facteur.get(u, 1)



#Fonction qui permet de générer le FHIR à partir du PN13 (fait appel aux mappings et aux fonctions précédentes)
def convert_pn13_to_fhir_file(xml_input: str,
                              json_output: str,
                              simple_map=SIMPLE_MAPPING,
                              composite_map=COMPOSITE_MAPPING,
                              static_map=STATIC_MAPPING,
                              transforms=TRANSFORMS) -> str:
    """
    Convertit un fichier PN13 XML en JSON FHIR MedicationRequest.
    Applique mappings simples, composites, statiques, conditions et transformations.
    Retourne le chemin du JSON généré.
    """
    # lecture XML
    tree = ET.parse(xml_input)
    root = tree.getroot()

    # initialisation de la ressource FHIR
    fhir = {"resourceType": "MedicationRequest",
    "contained": []}

    
    #Appel de la fonction pour créer la ressource medication et les champs qu'elle contient
    map_repeated_composants(
        root,
        fhir,
        base_xpath=".//Prescription/Elément_prescr_médic/Composant_prescrit",
        component_mappings=COMPONENT_MAPPINGS,
        component_transforms=COMPONENT_TRANSFORMS
    )
    
    #ajoute l'extension au champ valueBoolean (fourniture en PN13) dans Medication
    for med in fhir.get("contained", []):
        add_field_extension(
            med,
            ("valueBoolean",),       # clé du champ que l’on cible DANS la ressource Medication
            MY_EXTENSION
        )


    #Appel de la fonction pour créer la ressource practitioner et les champs qu'elle contient
    map_repeated_practitioners(
        root=root,
        fhir=fhir,
        base_xpath=".//Prescription/Elément_prescr_médic/Identification_prescripteur",
        practitioner_mappings={
            "Identifiant": ("identifier", "value"),
            "Nom_usage": ("name", "family"),
            "Prénom_usage": ("name", "given"),
        }
    )
    
    #Addaptation au format FHIR des champs de la balise Durée
    # 1) Extraire les deux champs PN13
    num_xpath = ".//Elément_posologie/Durée/Nombre"
    unit_xpath= ".//Elément_posologie/Durée/Unité"

    num_str  = root.findtext(num_xpath,  default="").strip()
    unit_str = root.findtext(unit_xpath, default="").strip()

    # 2) Si présents, parser et injecter
    if num_str and unit_str:
        d = parse_duration(num_str, unit_str)
        set_deep(fhir, ("dosageInstruction", "timing","repeat","duration"),     d["duration"])
        set_deep(fhir, ("dosageInstruction", "timing","repeat","durationUnit"), d["durationUnit"])
        
    
    #Appel de la fonction pour donner une valeur au champ ('MedicationRequest.groupIdentifier.value') si .//Messages[@Phast-id_message] est vide
    set_group_identifier_from_filename(fhir, xml_input)

    # 1) mappings simples avec les transformations
    for xpath, paths in simple_map.items():
        # Normalisation en liste
        if isinstance(paths, tuple):
            paths = [paths]

        # Pour chaque élément trouvé par ce xpath
        for el in root.findall(xpath):
            raw = (el.text or "").strip()
            if not raw:
                continue
            
            # ----- Cas spécial : Elément_posologie/Fréquence -----
            if xpath == ".//Elément_posologie/Fréquence":
                # Injecte directement dans `fhir["dosageInstruction"]["timing"]["repeat"]`
                inject_timing_from_pn13(fhir, raw)
                # On skip le set_deep pour ce champ précis
                continue
            
            # 2) Mise à jour de la table des voies d'administration
            if xpath == ".//Elément_prescr_médic/Voie_administration/VOIE":
                code  = raw
                label = el.attrib.get("Phast-libellé", "")
                update_voie_table(code, label)

            # 3) Application de la transformation si besoin
            fn = transforms.get(xpath)
            val = fn(raw) if fn else raw
            
            #Appel de la fonction pour traiter : Frq_filtreVal_1_N	Frq_filtreVal_2 Frq_filtreVal_3 Frq_filtreVal_4 Frq_filtreVal_5 Frq_filtreVal_6
            map_structured_frequency(root, fhir)

            # 4) Ne pas créer le champ si la transform renvoie None
            if val is None:
                continue

            # 5) Injection dans le JSON
            for p in paths:
                set_deep(fhir, p, val)


    # 2) mappings composites
    for xpaths, path in composite_map.items():
        if isinstance(xpaths, tuple) and len(xpaths) == 2 and "Int_temps_év_début" in xpaths[0]:
            # Traitement spécifique pour offset
            nombre = root.findtext(xpaths[0], default="").strip()
            unite = root.findtext(xpaths[1], default="").strip()
            offset = offset_from_nombre_unite(nombre, unite)
            if offset is not None:
                set_deep(fhir, path, offset)
        else:
            parts = []
            for xp in xpaths:
                txt = root.findtext(xp, default="").strip()
                if txt:
                    parts.append(txt)
            if parts:
                set_deep(fhir, path, " ".join(parts))

    # 3) mappings statiques
    for path, static_val in STATIC_MAPPING.items():
        set_deep(fhir, path, static_val)
    
    # 4) mappings conditionnels
    for cond in CONDITIONAL_MAPPING:
        raw = root.findtext(cond['pn13_xpath'], default="").strip()
        if raw:
            conditional_set(
                fhir,
                condition_path = cond['condition_path'],
                target_path    = cond['target_path'],
                value          = raw
            )
    #appel de la fonction add_system_if_code pour ajouter un system au code de la voie d'administration
    code_path = ('dosageInstruction','route','coding','code')
    add_system_if_code(fhir, code_path, 'http://standardterms.edqm.eu')

    #appel de la fonction add_system_if_code pour ajouter un system à l'unité de la quantité prescrite
    code_path = ('dosageInstruction', 'doseAndRate', 'doseQuantity', 'code')
    add_system_if_code(fhir, code_path, 'http://data.esante.gouv.fr/coe/standardterms')

    #appel de la fonction add_system_if_code pour ajouter un system à l'unité du débit
    code_path =('dosageInstruction', 'doseAndRate', 'rateQuantity', 'code')
    add_system_if_code(fhir, code_path, 'http://unitsofmeasure.org')
    
    # 5) ajoute une valeur à status dans le FHIR si GONOGO n'est pas présent dans le PN13
    if "status" not in fhir:
        fhir["status"] = "active"
    #ajoute une valeur à priority dans le FHIR si Urgent n'est pas présent dans le PN13
    if "priority" not in fhir:
        fhir["priority"] = "routine"
    #ajoute une valeure par défaut à period si il n'est pas déjà présent dans le FHIR
    repeat = fhir.setdefault("dosageInstruction", {}) \
             .setdefault("timing", {}) \
             .setdefault("repeat", {})
    if "period" not in repeat:
        repeat["period"] = 1
    #ajoute une valeure par défaut à frequency si il n'est pas déjà présent dans le FHIR
    repeat = fhir.setdefault("dosageInstruction", {}) \
             .setdefault("timing", {}) \
             .setdefault("repeat", {})
    if "frequency" not in repeat:
        repeat["frequency"] = 1
    

    #ajoute une valeur à timing dans le FHIR si Fréquence et Fréquence_structurée	ne sont pas présent dans le PN13
    repeat = fhir.get("dosageInstruction", {}) \
             .get("timing", {})
    # Si ni frequency, ni periodUnit, ni period n’existent :
    if all(key not in repeat for key in ("frequency", "periodUnit", "period")):
        # On (re)crée proprement le chemin jusqu’à repeat
        repeat = fhir.setdefault("dosageInstruction", {}) \
                    .setdefault("timing", {}) \
                    .setdefault("repeat", {})
        # On ajoute vos valeurs
        repeat["period"]     = "1"
        repeat["periodUnit"] = "d"


    # 6) Compléments pour certains champs
    #Appel de la fonction pour ajouter device 
    add_device_if_dispositif(fhir, root)
    
    #Appel de la fonction pour ajouter Patient 
    add_type_if_patient(fhir, root)

    #Appel de la fonction pour ajouter usual 
    add_use_if_patient(fhir, root)
    
    
    # 8) Ajout des extensions pour les champs choisi
    add_field_extension(
        fhir,
        ('supportingInformation', 0),
        {
          "valueCode": "UFHEB",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-uf-role"
        }
      )
    add_field_extension(
        fhir,
        ('supportingInformation', 1),
        {
          "valueCode": "UFMED",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-uf-role"
        }
      )
    add_field_extension(
        fhir,
        ("note", 0),
        {
          "valueCode": "PRESCCOM",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 3),
        {
          "valueCode": "PRESCCOM",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 4),
        {
          "valueCode": "LIPRESCRENSCOMP",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 5),
        {
          "valueCode": "LIPRESCLIBMED",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 6),
        {
          "valueCode": "LIPRESCPOS",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 7),
        {
          "valueCode": "LIPRESCIND",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 8),
        {
          "valueCode": "LIPRESCCOMM",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 9),
        {
          "valueCode": "LIPRESCCOMM",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    add_field_extension(
        fhir,
        ("note", 10),
        {
          "valueCode": "LIPRESCCONDAPPL",
          "url": "https://hl7.fr/fhir/fr/medication/StructureDefinition/fr-medicationrequest-note-scope"
        }
      )
    
    # 9) écriture JSON
    parent = os.path.dirname(json_output)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(fhir, f, ensure_ascii=False, indent=2)

    print(f"✔ La prescription médicamenteuse au format FHIR générée : {json_output}")


#Exécution de la fonction de convertion au standard FHIR

xml_in   = "2025051911285175_0000314_64166416_19924082.xml"#nom du fichier PN13 
json_out = "prescription_fhir.json"#nom que l'on souhaite donner au fichier FHIR

#Appel de la fonction de convertion
convert_pn13_to_fhir_file(xml_in, json_out)
