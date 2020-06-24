drop table if exists collaborateurs;
drop table if exists charges_parlementaires;
drop table if exists mandats;
drop table if exists acteurs;
drop table if exists organes;

create table if not exists acteurs
(
	id_an text primary key,
	source_an text,
	prenom text,
	nom text,
	civilite text,
	date_naissance date,
	ville_naissance text,
	departement_naissance text,
	date_deces date,
	label_profession text,
	categorie_insee text,
	famille_insee text
);

create table if not exists organes
(
    id_an text primary key,
    source_an text,
    label text,
    label_court text,
    type_organe text
);

create table if not exists mandats
(
    id integer primary key autoincrement,
    list_id_an_organe text,
    id_an_acteur text,
    date_debut date,
    date_fin date,
    label text,
    foreign key (id_an_acteur) references acteurs(id_an)
);

create table if not exists charges_parlementaires
(
    id integer primary key autoincrement,
    id_an_acteur text,
    source_an text,
    chambre text,
    region text,
    departement text,
    num_circonscription text,
    date_debut date,
    date_fin date,
    id_an_suppleant text,
    nb_collaborateurs integer,
    foreign key (id_an_acteur) references acteurs(id_an)
);

create table if not exists collaborateurs
(
    id integer primary key autoincrement,
    id_charge_parlementaire integer,
    prenom text,
    nom text,
    civilite text,
    date_debut date,
    date_fin date,
    foreign key (id_charge_parlementaire) references charges_parlementaires(id)
);

