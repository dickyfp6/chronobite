import pandas as pd

data = pd.read_csv("Data Processed/pivot_food_nutrients.csv")

print("Dataset awal:", data.shape)

# =====================
# LIST HARAM
# =====================

haram_keywords = [
"ABITA","ABSINTHE","ADOBO","ADVOCAT","AIDELLS","AJENJO","ALCHOLIC","ALCOHIC",
"ALCOHOL","ALCOHOLIC","ALE","AMARETTO","AMERICANO","ANDOUILLE","ANIMAL",
"ANISETTE","APERITIF","BACARDI","BACON","BAILEYS","BAROLO","BEER","BEERS",
"BEERTINI","BEERWURST","BIER","BISON","BITTERS","BLOOD","BOAR","BOCK",
"BOOZE","BOURBON","BRANDY","BRATWURST","BREW","BREWERY","BUDWEISER",
"CABERNET","CHAMPAGNE","CHARDONNAY","CHORIZO","CIDER","COGNAC",
"COSMOPOLITAN","CURRYWURST","DAIQUIRI","DISTILLED","DISTILLERY",
"DOPPELBOCK","DRUNKEN","GIN","GUINNESS","HAM","HOG","JAMON",
"JERKY","KAHLUA","KIELBASA","LAGER","LAMBIC","LARD","LIQUEUR",
"LIQUOR","MEAD","MERLOT","MEZCAL","MOJITO","MOONSHINE","MORTADELLA",
"MOSCATO","NDUJA","OKTOBERFEST","OUZO","PASTRAMI","PEPPERONI",
"PIG","PORK","PORCHETTA","PROSCIUTTO","PROSECCO","RUM","SAKE",
"SALAMI","SCHINKEN","SCOTCH","SHERRY","SHIRAZ","SPAM","SPARERIB",
"STOUT","SWINE","TEQUILA","VERMOUTH","VINO","VODKA","WHISKEY",
"WHISKY","WINE","WURST"
]

pattern = "|".join(haram_keywords)

data_no_haram = data[
~data["food_name"].str.upper().str.contains(pattern, na=False)
]

print("Dataset setelah filter haram:", data_no_haram.shape)

# =====================
# ANALISIS MISSING
# =====================

missing = data_no_haram.isnull().sum()

missing.to_csv(
"Data Processed/missing_analysis.csv"
)

data_no_haram.to_csv(
"Data Processed/dataset_no_haram.csv",
index=False
)

print("Dataset tanpa makanan haram disimpan.")
print("File missing analysis juga disimpan.")