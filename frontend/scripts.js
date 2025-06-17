let dadosCasos = [];
let graficoRosca = null;
let graficoDistribuicao = null;

const gradiente = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
];

function contarOcorrencias (dados, chave) {
    const contagem = {};
    dados.forEach(item => {
        try {
            const valor = chave.includes('.') 
            ? chave.split('.').reduce((o, k) => o && o[k], caso)
            : caso[chave];
        if (valor !== undefined && valor !== null) {
            contagem[valor] = (contagem[valor] || 0) + 1;
        }
        } catch {}

    });
    return contagem;
}

async function carregarDados() {
    try {
        const res = await fetch('https://localhost: 5000/api/casos');
        dadosCasos = await res.json();
        console.log("Dados carregados:", dadosCasos);
        atualizarGraficos();
        } catch (error) {
        console.error("Erro ao carregar os dados:", error);
        alert("Erro ao carregar os dados. Verifique o console para mais detalhes.");
    }
}

function filtrarPorData(casos) {
    const fim = document.getElementById('dataFim').value;
    
    return casos.filter(caso => {
        if (!caso.data_do_caso) return false;
        const data = new Date(caso.data_do_caso);
        const dataInicio = inicio ? new Date(inicio) : null;
        const dataFim = fim ? new Date(fim) : null;
        return (!dataInicio || data >= dataInicio) && (!dataFim || data <= dataFim);
    }
    );
}

function atualizarGraficoRosca(dadosFiltrados) {
  const contagem = contarOcorrencias(dadosFiltrados, "tipo_do_caso");
  const labels = Object.keys(contagem);
  const valores = Object.values(contagem);
  const cores = gradiente.slice(0, labels.length);

  const ctx = document.createElement('canvas');
  document.getElementById("graficoRosca").innerHTML = '';
  document.getElementById("graficoRosca").appendChild(ctx);

  if (graficoRosca) graficoRosca.destroy();

  graficoRosca = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: valores,
        backgroundColor: cores,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

function atualizarGraficoDistribuicao(dadosFiltrados) {
  const idades = dadosFiltrados
    .map(c => c.vitima?.idade)
    .filter(i => typeof i === 'number' && !isNaN(i) && i > 0);

  const max = Math.max(...idades, 100);
  const bins = [];
  const labels = [];

  for (let i = 1; i <= max; i += 10) {
    labels.push(`${i}-${i + 9}`);
    bins.push(0);
  }

  idades.forEach(idade => {
    const index = Math.floor((idade - 1) / 10);
    if (index >= 0 && index < bins.length) bins[index]++;
  });

  const ctx = document.createElement('canvas');
  document.getElementById("graficoDistribuicao").innerHTML = '';
  document.getElementById("graficoDistribuicao").appendChild(ctx);

}

document.getElementById("graficoDistribuicao").appendChild(ctx);
if (graficoDistribuicao) graficoDistribuicao.destroy();

    graficoDistribuicao = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Número de Vítimas',
        data: bins,
        backgroundColor: '#5d759c',
        borderWidth: 0
      }]
    },
    options: {
        responsive: true,
        scales: {
            y: {beginAtZero: true}
        },
    }
});

function atualizarGraficos() {
    const dadosFiltrados = filtrarPorData(dadosCasos);
    console.log("Dados filtrados:", dadosFiltrados);
    if (dadosFiltrados.length === 0) {
        alert("Nenhum caso encontrado para o período selecionado.");
        return;
    }
    atualizarGraficoRosca(dadosFiltrados);
    atualizarGraficoDistribuicao(dadosFiltrados);
}

document.getElementById('dataFim').addEventListener('change', atualizarGraficos);
document.getElementById('dataInicio').addEventListener('change', atualizarGraficos);

carregarDados();