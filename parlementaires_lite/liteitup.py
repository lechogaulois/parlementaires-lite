from orator import DatabaseManager
from pathlib import Path
import json


PROJECT_ROOT_PATH = Path(__file__).parent.parent
DATA_DIRECTORY = PROJECT_ROOT_PATH.joinpath('data')
DB_PATH = PROJECT_ROOT_PATH.joinpath('parlementaires.lite')
ACTEURS_JSON_PATH = DATA_DIRECTORY.joinpath('opendata_extract', 'acteurs')
ORGANES_JSON_PATH = DATA_DIRECTORY.joinpath('opendata_extract', 'organes')

def acteur_parsing(acteur_json):
    acteur_dict = {}
    acteur_dict["source_an"] = json.dumps(acteur_json)
    acteur_dict["id_an"] = j_to_s(acteur_json["acteur"]["uid"]["#text"])
    acteur_dict["prenom"] = j_to_s(acteur_json["acteur"]["etatCivil"]["ident"]["prenom"])
    acteur_dict["nom"] = j_to_s(acteur_json["acteur"]["etatCivil"]["ident"]["nom"])
    acteur_dict["civilite"] = j_to_s(acteur_json["acteur"]["etatCivil"]["ident"]["civ"])
    acteur_dict["date_naissance"] = j_to_s(acteur_json["acteur"]["etatCivil"]["infoNaissance"]["dateNais"])
    acteur_dict["ville_naissance"] = j_to_s(acteur_json["acteur"]["etatCivil"]["infoNaissance"]["villeNais"])
    acteur_dict["departement_naissance"] = j_to_s(acteur_json["acteur"]["etatCivil"]["infoNaissance"]["depNais"])
    acteur_dict["date_deces"] = j_to_s(acteur_json["acteur"]["etatCivil"]["dateDeces"])
    acteur_dict["label_profession"] = j_to_s(acteur_json["acteur"]["profession"]["libelleCourant"])
    acteur_dict["categorie_insee"] = j_to_s(acteur_json["acteur"]["profession"]["socProcINSEE"]["catSocPro"])
    acteur_dict["famille_insee"] = j_to_s(acteur_json["acteur"]["profession"]["socProcINSEE"]["famSocPro"])

    return acteur_dict


def organe_parsing(organe_json):
    organe_dict = {}
    organe_dict["source_an"] = json.dumps(organe_json)
    organe_dict["id_an"] = j_to_s(organe_json["organe"]["uid"])
    organe_dict["label"] = j_to_s(organe_json["organe"]["libelle"])
    organe_dict["label_court"] = j_to_s(organe_json["organe"]["libelleAbrege"])
    organe_dict["type_organe"] = j_to_s(organe_json["organe"]["codeType"])

    return organe_dict


def j_to_s(content):
    '''
        fonction utilitaire pour formater les valeurs nulles renvoyées par le moteur XML souverain
    '''
    str_content = str(content)
    if str_content == "{'@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', '@xsi:nil': 'true'}":
        return None
    return str_content

db_schema_sql = DATA_DIRECTORY.joinpath('schema.sql').read_text()

config = {
    'default': 'sqlite',
    'sqlite': {
        'driver': 'sqlite',
        'database': DB_PATH,
    }
}

db = DatabaseManager(config)

for statement in db_schema_sql.split(';'):
    db.statement(statement)


for organe in ORGANES_JSON_PATH.glob("*"):
    organe_obj = organe_parsing(json.loads(organe.read_text()))
    db.table('organes').insert(organe_obj)

for acteur in ACTEURS_JSON_PATH.glob("*"):
    acteur_json = json.loads(acteur.read_text())
    acteur_obj = acteur_parsing(acteur_json)

    db.table('acteurs').insert(acteur_obj)

    for mandat_json in acteur_json["acteur"]["mandats"]["mandat"]:
        db\
            .table('mandats').insert(
            list_id_an_organe=j_to_s(mandat_json["organes"]["organeRef"]),
            id_an_acteur=j_to_s(mandat_json["acteurRef"]),
            date_debut=j_to_s(mandat_json["dateDebut"]),
            date_fin=mandat_json["dateFin"],
            label=j_to_s(mandat_json["typeOrgane"])
        )

        qualite_mandat = mandat_json["typeOrgane"]

        if qualite_mandat == "SENAT" or qualite_mandat == "ASSEMBLEE":


            list_collaborateurs = []
            if mandat_json["collaborateurs"]:
                list_collaborateurs = mandat_json["collaborateurs"]["collaborateur"]
                if not isinstance(list_collaborateurs, list):
                    list_collaborateurs = [list_collaborateurs]

            id_suppleant = None
            if mandat_json["suppleants"]:
                id_suppleant = mandat_json["suppleants"]["suppleant"]["suppleantRef"]
            
            charge_id = db.table('charges_parlementaires').insert_get_id({
                "source_an":json.dumps(mandat_json),
                "id_an_acteur":acteur_obj["id_an"],
                "chambre":"Sénat" if qualite_mandat == "SENAT" else "Assemblée nationale",
                "region":mandat_json["election"]["lieu"]["region"],
                "departement":mandat_json["election"]["lieu"]["departement"],
                "num_circonscription":mandat_json["election"]["lieu"]["numCirco"],
                "date_debut":mandat_json["dateDebut"],
                "date_fin":mandat_json["dateFin"],
                "id_an_suppleant":id_suppleant,
                "nb_collaborateurs":len(list_collaborateurs),
            })

            for collaborateur in list_collaborateurs:
                print(collaborateur)
                print(charge_id)
                db.table('collaborateurs').insert(
                    id_charge_parlementaire=charge_id,
                    prenom=collaborateur["prenom"],
                    nom=collaborateur["nom"],
                    civilite=collaborateur["qualite"],
                    date_debut=collaborateur["dateDebut"],
                    date_fin=collaborateur["dateFin"]
                )








