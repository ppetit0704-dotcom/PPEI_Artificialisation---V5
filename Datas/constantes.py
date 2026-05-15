#Définition des constantes pour maintenances future
#Basé sur le fichier artificialisation du CEREM
#==========================================================================================
#           Liste des champs
# "idcom";"idcomtxt";"idreg";"idregtxt";"iddep";"iddeptxt";"epci24";"epci24txt";"scot";"aav2020";"aav2020txt";"aav2020_typo";
# "naf09art10";"art09act10";"art09hab10";"art09mix10";"art09rou10";"art09fer10";"art09inc10";"naf10art11";"art10act11";"art10hab11";"art10mix11";"art10rou11";"art10fer11";"art10inc11";"naf11art12";"art11act12";"art11hab12";"art11mix12";"art11rou12";"art11fer12";"art11inc12";"naf12art13";"art12act13";"art12hab13";"art12mix13";"art12rou13";"art12fer13";"art12inc13";"naf13art14";"art13act14";"art13hab14";"art13mix14";"art13rou14";"art13fer14";"art13inc14";"naf14art15";"art14act15";"art14hab15";"art14mix15";"art14rou15";"art14fer15";"art14inc15";"naf15art16";"art15act16";"art15hab16";"art15mix16";"art15rou16";"art15fer16";"art15inc16";"naf16art17";"art16act17";"art16hab17";"art16mix17";"art16rou17";"art16fer17";"art16inc17";"naf17art18";"art17act18";"art17hab18";"art17mix18";"art17rou18";"art17fer18";"art17inc18";"naf18art19";"art18act19";"art18hab19";"art18mix19";"art18rou19";"art18fer19";"art18inc19";"naf19art20";"art19act20";"art19hab20";"art19mix20";"art19rou20";"art19fer20";"art19inc20";"naf20art21";"art20act21";"art20hab21";"art20mix21";"art20rou21";"art20fer21";"art20inc21";"naf21art22";"art21act22";"art21hab22";"art21mix22";"art21rou22";"art21fer22";"art21inc22";"naf22art23";"art22act23";"art22hab23";"art22mix23";"art22rou23";"art22fer23";"art22inc23";"naf23art24";"art23act24";"art23hab24";"art23mix24";"art23rou24";"art23fer24";"art23inc24";"naf09art24";"art09act24";"art09hab24";"art09mix24";"art09inc24";"art09rou24";"art09fer24";"artcom0924";
# "pop15";"pop21";"pop1521";"men15";"men21";"men1521";"emp15";"emp21";"emp1521";"mepart1521";"menhab1521";"artpop1521";"surfcom2024"
#
#==========================================================================================


##############################################################################
#       CONSTANTES A CHANGER POUR LES MILLESIMES FUTUR
#Millésimmes
millesime_debut="09"
millesime_reference_debut="11"
millesime_reference_fin="20"
millesime="24"                                          #   Années de données traitées dans le fichier (CEREMA)
millesime_min="15"                                      #   Année de la dernière référence anneulle (INSEE)
millesime_max="21"                                      #   Année de la nouvelle référence annuelle traitée (INSEE)
millesime_aav="2020"                                    #   Année de référence des aires d'attraction des villes (INSEE)
millesime_periode=f"{millesime_min}{millesime_max}"     #   Plage périodique
start_periode_art="09"                                  #   Première année de comptabilisation de la consommation d'espace
end_periode_art=f"{millesime}"                          #   Dernière année de comptabilisation de la consommation d'espace


###################################################################################
#       CONSTANTES A SURTOUT NE PAS CHANGECHANGER POUR LES MILLESIMES FUTUR
#
#   Assure la bonne lectures des champs du ficichier CSV fournis par le CEREMA
#
###################################################################################

# Identité communale
M_COM_INSEE="idcom"
M_COM_NOM="idcomtxt"
#Identité Régionale
M_REG_INSEE="idreg"
M_REG_NOM="idregtxt"
#Identité Départementale
M_DEP_NUM="iddep"
M_DEP_NOM="iddeptxt"
#Identité EPCI
M_EPCI_SIRET=f"epci{millesime}"                         # Intitulé de champ : Numéro Siret EPCI
M_EPCI_NOM=f"epci{millesime}txt"                        # Intitulé de champ : Nom de l'EPCI
#Identité SCoT
M_SCOT_NOM="scot"


M_SURF_COM=f"surfcom20{millesime}"                        # Intitulé de champ : Surface communale en m²

M_AAV_CODE=f"aav{millesime_aav}"                        # Intitulé de champ : Code de l'aire d'attraction des villes
M_AAV_NOM=f"aav{millesime_aav}txt"                      # Intitulé de champ : Nom de l'aire d'attraction des villes

#Population
M_POP_MIN = f"pop{millesime_min}"                       # Intitulé de champ : dernière référence population traitée (INSEE)
M_POP_MAX = f"pop{millesime_max}"                       # Intitulé de champ : 
M_POP_PERIODE=f"pop{millesime_periode}"                 # Intitulé de champ : 

#Ménage
M_MEN_MIN = f"men{millesime_min}"                       # Intitulé de champ : 
M_MEN_MAX = f"men{millesime_max}"                       # Intitulé de champ : 
M_MEN_PERIODE = f"men{millesime_periode}"               # Intitulé de champ : 

#Emplois
M_EMP_MIN = f"emp{millesime_min}"                       # Intitulé de champ : 
M_EMP_MAX = f"emp{millesime_max}"                       # Intitulé de champ : 
M_EMP_PERIODE=f"emp{millesime_periode}"                 # Intitulé de champ : 


#Création automatique des constantes catégorielles
start = int(start_periode_art)
end = int(end_periode_art)


#Catégories
ACTIVITE = {}
HABITAT = {}
MIXTE = {}
INCONNU = {}
FERROVIAIRE = {}
ROUTE = {}

for count in range(start, end):
    c = f"{count:02d}"
    n = f"{count + 1:02d}"

    ACTIVITE[c] = f"art{c}act{n}"
    HABITAT[c] = f"art{c}hab{n}"
    MIXTE[c] = f"art{c}mix{n}"
    INCONNU[c] = f"art{c}inc{n}"
    FERROVIAIRE[c] = f"art{c}fer{n}"
    ROUTE[c] = f"art{c}rou{n}"

M_ART_TOTALE =f"artcom{millesime_debut}{millesime}"
M_ART_REFERENCE =f"artcom{millesime_reference_debut}{millesime_reference_fin}"


