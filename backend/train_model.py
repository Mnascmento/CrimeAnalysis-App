import pandas as pd
from pymongo import MongoClient
from xgboost import XGBClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle

# Configuração do MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['odontolegal']
colecao = db['dados']

dados = list(colecao.find({}, {'_id': 0}))

lista = []
for d in dados:
    lista.append({
        "idade": d['Vitima']['idade'],
        "etnia": d['Vitima']['etnia'],
        "localizacao": d['localizacao'],
        "tipo_de_caso": d['tipo_de_caso'],
    })

df = pd.DataFrame(lista)

x = df[['idade', 'etnia', 'localizacao']]
y = df['tipo_de_caso']

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

categorical_features = ['etnia', 'localizacao']
numerical_features = ['idade']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('num', 'passthrough', numerical_features)
    ],
)

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'))
])

# Treinar o modelo
pipeline.fit(x, y_encoded)
# Salvar o modelo treinado
with open('model.pkl', 'wb') as model_file:
    pickle.dump({
        'model': pipeline,
        'label_encoder': label_encoder
    }, model_file)

print("Modelo treinado e salvo em model.pkl!")

