from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dataclasses import dataclass, asdict
import random
from datetime import datetime, timedelta
from flask import request, abort

app = Flask(__name__)
CORS(app)

# Configuração do MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['odontolegal']
colecao = db['dados']

@dataclass
class Vitima:
    etnia: str
    idade: int

@dataclass
class Caso:
    data_do_caso: str
    tipo_de_caso: str
    localizacao: str
    Vitima: Vitima

    def to_dict(self):
        return {
            "data_do_caso": self.data_do_caso,
            "tipo_de_caso": self.tipo_de_caso,
            "localizacao": self.localizacao,
            "Vitima": asdict(self.Vitima)
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


if __name__ == '__main__':
    if colecao.count_documents({}) == 0:
        print("Inserindo dados aleatórios no MongoDB...")
        dados_iniciais = gerar_dados_aleatorio(100)
        colecao.insert_many(dados_iniciais)
    app.run(debug=True)