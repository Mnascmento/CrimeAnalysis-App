from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo import ObjectId
from dataclasses import dataclass, asdict
import random
from datetime import datetime, timedelta
from flask import request, abort
import pickle
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union


class Status(Enum):
    EM_ANDAMENTO = 1
    CONCLUIDO = 2

app = Flask(__name__)
CORS(app)

# Configuração do MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['odontolegal']
colecao = db['dados']

@dataclass
class Vitima:
    nic: str
    nome: str = None
    genero: str = None
    idade: int = None
    documento: str = None
    endereco: str = None
    corEtnia: str = None
    odontograma: List[ObjectId] = None

@dataclass
class Caso:
    titulo: str
    descricao: str
    vitimas: List[str]
    status: Status = Status.EM_ANDAMENTO
    dataAbertura: datetime = datetime.now()
    dataFechamento: Optional[datetime] = None
    geolocalizacao: Optional[dict[str, Union[str, float]]] = None
    evidencias: List[str] = None
    relatorio: Optional[str] = None

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "vitimas": [asdict(vitima) if isinstance(vitima, Vitima) else vitima for vitima in self.vitimas],
            "status": self.status.name,
            "dataAbertura": self.dataAbertura.isoformat(),
            "dataFechamento": self.dataFechamento.isoformat() if self.dataFechamento else None,
            "geolocalizacao": self.geolocalizacao,
        }

def gerar_dados_aleatorio(n:100):
    tipos_de_caso = ["Homicídio", "Acidente de Trânsito", "Desaparecimento", "Lesão Corporal", "Violência Doméstica", "Assalto", "Tráfico"]
    locais = ["Rua da Moeda", "Rua Bom Jesus", "Praça da Liberdade", "Avenida Paulista", "Parque Ibirapuera", "Estação Central", "Hospital Municipal"]
    etnias = ["Branca", "Preta", "Parda", "Amarela", "Indígena"]
    casos = []
    base_date = datetime.now() 
    for i in range(n):
        data_caso = (base_date - timedelta(days=random.randint(0, 365))).date().isoformat()
        caso = Caso(
            data_do_caso=data_caso,
            tipo_de_caso=random.choice(tipos_de_caso),
            localizacao=random.choice(locais),
            Vitima=Vitima(
                etnia=random.choice(etnias),
                idade=random.randint(1, 90)
            )
        )
        casos.append(caso.to_dict())
    return casos

def validar_caso_json(data):
    try:
        vitima = data['Vitima']
        assert isinstance(vitima, dict)
        assert all (k in vitima for k in ['etnia', 'idade'])
        datetime.fromisoformat(data['data_do_caso'])
        assert isinstance(data['tipo_de_caso'], str)
        assert isinstance(data['localizacao'], str)
    except:
        return False
    return True

@app.route('/api/casos', methods=['GET'])
def listar_casos():
    documentos = list(colecao.find({}, {'_id': 0}))
    return jsonify(documentos), 200

@app.route('/api/casos', methods=['POST'])
def criar_caso():
    data = request.get_json()
    if not data or not validar_caso_json(data):
        abort(400, description="Dados inválidos ou faltando campos obrigatórios.")
    colecao.insert_one(data)
    return jsonify({"message": "Caso criado com sucesso!"}), 201

@app.route('/api/casos/<string:tipo_de_caso>', methods=['GET'])
def buscar_caso(data_do_caso):
    caso = colecao.find_one({"data_do_caso": data_do_caso}, {'_id': 0})
    if not caso:
        abort(404, description="Caso não encontrado.")
    return jsonify(caso), 200

@app.route('/api/casos/<string:tipo_de_caso>', methods=['DELETE'])
def deletar_caso(data_do_caso):
    resultado = colecao.delete_one({"data_do_caso": data_do_caso})
    if resultado.deleted_count == 0:
        abort(404, description="Caso não encontrado.")
    return jsonify({"message": "Caso deletado com sucesso!"}), 200

with open('model.pkl', 'rb') as model_file:
    data = pickle.load(model_file)
    model = data['pipeline']
    label_encoder = data['label_encoder']

@app.route('/api/associacoes', methods=['GET'])
def associacoes():
    documentos = list(colecao.find({}, {"_id": 0}))
    if not documentos:
        return jsonify({"message": "Sem dados na coleção"}), 400

    lista = []
    for d in documentos:
        vitima = d.get("vitima", {})
        lista.append({
            "idade": vitima.get("idade"),
            "etnia": vitima.get("etnia"),
            "localizacao": d.get("localizacao"),
            "tipo_do_caso": d.get("tipo_do_caso")
        })

    df = pd.DataFrame(lista).dropna()
    try:
        X = df[["idade", "etnia", "localizacao"]]
        # Placeholder para análise futura
        return jsonify({"message": "Endpoint pronto para implementar análise"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao processar modelo: {str(e)}"}), 500

@app.route('/api/predizer', methods=['POST'])
def predizer():
    dados = request.get_json()
    if not dados or not all(k in dados for k in ("idade", "etnia", "localizacao")):
        return jsonify({"erro": "JSON inválido. Esperado: idade, etnia, localizacao"}), 400

    try:
        df = pd.DataFrame([dados])
        y_prob = modelo.predict_proba(df)[0]
        y_pred_encoded = modelo.predict(df)[0]
        y_pred = label_encoder.inverse_transform([y_pred_encoded])[0]
        classes = label_encoder.classes_

        resultado = {
            "classe_predita": y_pred,
            "probabilidades": {classe: round(prob, 4) for classe, prob in zip(classes, y_prob)}
        }
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao fazer predição: {str(e)}"}), 500

# Atualizando app.py
@app.route('/api/modelo/coficientes', methods=['GET'])
def coeficientes_modelo():
    try:
        # Pegando o pré-processador e o classificador XGBoost do pipeline
        preprocessor = modelo.named_steps['preprocessor']
        classifier = modelo.named_steps['classifier']

        # Pegando nomes das features após o OneHotEncoding
        cat_encoder = preprocessor.named_transformers_['cat']
        cat_features = cat_encoder.get_feature_names_out(preprocessor.transformers_[0][2])
        numeric_features = preprocessor.transformers_[1][2]
        all_features = list(cat_features) + list(numeric_features)

        # Pegando as importâncias de feature do XGBoost
        importancias = classifier.feature_importances_

        features_importances = {
            feature: float(importance)
            for feature, importance in zip(all_features, importancias)
        }

        return jsonify(features_importances), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    if colecao.count_documents({}) == 0:
        print("Inserindo dados aleatórios no MongoDB...")
        dados_iniciais = gerar_dados_aleatorio(100)
        colecao.insert_many(dados_iniciais)
    app.run(debug=True)
