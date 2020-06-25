update acteurs set source_an = null;
update charges_parlementaires set source_an = null;
update organes set source_an = null;

/* ne pas oublier d'utiliser la commande vacuum de sqlite */