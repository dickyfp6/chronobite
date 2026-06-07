import pandas as pd
import re
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate to parent directory (TugasAkhirDSS root)
root_dir = os.path.dirname(script_dir)
# Build paths relative to root
data_input_path = os.path.join(root_dir, "A. Data", "Data Processed", "02_pivot_food_nutrients.csv")
missing_output_path = os.path.join(root_dir, "A. Data", "Data Processed", "03_missing_analysis.csv")
halal_output_path = os.path.join(root_dir, "A. Data", "Data Processed", "03_dataset_halal.csv")

data = pd.read_csv(data_input_path)

print("Dataset awal:", data.shape)

# =====================
# LIST HARAM
# =====================

haram_keywords = [
    "ABITA", "ABSINTHE", "ADVOCAT", "AJENJO", "ALASKA", "ALCHOHOL", "ALCHOLIC", 
    "ALCOHAL", "ALCOHIC", "ALCOHOL", "ALCOHOLIC", "ALE", "AMARETTO", "AMBERYE", 
    "AMERETTO", "AMOORETTO", "ANDOUILIE", "ANDOUILLE", "ANDOVILLE", "ANISETTE", 
    "APERITIF", "APERITIVO", "APPLETINI", "ARABIKI", "ARMAGNAC", "ARMOUR", 
    "BABYBACK", "BACARDI", "BACCHUS", "BACKFAT", "BACN", "BACOM", "BACON", 
    "BACONADDICT", "BACONATOR", "BACONI", "BACONNAISE", "BAILEYS", "BANYULS", "BARBERA", 
    "BAREFOOT", "BAROLO", "BAUERNWURST", "BAVERIAN", "BEAR", "BEER", "BEERGARDEN", "BEERS", 
    "BEERTINI", "BEERWURST", "BEERY", "BELLINI", "BELLOTA", "BENEDICTINE", "BERETTA", 
    "BERLINKI", "BIER", "BIERGARTEN", "BIGOS", "BILTONG", "BITTERS", "BLOOD", 
    "BLOODYMARY", "BLUTWURST", "BOAR", "BOARS", "BOCK", "BOILERMAKER", "BOLLICINE", 
    "BOLOGNA", "BOORBON", "BOOZE", "BOOZY", "BORDEAUX", "BORRACHO", "BOUDAIN", "BOUDIN", 
    "BOURBAN", "BOURBON", "BOURBONRIDGE", "BRANDIED", "BRANDY", "BRAT", "BRATWURST", 
    "BRATWURSTS", "BRAUNSCHWEIGER", "BRAWTWURST", "BRBN", "BREADEDPORKPATTY", 
    "BREATWURST", "BREW", "BREWERY", "BREWS", "BROCKWURST", "BROURBON", "BRUT", 
    "BUDDIG", "BUDWEISER", "BURGUNDY", "BUZZED", "CABANOSSI", "CABERNET", "CACCIATORE", 
    "CALABRESA", "CANTIMPALO", "CAPACOLLA", "CAPICOLA", "CAPOCOLLA", "CAPOCOLLO", 
    "CARIGNANE", "CARNITA", "CARNITAS", "CAVA", "CELLARS", "CERDO", 
    "CERVELAT", "CERVEZA", "CHABLIS", "CHAMBORD", "CHAMPAGINE", "CHAMPAGNE", 
    "CHARCUTERIE", "CHARDONNAY", "CHASHU", "CHATEAU", "CHEDDARWURST", "CHELADA", 
    "CHENIN", "CHIANT", "CHIANTI", "CHICARON", "CHICARRONES", "CHICHARRON", 
    "CHICHARRONES", "CHIPOLATAS", "CHISTORRA", "CHITTERLINGS", "CHOPS", "CHORIZO", 
    "CHORIZOS", "CHOURICO", "CITTERIO", 
    "CLARET", "COCHON", "COCHONS", "COCKTAIL", "COCKTAILFROM", "COCKTAILS", "COCOKTAIL", 
    "COCTAIL", "COGNAC", "COKTAIL", "CORONA", "COSMOPOLITAN", "CRACKILINGS", "CRACKLING", 
    "CRACKLINGS", "CRISTAL", "CUBAN", "CUBEDHAM", "CUERITOS", "CURACAO", "CURED", 
    "CURRYWURST", "CUVEE", "DAIGUIRI", "DAIQUIRI", "DELICATESSEN", 
    "DEUTSCHMACHER", "DIGESTIF", "DISTILLATE", "DISTILLED", "DISTILLERY", 
    "DOLCETTO", "DOPPELBOCK", "DRAFT", "DRUNKEN", "DUBBEL", "DUNKELWURST", 
    "DUROC", "ECHOFALLS", "EMBASA", "ESSKAY", "ETHANOL", "ETOUFFEE", "EVERROAST", 
    "FALERNUM", "FATBACK", "FELINO", "FINOCCHIONA", "FIREBALL", "FIREROASTEDPORK", 
    "FIREWALKER", "FLASK", "FOIE", "FRANGELICO", "FRANKFURT", "FRANKFURTER", 
    "FRANKFURTEIS", "FRANKFURTERS", "FRANKFURTS", "FRANKFUTERS", "FRANKS", 
    "FRANKTACULAR", "FRNKS", "FROG", "FROGS", "FROSE", "FULLYCOOKEDBACON", "FUME", 
    "FUNDIDO", "GAMMON", "GELATIN", "GENOA", "GETTA", "GEWURZTRAMINER", "GIFFORDS", 
    "GIMLET", "GIN", "GLENFARCLAS", "GLENGOYNE", "GLOGG", "GLUG", "GOSLINGS", 
    "GOSMOPOLITAN", "GRASOVKA", "GRENACHE", "GRIGIO", "GROG", "GUANCIALE", 
    "GUINABEER", "GUINNESS", "HAM", "HAMONADO", "HAMPEAS", "HAMS", "HARP", "HATFIELD", 
    "HAWG", "HEADCHEESE", "HEMPLER", "HIBALL", "HOG", "HOGS", "HOPDEVIL", "HOPPY", 
    "HOPS", "IBERCO", "IBRICO", "IPA", "JAGERBOMB", "JAMBON", "JAMON", "JAMONILLA", 
    "JERKIE", "JERKY", "JERRKY", "JOWL", "JOWLS", "JULEP", "KABANOS", "KAHLA", 
    "KAHLUA", "KALBI", "KAMIKAZE", "KANPAI", "KASSLER", "KEG", "KEILBASA", "KIELASA", 
    "KIELBASA", "KIELBASI", "KIRSCH", "KISHKA", "KNACKWURST", "KOEGEL", "KOZLOWSKI", 
    "KRAKOVSKY", "KRAKOWSKA", "KRAKUS", "KUNZLER", "KUROBUTA", "KVASS", "LAGER", 
    "LAMBIC", "LAMBRUSCO", "LANDJAEGER", "LANDJAGER", "LANDRACE", "LANDSHARK", 
    "LARD", "LARDO", "LARDONS", "LAUGANEGA", "LBERICO", "LEMBERGER", "LEMONCELLO", 
    "LIMONCINO", "LINGUIA", "LINGUICA", "LINGUISA", "LIQUER", "LIQUERE", 
    "LIQUEUR", "LIQUEURS", "LIQUOR", "LONGANISA", 
    "LONGANIZA", "LUCANO", "LUGANIGA", "LUNCHEON", "MALT", "MALTS", "MANAPUA", 
    "MANHATTAN", "MANISCHEWITZ", "MARASCHINO", "MARGARITA", "MARSALA", 
    "MARSHMALLOW", "MARZEN", "MEAD", "MENAGE", "MERLOT", "METTWURST", 
    "MEZCAL", "MICHELADA", "MICHELADAS", "MICROBREW", "MIMOSA", "MIRIN", "MIXOLOGIST", 
    "MOJITO", "MONTEGRAPPA", "MOONSHINE", "MORCILLA", "MORITZ", "MORTADELLA", 
    "MOSCATEL", "MOSCATO", "MUDSLIDE", "MUFFALETTA", "MULLED", "MUNCHEN", "MUSCAT", 
    "NDUJA", "NECKBONES", "NOCINO", "OAKED", "OAKY", "OCTOBERFEST", "OINK", 
    "OKLOBERFEST", "OKTOBERFAST", "OKTOBERFEST", "ORGEAT", "ORZATA", "OUZO", 
    "PAINKILLER", "PANCETTA", "PASTETA", "PASTOR", "PASTRAMI", "PATA", "PATE", 
    "PATRON", "PATTY", "PEPPEROLI", "PEPPERONI", "PEPPERONI (PEPP)", "PEPPERRONI", 
    "PERON", "PERPPEONI", "PIG", "PIGCHASER", "PIGGIES", "PIGGY", "PIGLETS", "PIGS", 
    "PILS", "PILSNER", "PINOT", "PISCO", "POMMERY", "PONCHE", "PORC", "PORCHETTA", 
    "PORK", "PORKAND", "PORKETTA", "PORKIES", "PORKRIBPATTY", "PORKRIBPATW", 
    "PORKSKIN", "PORKSKINS", "PORKY", "PORN", "PORQ", "PORTER", "PORTO", "PPRONI", 
    "PROSC", "PROSCIUT", "PROSCIUTTO", "PROSCUITTO", "PROSECCO", "PROST", "PUB", 
    "PUERCO", "PUNSCH", "QUAFFY", "REFOSCO", "RELARD", "REPOSADO", "RHONE", 
    "RIBNOXIOUS", "RIESLING", "RIOJA", "ROSSI", "RUM", "SAHSAGE", "SAISAGE", "SAKE", "SALAME", "SALAMETTI", 
    "SALCHICHON", "SALCHION", "SALUMERIA", "SAMBUCA", "SANGARIA", "SANGIOVESE", 
    "SARONNO", "SAUAGE", "SAUCISSE", "SAUCISSON", "SAUTERNE", 
    "SAUVIGNON", "SAUVISNON", "SCHINKENBROT", "SCHMIRACLE", "SCHWARZWALDER", "SCOTCH", 
    "SCRAPPLE", "SCREAMARITA", "SCREWDRIVER", "SEABREEZE", "SEAGRAM", "SEAGRAMS", 
    "SELTZ", "SEMILLON", "SENGRIA", "SHANDY", "SHAOHSING", "SHERRY", "SHIRAZ", 
    "SHUMAI", "SIDRA", "SIRAH", "SKAL", "SKOL", "SLOE", 
    "SMOKIE", "SNAPPS", "SNOUTS", "SOLERA", "SOPERSSATA", "SOPPRESATA", "SOPPRESSATA", 
    "SOPRESSA", "SORTASAUSAGE", "SOUSE", "SPAM", "SPARERIB", "SPARERIBS", "SPDA", 
    "SPEAKEASY", "SPECK", "SPIRIT", "SPIRITS", "SPORESSATA", "SPRITZER", "SPRITZERS", 
    "SPUMANTE", "STEIN", "STOLI", "STOUT", "STRANAHAN", "STREAKY", "STROH", 
    "SUASAGE", "SUNTORY", "SWINE", "SWISSWURST", "SYRAH", "TALLOW", "TASSO", 
    "TEAWURST", "TEDESCHI", "TEPACHE", "TEQUILA", "TERRINE", "THURGAU", 
    "THURINGER", "TIPSY", "TOCINO", "TONGUE", "TREBBIANO", "TRIPEL", "TROPIQUILA", 
    "UNCORKED", "UNDERBERG", "USINGER", "VARIETAL", "VENTRICINA", "VERDICCHIO", 
    "VERITAS", "VERMOUTH", "VIENNAS", "VIGNERI", "VIN", "VINO", "VODKA", 
    "WEENIE", "WEINHARD", "WEISSWURST", "WHISKEY", "WHISKY", "WIENER", "WIENERS", 
    "WINE", "WINING", "WOODFORD", "WORMWOOD", "WURST", "XIMENEZ", "YACHTWURST", 
    "YODKA", "YUENGLING", "YUENGLINGS", "ZINFANDEL"
]

pattern = "(?:" + "|".join(re.escape(kw) for kw in haram_keywords) + ")"

data_no_haram = data[
~data["food_name"].str.upper().str.contains(pattern, na=False, regex=True)
]

print("Dataset setelah filter haram:", data_no_haram.shape)

# =====================
# HAPUS KATEGORI TERTENTU
# =====================

categories_to_remove = ["Alcoholic Beverages", "Baby Foods", "Pork Products", "Spices and Herbs", "American Indian/Alaska Native Foods"]

data_cleaned = data_no_haram[
~data_no_haram["food_group"].isin(categories_to_remove)
]

print("Dataset setelah hapus kategori:", data_cleaned.shape)

# Filter liver sausage dan pate berbasis babi dari Sausages and Luncheon Meats
pork_liver_keywords = ['braunschweiger', 'liver sausage', 'liverwurst', 'liver cheese', 'pate, liver']
pork_liver_mask = (
    (data_cleaned['food_group'] == 'Sausages and Luncheon Meats') &
    (data_cleaned['food_name'].str.lower().str.contains('|'.join(pork_liver_keywords), na=False))
)
before_liver = len(data_cleaned)
data_cleaned = data_cleaned[~pork_liver_mask]
print(f"Filter pork liver sausage/pate: {before_liver - len(data_cleaned)} items removed")
print("Dataset setelah filter liver products:", data_cleaned.shape)

# =====================
# FILTER NUTRISI UTAMA (ADVANCED)
# =====================

before_filter = len(data_cleaned)

data_cleaned = data_cleaned[
    (data_cleaned["protein_g"] > 0) &
    (data_cleaned["carbohydrate_g"] > 0) &
    (data_cleaned["fat_g"] > 0)
]

after_filter = len(data_cleaned)

print("\n" + "="*50)
print("FILTER NUTRISI (protein>0, carbo>0, fat>0)")
print("="*50)
print(f"Data sebelum: {before_filter}")
print(f"Data setelah: {after_filter}")
print(f"Data terhapus: {before_filter - after_filter}")
print("="*50)

# =====================
# ANALISIS MISSING
# =====================

missing = data_cleaned.isnull().sum()

missing.to_csv(missing_output_path)

data_cleaned.to_csv(halal_output_path, index=False)

print("Dataset tanpa makanan haram disimpan.")
print("File missing analysis juga disimpan.")